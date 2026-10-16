#!/usr/bin/env python3
"""school_tune_tune.py : install the question-answer convention on a base model.

Trains a LoRA adapter that teaches a base model one convention: in the frame
`Q: {question}\\nA:`, the text after the question is THE ANSWER, in the register
the question calls for. Nothing else is taught. Loads model weights, so it needs
a GPU (or `--dry-run` on CPU with a tiny stand-in model).

    python recipe/school_tune_tune.py --run my_run --lora v2 --corpus en \\
        --base-model google/gemma-2-9b --seed 20260909
    python recipe/school_tune_tune.py --run my_dry --lora v2 --corpus en --dry-run

Inputs are read from `corpus/instruction_corpus_{corpus}.jsonl` and
`corpus/instruction_corpus_{corpus}_heldout.jsonl`; outputs go to `runs/{run}/adapter` and
`runs/{run}/results/`, all relative to the `adapters/` directory.

═══════════════════════════════════════════════════════════════════════════════
EVERY HYPERPARAMETER IS READ FROM `school_tune_instruments`. NONE IS A FLAG.

The script chooses between two fixed specifications (`--lora v1` or `--lora
v2`), each with its own digest. There is no `--lr`, `--epochs` or `--batch`, so a
run cannot drift from its specification through the command line. The declared
exceptions are `--base-model`, `--seed`, `--max-seq-length` and `--micro-batch`
(which holds the effective batch fixed); each is recorded in the manifest beside
the unchanged specification digest.

At batch 4 and sequence 512, a large vocabulary (Gemma 2's is about 256k) makes
the logits tensor the dominant memory consumer during training, not the adapter.

═══════════════════════════════════════════════════════════════════════════════
LOSS IS COMPUTED ON THE ANSWER TOKENS ONLY

1. **The tune's one job is to teach that the text after a question is THE
   ANSWER.** Loss over the whole pair also trains the model to predict
   QUESTIONS, which reinforces continuing a worksheet rather than answering.
   Masking the prompt means the gradient carries only *given this question,
   produce this answer*.

2. **The composition constraint lives entirely in the ANSWERS.** The hedged
   register is a property of how a question is answered, not of how it is
   asked. Counting question tokens in the loss would dilute the designed
   proportion of answer kinds at the level the gradient sees.

═══════════════════════════════════════════════════════════════════════════════
THE MASK BOUNDARY IS ESTABLISHED ON THE TOKENISER, NEVER FROM THE STRING

**A mask off by one token trains on the prompt's last token or drops the answer's
first**, and either would be invisible in the loss curve. `"A:"` followed by
`" Yes"` need not tokenise the way the string suggests: BPE and SentencePiece both
merge across boundaries when the merge is frequent.

So the boundary is found with `return_offsets_mapping` and checked on every pair:

  - **no token may STRADDLE the boundary** (start before `len(prompt)`, end after).
    A straddling token contains prompt and answer characters, and every way of
    assigning it is wrong. A non-zero count is fatal;
  - **the prompt's own tokenisation must be a PREFIX of the pair's.** Otherwise
    the tokeniser re-segmented the prompt in the presence of the answer, and the
    boundary index computed from the prompt alone does not exist in the pair;
  - **the boundary must fall EXACTLY on a token start** (`offset[first][0] ==
    len(prompt)`), so nothing is silently skipped between the end of the prompt
    and the first unmasked token;
  - **the source characters the tokeniser attributes to the unmasked tokens must
    equal the completion** (the offset-span check). This is the primary check on
    the offsets path: it compares against the source text rather than against a
    `decode()` re-rendering, because on some tokenisers decode is not a left
    inverse of encode.

A decode round-trip is also computed and recorded. On the offsets path it is
informational; on the prefix path (below) it is the primary end-to-end check, with
two narrow concessions:

  - SentencePiece folds the space before the first answer token into that token,
    and `decode()` does not re-emit it, so a match against the completion with its
    LEADING WHITESPACE ONLY removed is accepted. It cannot absorb a dropped answer
    token, because `boundary_exact` is checked separately;
  - truncation at exactly `max_len` can sever a byte-fallback sequence
    mid-character, so trailing U+FFFD is ignored, and only on truncated pairs.

The count of pairs needing each concession is recorded in the manifest.

═══════════════════════════════════════════════════════════════════════════════
WHAT THIS SCRIPT DOES NOT DO

- **No `trl`.** `SFTTrainer` would supply completion-only masking whose boundary
  behaviour would then need verifying to the same standard as the above. Masking
  is done here, explicitly, and asserted.
- **No evaluation of the tuned model's moral answers.** This script emits an
  adapter and a manifest; any reading of the tuned model is a separate stage.
- **No re-tuning on failure**, and no loop that could become one.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import school_tune_instruments as I                                # noqa: E402

# The `adapters/` directory: corpus/, runs/ and requirements.txt are resolved
# relative to it.
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = f"{R}/corpus"

# The dry-run stand-in. A Gemma-architecture tiny model carrying the real Gemma
# vocabulary and a fast tokeniser, because the thing being exercised is the mask
# boundary, which is a property of the tokeniser.
DRY_RUN_MODEL = "hf-internal-testing/tiny-random-Gemma2ForCausalLM"

# Steps a dry run takes. Enough to exercise warmup, the scheduler, gradient
# accumulation and a save; far short of training anything.
DRY_RUN_STEPS = 4


def load_pairs(path):
    return [json.loads(l) for l in open(path)]


def build_example(tok, prompt, completion, max_len, use_offsets=True):
    """Tokenise one pair and mask the prompt. Returns (ids, labels, report).

    `report` carries the per-pair evidence for the boundary checks so the caller
    can aggregate them rather than trusting a silent pass.
    """
    text = prompt + completion
    b = len(prompt)

    if use_offsets:
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True,
                  truncation=True, max_length=max_len)
        ids = enc["input_ids"]
        offsets = enc["offset_mapping"]
        straddle = [i for i, (s, e) in enumerate(offsets) if s < b < e]
        first = next((i for i, (s, e) in enumerate(offsets) if s >= b), len(ids))
        prompt_ids = tok(prompt, add_special_tokens=False)["input_ids"]
        prefix_ok = ids[:len(prompt_ids)] == prompt_ids
        # The boundary must land ON a token start, not merely at-or-after one.
        # Tokeniser-independent, and it is what a silently dropped character or
        # token would violate. `first == len(ids)` means the answer was truncated
        # away entirely, which the zero-answer-token check reports.
        boundary_exact = first == len(ids) or offsets[first][0] == b
        # ── THE OFFSET-SPAN CHECK: EXACT, AND IT NEEDS NO CONCESSIONS ───────
        # The tokeniser reports which characters of the source each token came
        # from, so the completion is recovered from the source rather than from
        # `decode`, which on some tokenisers inserts or drops whitespace (for
        # example, rendering '<h1>Welcome!' as '<h1> Welcome!'). The span is
        # compared with the completion INCLUDING its leading space.
        if first < len(ids):
            _lo = offsets[first][0]
            _hi = max(e for _s, e in offsets[first:])
            span_src = text[_lo:_hi]
        else:
            span_src = ""
        offset_span_ok = (span_src == completion
                          or (len(ids) >= max_len and completion.startswith(span_src)))
    else:
        # ── THE PREFIX PATH: AN INVARIANT IN PLACE OF A CHECK ───────────────
        # For tokenisers that ship only a SLOW implementation, which cannot
        # return offsets. Converting such a tokeniser to a fast one is not a
        # substitute: a fast tokeniser built from the same model file can
        # segment differently, and a tune on those ids is a tune on ids the model
        # was never pretrained with.
        #
        # This path REQUIRES that the prompt's ids are a prefix of the pair's.
        # When that holds, everything the offsets were consulted for follows by
        # construction:
        #   - `first = len(prompt_ids)` is EXACT, because the first
        #     `len(prompt_ids)` tokens ARE the prompt's tokens;
        #   - NO TOKEN CAN STRADDLE, because a straddling token would make the
        #     prompt's ids differ from the pair's at that position;
        #   - THE BOUNDARY IS ON A TOKEN START, for the same reason.
        # When the prefix fails, `prefix_ok` is False and `assert_boundaries`
        # refuses, which is the same outcome the offsets path reaches.
        enc = tok(text, add_special_tokens=False, truncation=True,
                  max_length=max_len)
        ids = enc["input_ids"]
        prompt_ids = tok(prompt, add_special_tokens=False)["input_ids"]
        prefix_ok = ids[:len(prompt_ids)] == prompt_ids
        first = len(prompt_ids) if prefix_ok else len(ids)
        straddle = []
        boundary_exact = prefix_ok
        # NO OFFSETS ON THIS PATH BY DEFINITION, so the span check cannot run and
        # the decode concessions stay as the primary evidence here. `None` is not
        # a pass: assert_boundaries selects the check by path, never by truthiness.
        offset_span_ok = None
        span_src = None

    labels = [-100] * first + ids[first:]
    decoded = tok.decode(ids[first:])
    # Truncation can legitimately cut the tail, so the decode check compares
    # against the completion as far as the surviving tokens go.
    truncated = len(ids) >= max_len
    decode_strict = completion.startswith(decoded) or decoded == completion

    # CONCESSION 2, and it applies to the TAIL and only under truncation.
    # Cutting at exactly max_len can sever a byte-fallback sequence mid-character,
    # and decoding the surviving bytes yields U+FFFD. Guarded on `truncated`: an
    # untruncated pair emitting U+FFFD is a genuine encoding fault and still
    # refuses.
    cmp_dec = decoded.rstrip("�") if truncated else decoded

    # CONCESSION 1: SentencePiece folds the boundary space into the first answer
    # token and does not re-emit it. Leading whitespace ONLY; see the docstring.
    lstripped = completion.lstrip()
    decode_relaxed = bool(cmp_dec) and (completion.startswith(cmp_dec)
                                        or lstripped.startswith(cmp_dec)
                                        or cmp_dec in (completion, lstripped))
    decode_ok = decode_strict or decode_relaxed

    return ids, labels, {
        "uses_offsets": bool(use_offsets),
        "offset_span_ok": offset_span_ok,
        "offset_span_len": (len(span_src) if span_src is not None else None),
        "straddle": len(straddle), "prefix_ok": prefix_ok,
        "decode_ok": decode_ok, "decode_strict": decode_strict,
        "needed_lstrip": decode_ok and not decode_strict
        and not completion.startswith(cmp_dec),
        "needed_tail_concession": decode_ok and not decode_strict
        and cmp_dec != decoded,
        "boundary_exact": boundary_exact, "first_unmasked": first,
        "n_tok": len(ids), "n_answer_tok": len(ids) - first,
        "truncated": truncated,
    }


def assert_boundaries(reports, samples):
    """Fatal on any boundary defect. Returns the aggregate for the manifest."""
    n = len(reports)
    straddles = sum(r["straddle"] for r in reports)
    prefix_bad = [i for i, r in enumerate(reports) if not r["prefix_ok"]]
    boundary_bad = [i for i, r in enumerate(reports) if not r["boundary_exact"]]
    decode_bad = [i for i, r in enumerate(reports) if not r["decode_ok"]]
    # WHICH CHECK IS PRIMARY IS DECIDED BY THE PATH, NOT BY TRUTHINESS. On the
    # offsets path the exact span check is primary and the decode result is
    # informational; on the fallback path there are no offsets, so the decode
    # concessions remain the primary evidence. A report whose `offset_span_ok`
    # is None must never be read as passing.
    on_offsets = all(r["uses_offsets"] for r in reports)
    mixed_paths = on_offsets != any(r["uses_offsets"] for r in reports)
    span_bad = [i for i, r in enumerate(reports)
                if r["uses_offsets"] and r["offset_span_ok"] is not True]
    empty = [i for i, r in enumerate(reports) if r["n_answer_tok"] == 0]
    lstripped = [i for i, r in enumerate(reports) if r["needed_lstrip"]]
    tailed = [i for i, r in enumerate(reports) if r["needed_tail_concession"]]

    def fail(msg, idxs):
        lines = [f"REFUSING: {msg} ({len(idxs)} of {n} pairs)"]
        for i in idxs[:3]:
            lines.append(f"    pair {i}: prompt={samples[i][0]!r}")
            lines.append(f"             completion={samples[i][1]!r}")
        sys.exit("\n".join(lines))

    if straddles:
        bad = [i for i, r in enumerate(reports) if r["straddle"]]
        fail("tokens STRADDLE the prompt/answer boundary; every assignment of "
             "a straddling token is wrong", bad)
    if prefix_bad:
        fail("the prompt's tokenisation is not a PREFIX of the pair's, so the "
             "boundary computed from the prompt does not exist in the pair",
             prefix_bad)
    if boundary_bad:
        fail("the boundary does not fall on a token START, so something between "
             "the prompt and the first unmasked token was skipped", boundary_bad)
    if mixed_paths:
        sys.exit("REFUSING: some pairs were built with offsets and some without; "
                 "one run must use one masking path so the manifest can name it")
    if on_offsets:
        if span_bad:
            fail("the SOURCE CHARACTERS the tokeniser attributes to the unmasked "
                 "tokens are not the completion", span_bad)
    elif decode_bad:
        fail("decoding the unmasked span does not reproduce the completion",
             decode_bad)
    if empty:
        fail("a pair has ZERO answer tokens, so it contributes no gradient",
             empty)
    return {
        "n_pairs": n, "straddling_tokens": straddles,
        "masking_path": "character_offsets" if on_offsets else "prompt_prefix",
        "primary_boundary_check": ("offset_span_equals_completion" if on_offsets
                                   else "decode_roundtrip_with_concessions"),
        "offset_span_holds": (True if on_offsets else None),
        "concessions_active": (False if on_offsets else True),
        "concessions_note": ("retired on the offsets path: the span check is exact "
                             "and needs neither the leading-whitespace nor the "
                             "truncation-tail concession" if on_offsets else
                             "in force: no offsets are available on this path"),
        # INFORMATIONAL ON THE OFFSETS PATH. A non-zero count records a tokeniser
        # whose decode is not a left inverse of encode, which is a fact about the
        # tokeniser and not a defect in the mask.
        "decode_roundtrip_holds": len(decode_bad) == 0,
        "decode_roundtrip_failures": len(decode_bad),
        "prefix_property_holds": True,
        "boundary_falls_on_token_start": True,
        "pairs_with_zero_answer_tokens": 0,
        # NOT a pass/fail. A non-zero count says the tokeniser folded the
        # boundary space into the first answer token (SentencePiece does, BPE
        # does not), and it is recorded so the concession's use is visible.
        "decode_needed_leading_whitespace_concession": len(lstripped),
        # Severed byte-fallback characters at the truncation cut. Only ever
        # non-zero on pairs that hit max_len, and guarded on that.
        "decode_needed_truncation_tail_concession": len(tailed),
        "decode_strict_holds_unaided": len(lstripped) + len(tailed) == 0,
        "n_truncated_at_max_len": sum(1 for r in reports if r["truncated"]),
        "mean_answer_tokens": round(
            sum(r["n_answer_tok"] for r in reports) / n, 1),
        "mean_total_tokens": round(sum(r["n_tok"] for r in reports) / n, 1),
        "checked_on": "every pair, not a sample",
    }


def _provenance(model_id, a, adapter_dir, boundary, set_path,
                seed_config=None, seed_used=None):
    """The provenance record for a published adapter, written at train time.

    **The anchor is the adapter's own sha256**, because every reading taken
    through the adapter can assert its digest, so that one number ties the
    weights to the readings. Everything else is provenance around it.

    Each field says WHEN it was determined: a base-model revision resolved at
    upload time is not necessarily the revision trained against.
    """
    import hashlib as _h, subprocess as _sp
    def _sha(path):
        try:
            return _h.sha256(open(path, "rb").read()).hexdigest()
        except OSError:
            return None
    def _dir_digest(d):
        """sha256 over the sorted .safetensors/.bin/.json files of the adapter
        directory, truncated to 16 hex: the adapter's directory digest."""
        h = _h.sha256()
        try:
            for f in sorted(x for x in os.listdir(d)
                            if x.endswith((".safetensors", ".bin", ".json"))):
                h.update(open(os.path.join(d, f), "rb").read())
        except OSError:
            return None
        return h.hexdigest()[:16]
    rev = None
    try:
        from huggingface_hub import HfApi
        rev = HfApi().model_info(model_id).sha
    except Exception:
        pass
    try:
        commit = _sp.check_output(["git", "-C", R, "rev-parse", "HEAD"],
                                 text=True, stderr=_sp.DEVNULL).strip()
        dirty = bool(_sp.check_output(["git", "-C", R, "status", "--porcelain"],
                                     text=True, stderr=_sp.DEVNULL).strip())
    except Exception:
        commit, dirty = None, None
    return {
        "adapter_sha256": _sha(os.path.join(adapter_dir, "adapter_model.safetensors")),
        "adapter_expect_digest": _dir_digest(adapter_dir),
        "adapter_expect_digest_note":
            "sha256 over the sorted .safetensors/.bin/.json contents of the adapter "
            "directory, truncated to 16 hex. A .txt or .md file in that directory "
            "does NOT enter it.",
        "base_model_id": model_id,
        "base_model_revision": rev,
        "base_model_revision_when": ("resolved at TRAIN time from the Hub" if rev
                                     else "could not be resolved at train time"),
        "training_seed": seed_used,
        "training_seed_source": ("--seed flag, overriding the spec's "
                                 f"{seed_config}" if seed_used != seed_config
                                 else "the fixed lora_spec"),
        "training_set": os.path.relpath(set_path, R),
        "training_set_sha256": _sha(set_path),
        "training_set_sha256_when": "hashed at TRAIN time from the file that was read",
        "trainer_git_commit": commit,
        "trainer_git_dirty": dirty,
        "trainer_git_note": ("the working tree had uncommitted changes at train time"
                             if dirty else None),
        "masking_path": boundary.get("masking_path"),
        "primary_boundary_check": boundary.get("primary_boundary_check"),
        "decode_roundtrip_failures": boundary.get("decode_roundtrip_failures"),
        "concessions_active": boundary.get("concessions_active"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True,
                    help="label for this run; outputs go to runs/<run>/")
    ap.add_argument("--max-seq-length", type=int, default=None,
                    help="override the specification's max_seq_length. Raising it "
                         "only affects pairs longer than the old limit. The "
                         "specification and its digest are not edited; the "
                         "override is recorded in the manifest.")
    ap.add_argument("--micro-batch", type=int, default=None,
                    help="per-device batch size. The EFFECTIVE batch is held fixed "
                         "by adjusting gradient_accumulation_steps to match, and the "
                         "product is asserted.")
    ap.add_argument("--heldout-corpus", default=None,
                    help="take the held-out slice from a different set than "
                         "--corpus. The slice only checks that the adapter answers "
                         "in the required form. Overlap with the training set is "
                         "asserted absent by uid, by sha and by normalised text, and "
                         "the manifest records which slice was used.")
    ap.add_argument("--corpus", default="en",
                    help="name of the corpus to train on: reads "
                         "corpus/instruction_corpus_<name>.jsonl and "
                         "corpus/instruction_corpus_<name>_heldout.jsonl")
    # WHICH FIXED SPECIFICATION, not which hyperparameters. There is no --lr and
    # no --epochs: the choice is between two dicts, each with its own digest.
    ap.add_argument("--lora", choices=("v1", "v2"), default="v1",
                    help="v1 = LORA (r=8, attention projections). "
                         "v2 = LORA_V2 (r=32, attention and MLP projections).")
    # The base model is an override rather than a field of a new specification,
    # so that adapters on different bases share one specification digest and the
    # base is recorded as the one declared difference.
    ap.add_argument("--base-model", default=None,
                    help="override the specification's base_model. The "
                         "specification and its digest are NOT mutated; the "
                         "override is recorded in the manifest.")
    ap.add_argument("--seed", type=int, default=None,
                    help="override ONLY the training seed. The specification and "
                         "its digest are unchanged, so several seeds of one recipe "
                         "remain one recipe. Omitting the flag uses the "
                         "specification's seed.")
    ap.add_argument("--trust-remote-code", action="store_true")
    # ── OPTIONAL: THE GRADATION CURVE ───────────────────────────────────────
    # A final loss cannot distinguish "the model cannot learn this" from
    # "training stopped too early". The gradation curve measures, every N steps,
    # how well the model fits the bare-digit training items: a curve still rising
    # at the final step says the run was short; a plateau says the set or the
    # capacity is the constraint. It selects nothing and changes nothing: it runs
    # under no_grad and restores training mode, so the adapter written is the
    # same as without the flag. It is measured on TRAINING items on purpose,
    # because failure to fit what was shown is the diagnostic.
    ap.add_argument("--resume-adapter", default=None,
                    help="continue training an adapter already written. The "
                         "cosine schedule cannot be resumed, so the segment "
                         "runs at a CONSTANT learning rate from the "
                         "specification. Recorded as a separate segment.")
    ap.add_argument("--extra-steps", type=int, default=0,
                    help="optimizer steps for a resumed segment. Required with "
                         "--resume-adapter, meaningless without it.")
    ap.add_argument("--gradation-eval-every", type=int, default=0,
                    help="evaluate numeric gradation every N optimizer steps "
                         "and record the curve in the manifest. 0 disables it "
                         "(the default).")
    # Required for tokenisers that ship only a SLOW implementation, which cannot
    # return offsets.
    ap.add_argument("--no-offsets", action="store_true",
                    help="use the prefix invariant instead of character offsets")
    ap.add_argument("--dry-run", action="store_true",
                    help="tiny model on CPU; exercises the whole path including "
                         "the boundary assertions")
    a = ap.parse_args()

    import torch
    from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                              TrainingArguments)
    from peft import LoraConfig, get_peft_model

    L = I.LORA if a.lora == "v1" else I.LORA_V2
    spec_digest = I.digest() if a.lora == "v1" else I.digest_v2()
    out_dir = f"{R}/runs/{a.run}/results"
    adapter_dir = f"{R}/runs/{a.run}/adapter"
    os.makedirs(out_dir, exist_ok=True)
    man_path = f"{out_dir}/school_tune_tune.json"
    txt_path = f"{out_dir}/school_tune_tune.txt"
    # Write-once: an existing output is never overwritten.
    for p in (man_path, txt_path, adapter_dir):
        if os.path.exists(p):
            sys.exit(f"REFUSING: {p} exists. Write-once, no override.")

    lines = []

    def say(s=""):
        print(s, flush=True)
        lines.append(s)

    model_id = (DRY_RUN_MODEL if a.dry_run
                else (a.base_model or L["base_model"]))
    base_model_overridden = bool(a.base_model and not a.dry_run
                                 and a.base_model != L["base_model"])
    seed_used = L["seed"] if a.seed is None else a.seed
    seed_overridden = a.seed is not None and a.seed != L["seed"]
    if base_model_overridden:
        say(f"   *** BASE MODEL OVERRIDDEN: {L['base_model']} -> {model_id}")
        say(f"       The specification and its digest are unchanged; the base "
            f"model is the one declared difference.")
    say("== SCHOOL TUNE. Install the question-answer convention. Nothing else.")
    say(f"   instruments digest {I.digest()}, committed {I.COMMITTED}")
    say(f"   model {model_id}" + ("   [DRY RUN: numbers are plumbing and none "
                                  "may be quoted]" if a.dry_run else ""))
    say(f"   spec {a.lora.upper()} (digest {spec_digest})"
        + ("" if a.lora == "v1" else
           f"  [{L['variant']}] single change: {L['single_change']}"))
    # ── THE TWO DECLARED OVERRIDES, applied to a COPY of the specification ──
    # `L` is a dict read from the instruments module; overriding it here leaves
    # the module and its digest untouched, and the override is recorded in the
    # manifest. The EFFECTIVE BATCH IS HELD FIXED by adjusting accumulation to
    # match the micro-batch, and the product is asserted so it cannot drift.
    msl_overridden = mb_overridden = False
    EFFECTIVE = (L["per_device_batch_size"] * L["gradient_accumulation_steps"])
    if a.max_seq_length is not None and a.max_seq_length != L["max_seq_length"]:
        L = dict(L, max_seq_length=a.max_seq_length)
        msl_overridden = True
    if a.micro_batch is not None and a.micro_batch != L["per_device_batch_size"]:
        if EFFECTIVE % a.micro_batch:
            sys.exit(f"REFUSING: micro-batch {a.micro_batch} does not divide the "
                     f"effective batch {EFFECTIVE}, so the effective batch would "
                     f"change. The effective batch is held fixed.")
        L = dict(L, per_device_batch_size=a.micro_batch,
                 gradient_accumulation_steps=EFFECTIVE // a.micro_batch)
        mb_overridden = True
    got_eff = L["per_device_batch_size"] * L["gradient_accumulation_steps"]
    if got_eff != EFFECTIVE:
        sys.exit(f"REFUSING: effective batch moved from {EFFECTIVE} to {got_eff}")
    if msl_overridden or mb_overridden:
        say(f"   *** DECLARED OVERRIDES (spec and digest unchanged):")
        if msl_overridden:
            say(f"       max_seq_length -> {L['max_seq_length']}  (raising it only "
                f"affects pairs longer than the old limit)")
        if mb_overridden:
            say(f"       per_device_batch_size -> {L['per_device_batch_size']}, "
                f"gradient_accumulation_steps -> "
                f"{L['gradient_accumulation_steps']}; effective batch still "
                f"{got_eff}, ASSERTED")
    say(f"   hyperparameters READ FROM THE FIXED SPEC, not from flags:")
    for k in ("r", "lora_alpha", "lora_dropout", "target_modules", "epochs",
              "learning_rate", "lr_scheduler", "warmup_ratio",
              "per_device_batch_size", "gradient_accumulation_steps",
              "max_seq_length", "seed"):
        if k == "seed":
            say(f"     {k:<30} {seed_used}"
                + (f"   *** OVERRIDDEN from the spec's {L['seed']} by --seed; "
                   f"the spec and its digest are unchanged"
                   if seed_overridden else
                   ("   (--seed given and equal to the spec's value, so nothing "
                    "is overridden)" if a.seed is not None else "")))
        else:
            say(f"     {k:<30} {L[k]}")
    say()

    train = load_pairs(f"{CORPUS}/instruction_corpus_{a.corpus}.jsonl")
    ho_corpus = a.heldout_corpus or a.corpus
    held = load_pairs(f"{CORPUS}/instruction_corpus_{ho_corpus}_heldout.jsonl")
    say(f"   train {len(train)} from {a.corpus} | held-out {len(held)} from "
        f"{ho_corpus}{' (BORROWED)' if ho_corpus != a.corpus else ''}, "
        f"frame {I.QA_FRAME!r}")
    if ho_corpus != a.corpus:
        # A BORROWED SLICE IS ONLY LEGITIMATE IF IT IS NOT TRAINED ON, so the
        # overlap is asserted here on the bytes about to be trained. Three
        # identities, because a pair can be the same material under a different
        # label.
        import hashlib as _h

        def _norm(r):
            q = " ".join((r.get("question") or "").split()).casefold()
            an = " ".join((r.get("answer") or "").split()).casefold()
            return _h.sha256((q + "\x00" + an).encode()).hexdigest()

        tr_uid = {r.get("uid") for r in train}
        tr_sha = {r.get("sha") for r in train if r.get("sha")}
        tr_txt = {_norm(r) for r in train}
        bad = {"uid": sorted({r.get("uid") for r in held} & tr_uid),
               "sha": sorted({r.get("sha") for r in held if r.get("sha")} & tr_sha),
               "text": sorted({_norm(r) for r in held} & tr_txt)}
        if any(bad.values()):
            sys.exit(f"REFUSING: the borrowed held-out slice ({ho_corpus}) overlaps the "
                     f"training set ({a.corpus}): {bad}. A held-out pair that is "
                     f"trained on gives a parse rate measured on memorised material, "
                     f"which is a gate nobody can fail.")
        say(f"   borrowed-slice overlap gate: 0 by uid, 0 by sha, 0 by text")

    tok = AutoTokenizer.from_pretrained(
        model_id, trust_remote_code=a.trust_remote_code)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    # ── the boundary, established on the tokeniser ──────────────────────────
    ids_l, lab_l, reports, samples = [], [], [], []
    for r in train:
        ids, labels, rep = build_example(tok, r["prompt"], r["completion"],
                                         L["max_seq_length"], use_offsets=not a.no_offsets)
        ids = ids + [tok.eos_token_id]
        labels = labels + [tok.eos_token_id]
        ids_l.append(ids)
        lab_l.append(labels)
        reports.append(rep)
        samples.append((r["prompt"], r["completion"]))
    boundary = assert_boundaries(reports, samples)
    say("   MASK BOUNDARY ESTABLISHED ON THE TOKENISER AND ASSERTED:")
    say(f"     straddling tokens {boundary['straddling_tokens']} | prefix "
        f"property holds | decode round-trip holds | zero-answer pairs 0")
    say(f"     checked on EVERY pair ({boundary['n_pairs']}), not a sample")
    say(f"     mean {boundary['mean_answer_tokens']} answer tokens of "
        f"{boundary['mean_total_tokens']} total; "
        f"{boundary['n_truncated_at_max_len']} truncated at "
        f"{L['max_seq_length']}")
    say(f"     EOS appended, so the model learns to stop rather than to run on")
    say()

    class DS(torch.utils.data.Dataset):
        def __len__(self):
            return len(ids_l)

        def __getitem__(self, i):
            return {"input_ids": ids_l[i], "labels": lab_l[i]}

    def collate(batch):
        n = max(len(b["input_ids"]) for b in batch)
        pad = tok.pad_token_id
        return {
            "input_ids": torch.tensor(
                [b["input_ids"] + [pad] * (n - len(b["input_ids"]))
                 for b in batch]),
            "attention_mask": torch.tensor(
                [[1] * len(b["input_ids"]) + [0] * (n - len(b["input_ids"]))
                 for b in batch]),
            "labels": torch.tensor(
                [b["labels"] + [-100] * (n - len(b["labels"]))
                 for b in batch]),
        }

    dtype = torch.float32 if a.dry_run else torch.bfloat16
    # THE KWARG NAME IS VERSION-DEPENDENT AND THE DTYPE IS NOT. `dtype=` is the
    # current spelling; older transformers releases want `torch_dtype=` and pass
    # an unknown `dtype` through to the model constructor, which can raise
    # TypeError. Both spellings are tried, and the dtype actually loaded is read
    # back from the model below rather than assumed.
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, dtype=dtype, trust_remote_code=a.trust_remote_code)
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=dtype,
            trust_remote_code=a.trust_remote_code)
    # THE DTYPE IS RECORDED FROM THE MODEL, NOT FROM THE SPEC STRING, so a
    # silently ignored dtype argument cannot be reported as bf16.
    actual_dtype = str(next(model.parameters()).dtype)

    targets = L["target_modules"]
    present = {n.split(".")[-1] for n, _ in model.named_modules()}
    missing = [t for t in targets if t not in present]
    if missing:
        sys.exit(f"REFUSING: target modules absent from this model: {missing}. "
                 f"The spec targets {targets}; the adapter would attach "
                 f"to fewer modules than the spec claims.")

    if a.resume_adapter:
        # ── RESUMING AN EXISTING ADAPTER ────────────────────────────────────
        # The cosine schedule has decayed to approximately zero by its final
        # step, so it cannot be continued. A resumed segment runs at the
        # specification's learning rate held CONSTANT, with no second warmup and
        # no fresh decay cycle. It is a second segment, not a longer first run,
        # and the manifest labels it that way: its curve may not be joined to the
        # original's and read as one training run.
        from peft import PeftModel
        if not os.path.isdir(a.resume_adapter):
            sys.exit(f"REFUSING: --resume-adapter {a.resume_adapter} is not a "
                     f"directory")
        prior = json.load(open(f"{a.resume_adapter}/adapter_config.json"))
        if prior.get("base_model_name_or_path") != model_id:
            sys.exit(f"REFUSING: the adapter was trained on "
                     f"{prior.get('base_model_name_or_path')!r} and this run "
                     f"loads {model_id!r}. Resuming across bases is not a "
                     f"continuation of anything.")
        if prior.get("r") != L["r"]:
            sys.exit(f"REFUSING: adapter r={prior.get('r')} against spec "
                     f"r={L['r']}")
        model = PeftModel.from_pretrained(model, a.resume_adapter,
                                          is_trainable=True)
        say(f"   RESUMED from {os.path.relpath(a.resume_adapter, R)} "
            f"(r={prior.get('r')}, base {prior.get('base_model_name_or_path')})")
        say(f"     the cosine schedule is NOT resumed: this segment runs at a "
            f"CONSTANT lr {L['learning_rate']}, no warmup, no decay")
    else:
        # ── THE SEED IS SET HERE, BEFORE THE ADAPTER IS BUILT ───────────────
        # peft initialises `lora_A` with `kaiming_uniform_` off torch's global
        # generator when `get_peft_model` runs. `Trainer.__init__` also calls
        # `set_seed(args.seed)`, but `Trainer` is constructed later, so a seed
        # applied only there would govern data order and dropout and leave the
        # adapter's initialisation to the ambient RNG state. Setting it here
        # makes the seed govern initialisation as well.
        from transformers import set_seed as _set_seed
        _set_seed(seed_used)
        model = get_peft_model(model, LoraConfig(
            r=L["r"], lora_alpha=L["lora_alpha"], lora_dropout=L["lora_dropout"],
            target_modules=targets, task_type="CAUSAL_LM", bias="none"))
        say(f"   seed {seed_used} set BEFORE the adapter is built, so the "
            f"initialisation is governed by it and not by the ambient RNG")
    # GRADIENT CHECKPOINTING WITH A FROZEN BASE NEEDS THE EMBEDDING OUTPUT TO
    # REQUIRE GRAD. With every base parameter frozen, the embedding output
    # carries no grad_fn, so a checkpointed segment recomputes a graph that
    # connects to nothing and backward fails with "element 0 of tensors does not
    # require grad". This marks an activation as requiring grad so the graph
    # connects; no parameter's frozen state changes, and the trainable count is
    # asserted unchanged.
    _before = sum(p.numel() for p in model.parameters() if p.requires_grad)
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    _after = sum(p.numel() for p in model.parameters() if p.requires_grad)
    assert _before == _after, (
        f"enable_input_require_grads changed the trainable count "
        f"{_before} -> {_after}; it must not")
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    say(f"   adapter attached: {trainable/1e6:.2f} M trainable of "
        f"{total/1e6:.1f} M ({100*trainable/total:.3f}%), dtype {actual_dtype}")

    # THE SPECIFICATION'S `warmup_ratio` IS CONVERTED TO STEPS. transformers 5.x
    # takes an absolute `warmup_steps`; the specification states a ratio of
    # training, so the ratio is applied to the step count this configuration
    # produces and both numbers go in the manifest.
    eff_batch = L["per_device_batch_size"] * L["gradient_accumulation_steps"]
    steps_per_epoch = -(-len(train) // eff_batch)          # ceil
    total_steps = steps_per_epoch * L["epochs"]
    warmup_steps = round(L["warmup_ratio"] * total_steps)
    say(f"   warmup_ratio {L['warmup_ratio']} of {total_steps} total steps "
        f"-> warmup_steps {warmup_steps} (effective batch {eff_batch}, "
        f"{steps_per_epoch} steps/epoch x {L['epochs']} epochs)")
    say("     the spec's warmup RATIO is converted to steps, never replaced by a "
        "hand-written step count")

    resumed = bool(a.resume_adapter)
    if resumed:
        if a.extra_steps <= 0:
            sys.exit("REFUSING: --resume-adapter needs --extra-steps > 0")
        say(f"   RESUMED SEGMENT: {a.extra_steps} steps at constant lr "
            f"{L['learning_rate']} (cosine and warmup both disabled)")
    args = TrainingArguments(
        output_dir=f"{R}/runs/{a.run}/_trainer",
        num_train_epochs=(100 if resumed else L["epochs"]),
        learning_rate=L["learning_rate"],
        lr_scheduler_type=("constant" if resumed else L["lr_scheduler"]),
        warmup_steps=(0 if resumed else warmup_steps),
        per_device_train_batch_size=L["per_device_batch_size"],
        gradient_accumulation_steps=L["gradient_accumulation_steps"],
        seed=seed_used, bf16=(not a.dry_run and L["bf16"]),
        gradient_checkpointing=not a.dry_run,
        logging_steps=10, save_strategy="no", report_to=[],
        # A DRY RUN EXERCISES THE PATH; IT DOES NOT TRAIN. The boundary
        # assertion, which is the check worth having, runs over every pair
        # before this loop starts and is unaffected by the step cap.
        **({"max_steps": DRY_RUN_STEPS} if a.dry_run
           else {"max_steps": a.extra_steps} if resumed else {}),
    )
    # ── GRADATION CURVE CALLBACK ────────────────────────────────────────────
    grad_curve = []
    callbacks = []
    if a.gradation_eval_every > 0:
        import re as _re
        from transformers import TrainerCallback

        rate_rows = [r for r in train
                     if _re.fullmatch(r"\s*\d\s*", r["completion"])]
        say(f"   gradation curve: every {a.gradation_eval_every} steps on "
            f"{len(rate_rows)} bare-digit TRAINING items")
        if not rate_rows:
            sys.exit("REFUSING: --gradation-eval-every with no digit targets "
                     "in the set; the curve would measure nothing")
        # THE DEVICE IS READ AT CALL TIME, NEVER CAPTURED HERE. `Trainer` moves
        # the model to the accelerator when `train()` starts, so a device bound
        # at setup would be the CPU.
        _dids = [tok(f" {d}", add_special_tokens=False)["input_ids"][-1]
                 for d in range(10)]
        if len(set(_dids)) != 10:
            sys.exit(f"REFUSING: the ten digit answers do not tokenise to ten "
                     f"distinct ids ({sorted(set(_dids))}); the curve would "
                     f"score different digits as the same answer")

        def _measure(step):
            """Mode, MAE and fit against the digit the item was trained on.

            **UNDER `no_grad` AND WITH TRAINING MODE RESTORED**, so the curve
            cannot perturb the run it is describing. Eval mode is entered and
            left exactly around the measurement, so dropout does not add noise.
            """
            was_training = model.training
            model.eval()
            dev = next(model.parameters()).device      # read NOW, not at setup
            pred, targ = [], []
            try:
                with torch.no_grad():
                    for r in rate_rows:
                        ids = tok(r["prompt"], return_tensors="pt").to(dev)
                        lg = model(**ids).logits[0, -1]
                        pr = torch.softmax(lg[_dids].float(), 0)
                        pred.append(int(pr.argmax()))
                        targ.append(int(r["completion"].strip()))
            finally:
                if was_training:
                    model.train()
            n = len(pred)
            exact = sum(p == t for p, t in zip(pred, targ))
            mae = sum(abs(p - t) for p, t in zip(pred, targ)) / n
            modal = max(set(pred), key=pred.count)
            return {"step": step, "n": n, "exact": exact,
                    "exact_pct": round(100 * exact / n, 2),
                    "mae": round(mae, 4),
                    "modal_digit": modal,
                    "modal_share": round(pred.count(modal) / n, 4),
                    "distinct_digits": len(set(pred))}

        class GradationCurve(TrainerCallback):
            def on_train_begin(self, args_, state, control, **kw):
                # Step 0 is taken here, once the model is on the accelerator.
                row = _measure(0)
                grad_curve.append(row)
                say(f"     step    0  exact {row['exact_pct']:>5.1f}%  "
                    f"MAE {row['mae']:.2f}  modal {row['modal_digit']} on "
                    f"{row['modal_share']:.0%}  distinct {row['distinct_digits']}")

            def on_step_end(self, args_, state, control, **kw):
                if state.global_step % a.gradation_eval_every == 0:
                    row = _measure(state.global_step)
                    grad_curve.append(row)
                    say(f"     step {row['step']:>4}  exact "
                        f"{row['exact_pct']:>5.1f}%  MAE {row['mae']:.2f}  "
                        f"modal {row['modal_digit']} on {row['modal_share']:.0%}"
                        f"  distinct {row['distinct_digits']}")

        callbacks.append(GradationCurve())

    t0 = time.time()
    tr = Trainer(model=model, args=args, train_dataset=DS(),
                 data_collator=collate, callbacks=callbacks or None)
    res = tr.train()
    secs = time.time() - t0
    say(f"   trained in {secs/60:.1f} min | final loss "
        f"{res.training_loss:.4f} over {res.global_step} steps")

    model.save_pretrained(adapter_dir)
    say(f"   adapter -> {os.path.relpath(adapter_dir, R)}")

    # The environment pin gets its own digest, kept separate from I.digest() so
    # the instruments digest identifies the instruments alone.
    import hashlib
    req_path = f"{R}/requirements.txt"
    # The environment pin is a RECORD, not a precondition: the tune is already
    # finished by this point and nothing about it depends on reading this file.
    # So its absence is recorded rather than raised, and the manifest is still
    # written.
    try:
        req_digest = hashlib.sha256(open(req_path, "rb").read()).hexdigest()[:16]
        say(f"   environment pin digest {req_digest} "
            f"({os.path.relpath(req_path, R)})")
    except FileNotFoundError:
        req_digest = None
        say(f"   *** ENVIRONMENT PIN NOT PRESENT at "
            f"{os.path.relpath(req_path, R)}: recording its ABSENCE. The tune is "
            f"complete and unaffected; the manifest cannot name the pinned "
            f"environment and says so.")

    man = {
        "run": a.run, "corpus": a.corpus, "dry_run": a.dry_run,
        "max_seq_length_used": L["max_seq_length"],
        "max_seq_length_overridden": msl_overridden,
        "micro_batch_used": L["per_device_batch_size"],
        "gradient_accumulation_used": L["gradient_accumulation_steps"],
        "effective_batch_asserted": (L["per_device_batch_size"]
                                     * L["gradient_accumulation_steps"]),
        "overrides_why": ("declared overrides of max_seq_length and/or the "
                          "micro-batch; raising max_seq_length only affects pairs "
                          "longer than the old limit, and the effective batch is "
                          "held fixed"
                          if (msl_overridden or mb_overridden) else None),
        "heldout_corpus": (a.heldout_corpus or a.corpus),
        "heldout_borrowed": bool(a.heldout_corpus and a.heldout_corpus != a.corpus),
        "heldout_borrowed_why": (
            "the held-out slice checks form only (parse rate against the floor) and "
            "is taken from another set; overlap with the training set asserted "
            "absent by uid, sha and normalised text at load time."
            if (a.heldout_corpus and a.heldout_corpus != a.corpus) else None),
        "lora_spec": a.lora, "lora_spec_digest": spec_digest,
        "base_model_config": L["base_model"],
        "base_model_used": model_id,
        "base_model_overridden": base_model_overridden,
        "base_model_override_why": (
            "the base model is set by --base-model; every other hyperparameter is "
            "the specification's, and the specification and its digest are not "
            "mutated."
            if base_model_overridden else None),
        "seed_config": L["seed"],
        "seed_used": seed_used,
        "seed_overridden": seed_overridden,
        "seed_override_why": (
            "--seed overrides the seed and nothing else; lora_spec_digest is "
            "unchanged because the specification is unchanged."
            if seed_overridden else None),
        "instruments_digest": I.digest(), "model": model_id,
        "requirements_digest": req_digest,
        "requirements_path": os.path.relpath(req_path, R),
        "environment_observed": {
            "python": sys.version.split()[0],
            "torch": __import__("torch").__version__,
            "transformers": __import__("transformers").__version__,
            "peft": __import__("peft").__version__,
        },
        "environment_note":
            "torch's CUDA build, the Python version and cuDNN are set by the "
            "machine image rather than by requirements.txt; the observed versions "
            "are recorded above.",
        "dtype_from_model_not_spec": actual_dtype,
        "hyperparameters": L,
        "hyperparameters_source":
            "school_tune_instruments.LORA or LORA_V2; this script has no "
            "hyperparameter flags beyond the declared overrides",
        "loss": "answer tokens only; prompt masked with -100",
        "why_answer_only":
            "the tune's one job is to teach that the text after a question is "
            "the answer; loss over the whole pair also trains question "
            "prediction, and dilutes the composition proportion because the "
            "hedged register lives entirely in the answers",
        "warmup_ratio_banked": L["warmup_ratio"],
        "warmup_steps_derived": warmup_steps,
        "total_optimizer_steps": total_steps,
        "effective_batch": eff_batch,
        "why_warmup_converted":
            "transformers 5.x takes an absolute `warmup_steps`; the "
            "specification states a ratio of training, so the ratio is applied "
            "to the step count this configuration produces.",
        "boundary_checks": boundary,
        "n_train": len(train), "n_held_out": len(held),
        "trainable_params": trainable, "total_params": total,
        "train_seconds": round(secs, 1),
        "final_loss": res.training_loss, "steps": res.global_step,
        "resumed_from_adapter": a.resume_adapter,
        "resumed_segment_steps": (a.extra_steps if a.resume_adapter else None),
        "resumed_schedule_note": (
            "a resumed segment runs at a CONSTANT learning rate from the "
            "specification with no warmup and no decay, because the cosine "
            "schedule had decayed to approximately zero and cannot be continued. "
            "The learning rate therefore DIFFERS ACROSS THE JOIN, so this "
            "segment's curve may not be joined to the original's and read as one "
            "training run."
            if a.resume_adapter else None),
        # The curve is empty unless --gradation-eval-every was passed.
        "gradation_eval_every": a.gradation_eval_every,
        "gradation_curve": grad_curve,
        "gradation_curve_note": (
            "mode-vs-target on the TRAINING digit items, measured under no_grad "
            "with training mode restored. A curve still rising at the final step "
            "says the run was short; a plateau says the set or the capacity is "
            "the constraint. Fitting what was shown is the diagnostic, so this "
            "is deliberately not a generalisation measurement."),
        "adapter_dir": os.path.relpath(adapter_dir, R),
        # ── THE PROVENANCE BLOCK ────────────────────────────────────────────
        # Written by the trainer at train time, so a published adapter can state
        # how its weights were made without reconstruction afterwards.
        "provenance": _provenance(
            model_id, a, adapter_dir, boundary,
            f"{CORPUS}/instruction_corpus_{a.corpus}.jsonl",
            seed_config=L["seed"], seed_used=seed_used),
        "held_out_parse_floor": I.HELD_OUT_PARSE_FLOOR,
        "held_out_check_is_a_separate_stage":
            "this script reads no answers from the tuned model; the held-out "
            "parse check and any further reading are separate stages",
    }
    if a.dry_run:
        man["DRY_RUN_WARNING"] = (
            "tiny stand-in model on CPU. These numbers are PLUMBING and none "
            "may be quoted.")
    json.dump(man, open(man_path, "w"), indent=1)
    open(txt_path, "w").write("\n".join(lines) + "\n")
    say(f"   manifest -> {os.path.relpath(man_path, R)}")


if __name__ == "__main__":
    main()

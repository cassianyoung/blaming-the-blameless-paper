#!/usr/bin/env python3
"""gradient_model.py : the two readouts every stage of an earlier run uses.

One scorer and one sampler, written once so no stage can quietly differ from
another in how it reads the model. Governed by `records/PREREG_probe_gradient.md`
sections 2 and 10.

TWO NUMBERS PRESENTED AS A CHANGE MUST COME FROM THE SAME INSTRUMENT, and this
module exists because the pilot, the gate, the behavioural sweep and the §6
extension all quote quantities that get compared with each other.

THE SCORER. Each of the ten graded answers is scored by TEACHER-FORCED
log-probability over ALL of its own tokens, batched so the cost is one forward
pass per cell. Never a first-token readout: under the raw frame convention all ten
answers resolve to a single first token on this tokeniser, so a first-token
readout could not fail its own readability test there. That is the banked defect
of 2026-08-23, and stage 0 measures it per frame rather than assuming it.

LENGTH. The scale is 0..9, so every answer is the SAME token length within a frame
and there is no length bias to correct. What normalisation then does depends on
that length, and the two cases are different: at L = 1 (the chat convention)
`logprob_norm` IS `logprob_raw` and the two channels are identical, so the
two-normalisation rule of 2026-08-23 is vacuous; at L = 2 (the raw convention) norm
is raw/2, a TEMPERATURE RESCALING of the answer distribution, which cannot change
the argmax but does change the MEAN RESPONSE and therefore can change a curve.
Measured on the pilot: the two channels put the same frame first, and their
separations differ (f1: 2.180 raw against 1.246 norm). Which case applies is a
property of the frozen frame and the pilot records it.

Under 0..10 there WAS a length difference, and it came with a worse problem than
the bias it would have caused: "1" is a strict token-prefix of "10", so the shorter
strictly dominated and the top of the scale was unreachable.

`answer_mass` is the probability the next token BEGINS some answer, summed over
the DISTINCT first tokens. Deduplication is what keeps it bounded by 1: under the
raw convention it is P(space), a real readability measure rather than ten copies of
one, and under the chat convention it is the mass on the ten digits.

THE SAMPLER returns the parsed integers, the raw strings, and the parse rate. A
sample that does not parse is COUNTED, never silently dropped: an absent
measurement emits its absence.

PRECISION IS A PRE-BINDING, NOT AN INFERENCE. `load()` takes "<device>:<dtype>"
from `prebindings.json` and refuses if that device is unavailable, rather than
picking whatever is to hand. THE TWO SPECS ARE NOT NAMED HERE, because prose is
not where they live and this sentence read `mps:bfloat16` / `cpu:float32` for ten
days after the 2026-08-28 rebinding moved both to cuda. Read them from
`prebindings.json`, where each carries its own date and reason; the two are
compared on the pilot's own cells by
`gradient_precision.py` before the sweep is spent, against a bound fixed in
advance. bf16 is Gemma-2's release precision and the precision a 9B replication
would run at, so this is not the quantisation refusal of 2026-08-23 in reverse:
that refused reading logits off a compressed model to make it fit, and the claim
that these two agree is measured rather than asserted.
"""
import os
import re

import numpy as np
import torch

_INT = re.compile(r"-?\d+")


_DTYPES = {"float32": torch.float32, "bfloat16": torch.bfloat16,
           "float16": torch.float16}


def load(model_id, spec, threads=None, adapter=None, trust_remote_code=False):
    """`spec` is "<device>:<dtype>", read from prebindings and never inferred.

    THE DEVICE IS A PRE-BINDING BECAUSE IT IS PART OF THE INSTRUMENT. Inferring it
    from what happens to be available is how two stages end up reading the model
    at two precisions and quoting the difference as a result.

    `adapter` (added 2026-09-10 for the school tune's §3) loads a PEFT/LoRA
    adapter onto `model_id` and MERGES it, so every generation-side instrument
    reads the tuned model through the code that produced the base and vendor
    readings it is being compared against. A separate tuned-model loader would
    confound the arm difference with a code difference.
    """
    import hashlib
    import os
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if threads:
        torch.set_num_threads(int(threads))
    dev, _, dtn = spec.partition(":")
    if dev == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("prebindings ask for mps and it is not available")
    if dev == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("prebindings ask for cuda and it is not available")
    dt = _DTYPES[dtn]
    # **`trust_remote_code` IS OPT-IN AND DEFAULTS OFF, so every arm read before
    # 2026-09-15 is byte-identical.** It executes code shipped by the repo owner.
    # It is needed for `m-a-p/CT-LLM-*`, whose only custom file is
    # `tokenization_baichuan.py`: a 253-line PreTrainedTokenizer subclass wrapping
    # SentencePiece, read before it was run, with no subprocess, eval, exec or
    # network calls. That inspection is the licence, not the convenience.
    tok = AutoTokenizer.from_pretrained(model_id,
                                        trust_remote_code=trust_remote_code)
    # VERSION-DEPENDENT KWARG, SAME SHIM AS extract.py AND school_tune_tune.py
    # (2026-09-13, an earlier run: the THIRD place this was needed). `dtype=` is the
    # modern spelling; transformers <= 4.5x wants `torch_dtype=` and passes an
    # unknown `dtype` through to the constructor, where Qwen3ForCausalLM raises
    # TypeError. Qwen3 needs >= 4.51 and torch 2.4.1 refuses >= 5, so 4.51.3 is
    # the only window and it is the older spelling.
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, dtype=dt, trust_remote_code=trust_remote_code)
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=dt, trust_remote_code=trust_remote_code)
    adapter_digest = None
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
        model = model.merge_and_unload()
        h = hashlib.sha256()
        for f in sorted(os.listdir(adapter)):
            if f.endswith((".safetensors", ".bin", ".json")):
                h.update(open(os.path.join(adapter, f), "rb").read())
        adapter_digest = h.hexdigest()[:16]
    model.to(dev)
    model.eval()
    # DTYPE RECORDED FROM THE MODEL, NOT FROM THE SPEC STRING. Banked weakness
    # (2026-09-09, `POD_ERRAND_moral_frame_pilot.md` and RUNS.md row 121): this
    # meta read the spec, so a `dtype=` that was silently ignored would have
    # produced a float32 run reporting itself as bf16. The check passed then and
    # the weakness was left unfixed; it is fixed here. `dtype` keeps its old
    # meaning (what was ASKED FOR) so nothing downstream that reads it changes.
    return tok, model, {"device": dev, "dtype": dtn, "spec": spec,
                        "dtype_from_model": str(next(model.parameters()).dtype),
                        "model_id": model_id, "adapter": adapter,
                        "adapter_digest": adapter_digest,
                        "arm_kind": "tuned" if adapter else "base",
                        "trust_remote_code": bool(trust_remote_code),
                        "threads": torch.get_num_threads()}


def sync(model):
    if next(model.parameters()).device.type == "mps":
        torch.mps.synchronize()


def answer_ids(tok, answers, prefix=" ", prompt=None):
    """Token ids for each answer AS THE FRAME WILL RENDER IT.

    `prefix` belongs to the frame, not to the answer: a raw "A:" frame continues
    with " 7" and a chat frame, after "<start_of_turn>model\\n", continues with
    "7". Scoring the wrong one reads a string the model will never emit, which the
    dry run exposed as answer_mass 0.0000 on both chat candidates.

    ═══════════════════════════════════════════════════════════════════════════
    `prompt` MAKES THE TOKENISATION IN CONTEXT, AND ON A SENTENCEPIECE TOKENISER
    THAT IS THE DIFFERENCE BETWEEN A READING AND A NULL (added 2026-09-12).

    Without it, the ids come from tokenising the answer STANDALONE, and
    **SentencePiece prepends its space piece to a standalone string whatever
    `prefix` says.** On `01-ai/Yi-1.5-9B-Chat`:

        tok("0")   -> [59568, 77]   ['▁', '0']
        tok(" 0")  -> [59568, 77]   IDENTICAL
        tok("答：0") -> [..., 106, 77]  no ▁ at all

    So `prefix=""` and `prefix=" "` produce the same ids, and `first_ids` is the
    `▁` piece. **In English that piece is genuinely emitted** -- Yi's English
    answer mass read 0.9501 -- and in Chinese it is not, so the mass reads ~0 and
    an answer-mass floor fires on the SCORER rather than on the model. An earlier run
    eliminated all three Chinese frames on Yi that way, at parse 1.00 and
    separations up to +4.38.

    **THE ANALOGY THAT WAS USED TO DISMISS THIS IS WHY IT SURVIVED.** `gemma-2-9b`
    with the banked `prefix=" "` also has all ten answers sharing a first token,
    and that IS documented design. The mechanism is identical; the consequence is
    not, because gemma's shared piece is emitted and Yi's Chinese one is not. **An
    analogy between two instruments has to hold at the level of what is OBSERVED,
    not only at the level of how it works.**

    With `prompt` given, the ids are the delta between tokenising the prompt and
    tokenising prompt+prefix+answer, which is exactly what the model will be fed.
    A retokenisation that changes the prompt's own ids raises, because then the
    scored string is not the rendered string.

    **NO CALL SITE IN THIS REPO PASSES `prompt`, AND ON Qwen3 THAT IS SAFE AND
    MEASURED (2026-09-14).** Every caller here uses the standalone form. Before
    running a CHINESE frame on `Qwen/Qwen3-8B-Base` the question was settled by
    measurement rather than by reasoning from tokeniser family: all ten answer
    atoms tokenise identically standalone and in context, under both the English
    and the Chinese frame, and the prompt does not retokenise when an answer is
    appended. Qwen3 is byte-level BPE, so `" 0"` is `[220, 15]` -- an explicit
    space token then the digit -- with no SentencePiece `▁` piece and therefore no
    Chinese-context divergence. Artefact: `records/ZH_FRAME_ANSWER_ATOMS.json`.

    **THIS LICENSES Qwen3 AND NOTHING ELSE.** The Yi failure is a property of
    SentencePiece tokenisers, and any arm using one must measure this again before
    a non-English frame is trusted. That is this docstring's own rule applied to
    itself: an analogy between two instruments has to hold at the level of what is
    OBSERVED.
    ═══════════════════════════════════════════════════════════════════════════
    """
    if prompt is None:
        ids = [tok(f"{prefix}{a}", add_special_tokens=False)["input_ids"]
               for a in answers]
        return ids, sorted({a[0] for a in ids})
    base = tok(prompt, add_special_tokens=False)["input_ids"]
    ids = []
    for a in answers:
        full = tok(f"{prompt}{prefix}{a}", add_special_tokens=False)["input_ids"]
        if full[:len(base)] != base:
            raise ValueError(
                f"REFUSING: appending {prefix + a!r} retokenises the prompt, so the "
                f"scored string is not the rendered string. Answer {a!r}.")
        ids.append(full[len(base):])
    return ids, sorted({a[0] for a in ids})


def score(tok, model, prompt, answers, ans_ids=None, first_ids=None, depths=None,
          prefix=" ", values=None, forward_kwargs=None):
    """Teacher-forced full-answer scoring for one cell. One forward pass.

    `values` and `forward_kwargs` were added 2026-09-08 for an earlier run's outing and
    BOTH DEFAULT TO THE PREVIOUS BEHAVIOUR EXACTLY, because this is the shared
    instrument and two numbers presented as a change must come from it unchanged.

    `values` is the numeric value of each answer, used only for the mean response.
    It defaulted to `float(answer)` and still does, which is right for a digit
    scale and impossible for the base arm's completion frame, whose answers are
    truth-value WORDS. Passing `values=False` returns `mean_raw` and `mean_norm`
    as None rather than inventing an ordering over words that has none. A THIRD
    OPTION WOULD HAVE BEEN A SEPARATE SCORER for that arm, and it was rejected:
    two scorers drift, and the distribution, the entropy and the answer mass are
    the same quantities whatever the answers denote. Only the mean is not.

    `forward_kwargs` passes model-specific flags into the forward call, and exists
    for one case: `output_router_logits=True` on an MoE, which is how the expert
    assignment is read. It is a passthrough and this module asserts nothing about
    it.

    `depths` also returns the residual stream over the PROMPT positions, last and
    mean pooled, from THE SAME forward pass. That is not an optimisation for its
    own sake: row 0 of this batch is the prompt followed by the answer "0", and
    positions 0..np-1 are the prompt alone, so the activations a probe reads are
    literally the ones the behavioural reading was taken from. Harvesting them
    separately would have run the model twice and left two sets of activations
    that could drift apart.
    """
    if ans_ids is None:
        # IN CONTEXT BY DEFAULT (2026-09-12). A caller that does not precompute the
        # ids gets the corrected path without having to remember it, and the test
        # `tests/test_answer_ids_in_context.py` pins that this is identical to the
        # old standalone result on Qwen3, gemma-2-9b, gemma-2-27b and Yi-in-English,
        # i.e. everywhere the standalone path was right.
        ans_ids, first_ids = answer_ids(tok, answers, prefix, prompt=prompt)
    dev = next(model.parameters()).device
    p_ids = tok(prompt, return_tensors="pt")["input_ids"][0].tolist()
    np_ = len(p_ids)
    seqs = [p_ids + a for a in ans_ids]
    mx = max(len(s) for s in seqs)
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    batch = torch.full((len(seqs), mx), pad, dtype=torch.long)
    mask = torch.zeros((len(seqs), mx), dtype=torch.long)
    for i, sq in enumerate(seqs):
        batch[i, :len(sq)] = torch.tensor(sq)
        mask[i, :len(sq)] = 1
    mxa = max(len(a) for a in ans_ids)
    acts = None
    with torch.no_grad():
        out = model(input_ids=batch.to(dev), attention_mask=mask.to(dev),
                    output_hidden_states=bool(depths),
                    **(forward_kwargs or {}))
        lg = out.logits
        win = lg[:, np_ - 1: np_ + mxa - 1, :].float()
        lp = torch.log_softmax(win, -1).cpu()
        pr0 = torch.softmax(lg[0, np_ - 1].float(), -1).cpu()
        if depths:
            # Row 0 is prompt + "0"; positions 0..np_-1 are the PROMPT ALONE, so
            # the slice is the prompt's own residual stream and carries none of
            # the answer. Taken from the row rather than from the batch, because
            # rows 1..10 differ only after np_ and pooling over the batch would
            # mix answers into a quantity that must be answer-free.
            acts = {}
            for d in depths:
                h = out.hidden_states[d][0, :np_].float()
                acts[int(d)] = {"last": h[-1].cpu().numpy(),
                                "mean": h.mean(0).cpu().numpy()}
    # ROUTER LOGITS, MoE ONLY, and only when the caller asked for them.
    # `router_logits` is one entry per DECODER LAYER, so entry d-1 is the router
    # that produced hidden_states[d]; depth 0 is the embedding table and has no
    # router, which is why it returns None rather than entry -1. Each entry is
    # (batch * seq, n_experts) flattened, so row 0's last prompt position is at
    # index (np_ - 1) with a batch stride of `mx`.
    routing = None
    rl = getattr(out, "router_logits", None) if forward_kwargs else None
    if rl is not None and depths:
        routing = {}
        for d in depths:
            if d < 1 or (d - 1) >= len(rl) or rl[d - 1] is None:
                routing[int(d)] = None
                continue
            lg = rl[d - 1].float().reshape(len(seqs), mx, -1)[0, np_ - 1]
            pr = torch.softmax(lg, -1)
            k = min(2, pr.numel())
            tk = torch.topk(pr, k)
            routing[int(d)] = {"experts": [int(i) for i in tk.indices],
                               "weights": [float(p) for p in tk.values],
                               "n_experts": int(pr.numel())}
    raw, norm = [], []
    for i, a in enumerate(ans_ids):
        tot = float(sum(float(lp[i, k, t]) for k, t in enumerate(a)))
        raw.append(tot)
        norm.append(tot / len(a))
    d_raw = torch.softmax(torch.tensor(raw), -1).numpy()
    d_norm = torch.softmax(torch.tensor(norm), -1).numpy()
    if values is False:
        m_raw = m_norm = None            # the answers carry no ordering; see above
    else:
        vals = np.array([float(x) for x in (values if values is not None
                                            else answers)], dtype=float)
        m_raw, m_norm = float(np.dot(d_raw, vals)), float(np.dot(d_norm, vals))
    ent = float(-np.sum(d_raw * np.log(d_raw + 1e-12)))
    top = torch.topk(pr0, 5)
    return {
        "logprob_raw": raw, "logprob_norm": norm,
        "dist": d_raw.tolist(), "dist_norm": d_norm.tolist(),
        "mean_raw": m_raw, "mean_norm": m_norm,
        "argmax_raw": answers[int(np.argmax(d_raw))],
        "argmax_norm": answers[int(np.argmax(d_norm))],
        "entropy": ent,
        "answer_mass": float(sum(float(pr0[t]) for t in first_ids)),
        "n_answer_tokens": [len(a) for a in ans_ids],
        "n_distinct_first_tokens": len(first_ids),
        "top5": [[tok.decode([int(i)]), float(p)]
                 for p, i in zip(top.values, top.indices)],
        "n_prompt_tokens": int(np_),
        "acts": acts,
        "routing": routing,
    }


def sample(tok, model, prompt, n, temperature, seed, lo, hi, max_new=4,
           chunk=0):
    """n sampled continuations at a fixed temperature and a recorded seed.

    `chunk` SPLITS THE GENERATION INTO SEVERAL CALLS AND DEFAULTS TO 0, WHICH IS
    THE PREVIOUS BEHAVIOUR EXACTLY (one call, `num_return_sequences=n`). It exists
    for one measured reason: on 2026-09-08 Mixtral-8x7B loaded fine in bf16 at
    87 GiB and then OOMed inside `generate`, which tried to allocate 13.12 GiB to
    materialise thirty sequences at once against 7 GiB free. THE WEIGHTS WERE
    NEVER THE PROBLEM; the sampler was, and the bf16-first ruling was right.

    IT IS AN INSTRUMENT CHANGE ON THE SAMPLING CHANNEL AND IS DECLARED AS ONE.
    The draw is still n continuations at the same temperature, so the estimator is
    unchanged, but the SEQUENCE of random numbers differs: one call of thirty and
    six calls of five do not produce the same thirty samples. Each chunk therefore
    carries its own derived seed, printed into the artefact, so the draw is
    reproducible even though it is not identical to an unchunked one. The
    teacher-forced channel, which is the primary reading, is untouched.

    `lo` and `hi` are REQUIRED rather than defaulted, because a default here is a
    second source of truth about what counts as an answer: when the scale moved
    from 0..10 to 0..9 a stale default would have kept admitting a sampled "10"
    that the scorer has no column for.
    """
    dev = next(model.parameters()).device
    enc = tok(prompt, return_tensors="pt")
    sizes = ([int(n)] if not chunk else
             [min(int(chunk), int(n) - i) for i in range(0, int(n), int(chunk))])
    seeds, texts = [], []
    npr = enc["input_ids"].shape[1]
    for k, sz in enumerate(sizes):
        sk = int(seed) + k * 7919      # a prime, so chunk seeds cannot collide
        seeds.append(sk)
        torch.manual_seed(sk)
        with torch.no_grad():
            out = model.generate(
                input_ids=enc["input_ids"].to(dev),
                attention_mask=enc["attention_mask"].to(dev),
                do_sample=True, temperature=float(temperature), top_k=0, top_p=1.0,
                max_new_tokens=int(max_new), num_return_sequences=int(sz),
                pad_token_id=tok.pad_token_id or tok.eos_token_id)
        texts += [tok.decode(o[npr:], skip_special_tokens=True) for o in out]
    parsed, unparsed = [], []
    for t in texts:
        m = _INT.search(t)
        v = int(m.group()) if m else None
        if v is None or not (lo <= v <= hi):
            unparsed.append(t)
        else:
            parsed.append(v)
    return {"texts": texts, "parsed": parsed, "n_parsed": len(parsed),
            "chunk": int(chunk), "chunk_seeds": seeds,
            "n_unparsed": len(unparsed), "unparsed_examples": unparsed[:5],
            "parse_rate": len(parsed) / max(1, len(texts)),
            "seed": int(seed), "temperature": float(temperature),
            "mean": float(np.mean(parsed)) if parsed else None,
            "sd": float(np.std(parsed, ddof=1)) if len(parsed) > 1 else None}

#!/usr/bin/env python3
"""rate_pod216.py : ONE LOAD, everything a local_tuning checkpoint owes. §4 of the order.

    python3 scripts/rate_pod216.py --run local_tuning --arm llama31_base \
        --model meta-llama/Llama-3.1-8B --spec cuda:bfloat16 --delivery completion
    python3 scripts/rate_pod216.py ... --delivery completion,chat   # ONE load, both
    python3 scripts/rate_pod216.py ... --dry-run          # gpt2, CPU, offline

**`--delivery` TAKES A LIST AND THE LOAD IS SHARED ACROSS IT.** An earlier run measured the
cost of not doing this: four two-item cells on Yi-1.5-34B read 762 s, 1 s, 1 s, 2 s, so
the first cell was **99.87% load**, and driving one frame per invocation re-read 69 GB
four times. An instruct arm owes both deliveries, so asking for them separately paid
for the checkpoint twice. Each delivery still writes its OWN artefact, so the
write-once paths and everything downstream are unchanged.

Stages, in order, all off one load:

    a  determinism assert: one cell, two forward passes, identical logits
    b  gates: N mean <= --gate-mean and mass(0-3) >= 0.8; I >= 7; answer mass >= 0.7
    c  completion: ten rows, BLAME, five permutations          (--delivery completion)
    d  chat: ten rows, four channels                           (--delivery chat)
    f  harvest: final-token residual stream, every layer, BLAME + REASONABLE

**A FAILED GATE BANKS THE CHECKPOINT AS FAILED AND RETURNS. It never lowers a
threshold**, and `--gate-mean` exists so a relaxation is passed explicitly and recorded
in the artefact beside its default, never edited in (deployed_bicycle_ladder's Gemma cell).

**YES/NO CHANNELS GO THROUGH `values=False`**, which `gradient_model.score` documents
for word answers, so the distribution, entropy and answer mass come off the same
instrument as the digit channels and only the mean is withheld.
"""
import argparse, hashlib, json, os, statistics, sys, time

R = os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
import bank_lock
import moral_frames as MF
import gradient_model as MODEL

BANK = "records/excuse_bank.jsonl"
FRAMES = "records/POD_FRAMES_216.json"
LADDER = ["P0", "P1", "P2", "P1_R", "P1_neutral", "P2_other", "BYSTANDER"]
ROWS_ALL = ["N", "C", "I"] + LADDER
SUPPLIER_ROLES = ["SUPPLIER"]


def ROWS_PRESENT(rows):
    """The canonical role order, restricted to what this bank actually holds.

    The bicycle bank has the ten roles of ROWS_ALL. The families bank has those plus
    SUPPLIER, and only on the two prawns families. A FIXED LIST WOULD EITHER MISS
    SUPPLIER OR DEMAND IT WHERE IT DOES NOT EXIST, and a KeyError mid-read costs the
    load. Ordering is kept canonical rather than taken from the file, so two families
    with different role sets still report in the same column order.
    """
    return [u for u in ROWS_ALL + SUPPLIER_ROLES if u in rows]
NEAR_MISS_N = 0.25   # how far past the N gate still gets its battery read
PREFIX_OK = 0.50     # declared prefix is kept if it carries at least this much mass
# ── THE COMPLETION-FRAME GATE IS BAND-RELATIVE (Cassian, HALT 2, 2026-09-30) ──
# The fixed digits (N <= 1.05, I >= 7) were set on CHAT and API arms and were never
# calibrated for a worksheet read by a base model. On llama-3.1-8B all three arms
# failed them while sitting 5 to 8 band-widths below P0, which is a floor by any
# reading that matters. So on completion, "floor" means "N sits well below the effect
# being measured", and the permutation band is the unit.
#   N is a floor   if mass(0-3) >= 0.8 AND (P0 - N) >= 3 bands
#   I is a ceiling if (I - C) >= 2 bands
#   answer mass    >= 0.7, as before
# **THE FIXED DIGITS STAY FOR CHAT AND API CELLS**, which have no permutation band.
# ── THE BAND IS 2.33 x sd, NOT THE RANGE (Cassian, 2026-09-30) ──────────────
# A RANGE IS AN ESTIMATOR WHOSE EXPECTATION GROWS WITH THE NUMBER OF DRAWS, so bands
# from different n are not comparable and n becomes a hidden variable in the gate.
# Measured on qwen3_base: range 1.167 at n=5 -> 1.307 at n=10, +12%, while sd moved
# 0.424 -> 0.429, +1%. 2.33 reproduces the expected range of five normal draws, so the
# tier boundaries keep the meaning they were calibrated with on n=5.
BAND_SD_K = 2.33
BANDS_N_FLOOR = 3.0      # LICENSED: enters the headline tables and the Q1 count
BANDS_N_DIRECTIONAL = 1.5  # DIRECTIONAL: banked, second table, band as the error bar
BANDS_I_CEIL = 2.0
# ── THREE TIERS, NOT TWO (Cassian, 2026-09-30, after qwen3_base) ─────────────
# qwen3_base reads N 1.731 and P0-N 2.216 against llama31_base's 1.739 and 2.527: the
# EFFECT is the same size, and what differs is that its five permutations disagree 2.4x
# more (band 1.167 against 0.491). A hard pass/fail at 3 bands throws that arm out
# entirely; the fixed digit would have passed it. Neither is right for an arm whose
# DIRECTION is clear and whose MAGNITUDE is uncertain, so it is banked as DIRECTIONAL
# and reported with the band as its error bar, never in the headline count.
HARVEST_CHANNELS = ("BLAME", "REASONABLE")


def _env():
    """torch and friends, recorded so a reading is tied to the numerics behind it."""
    import platform
    out = {"python": platform.python_version()}
    for mod in ("torch", "transformers", "peft", "safetensors", "numpy"):
        try:
            out[mod] = __import__(mod).__version__
        except Exception as e:
            out[mod] = f"<{type(e).__name__}>"
    try:
        import torch
        out["cuda_build"] = torch.version.cuda
        out["cuda_available"] = torch.cuda.is_available()
        out["device_name"] = (torch.cuda.get_device_name(0)
                              if torch.cuda.is_available() else None)
        out["driver_cuda"] = getattr(
            getattr(torch, "_C", None), "_cuda_getDriverVersion", lambda: None)()
    except Exception:
        pass
    return out


def log(m):
    print(m, flush=True)


def prompt_for(frame, text, tok):
    body = MF.render(frame, text)
    if frame["wrap"] != "chat":
        return body, "raw"
    if getattr(tok, "chat_template", None) in (None, ""):
        return None, "NO_CHAT_TEMPLATE"
    msgs = ([{"role": "system", "content": frame["system"]}] if frame.get("system")
            else []) + [{"role": "user", "content": body}]
    # ── enable_thinking=False ON EVERY CHAT RENDER (Cassian, 2026-09-30) ─────
    # Qwen3's DEFAULT template opens a reasoning block, so a teacher-forced read at the
    # answer position scores NOTHING: answer mass 0.000, twice. The API arms that
    # passed the gate were served with thinking disabled, which is the non-thinking
    # read the plan means by "chat frame". Templates that do not use the flag ignore
    # it, so llama's render is byte-identical and nothing already banked moves.
    def _apply(m):
        try:
            return tok.apply_chat_template(m, tokenize=False,
                                           add_generation_prompt=True,
                                           enable_thinking=False)
        except TypeError:
            return tok.apply_chat_template(m, tokenize=False,
                                           add_generation_prompt=True)
    try:
        return _apply(msgs), "chat"
    except Exception:
        # ── SOME TEMPLATES REFUSE A SYSTEM ROLE, AND GEMMA'S RAISES ON IT ────
        # gemma-2-9b-it and gemma-2-27b-it carry a literal
        # raise_exception("System role not supported"). Folding the instruction to the
        # top of the USER turn is the only way to ask them at all, and it is how
        # anyone deploying Gemma asks. **IT CHANGES THE PROMPT**, so it is RECORDED on
        # the cell rather than hidden: a gemma chat cell is not byte-comparable with
        # an arm carrying a real system turn. Every other arm is untouched.
        sysmsg = frame.get("system") or ""
        folded = [{"role": "user", "content": (sysmsg + "\n\n" + body).strip()}]
        return _apply(folded), "chat_system_folded"


def read_cell(tok, model, frame, text, depths=False):
    p, wrap = prompt_for(frame, text, tok)
    if p is None:
        return {"void": True, "void_reason": wrap}
    answers = frame["answers"]
    digits = frame["scale"] is not None
    # ── THE ANSWER PREFIX IS RESOLVED PER TEMPLATE, NOT FIXED IN THE FRAME ────
    # `answer_ids` warns that the prefix belongs to the FRAME and that scoring the
    # wrong one "reads a string the model will never emit". I hard-coded one prefix for
    # every chat template and walked into exactly that: Mistral's `[/INST]` continues
    # with a LEADING SPACE, so the emitted token is " 0" and not "0". Scoring "" gave
    # answer_mass 7e-08 and N 2.981; scoring " " gives mass 0.9995 and N 0.034. The
    # arm was fully readable and was banked as dead.
    # **THE DECLARED PREFIX IS ALWAYS TRIED FIRST AND KEPT IF IT WORKS**, so every cell
    # already banked with good mass is byte-identical. Alternatives are only reached
    # when the declared one carries almost no mass, which is the signature of scoring a
    # string the model cannot emit.
    declared = frame["answer_prefix"]
    tried = {}
    best = None
    for cand in [declared] + [x for x in (" ", "", "\n") if x != declared]:
        aid, fid = MODEL.answer_ids(tok, answers, cand, prompt=p)
        sc = MODEL.score(tok, model, p, answers, ans_ids=aid, first_ids=fid,
                         prefix=cand, values=None if digits else False,
                         depths=depths if cand == declared else None)
        tried[repr(cand)] = round(sc["answer_mass"], 6)
        if best is None or sc["answer_mass"] > best[1]["answer_mass"]:
            best = (cand, sc)
        if sc["answer_mass"] >= PREFIX_OK:      # the declared one works: stop here
            break
    prefix_used, s = best
    if prefix_used != declared and depths:
        aid, fid = MODEL.answer_ids(tok, answers, prefix_used, prompt=p)
        s = MODEL.score(tok, model, p, answers, ans_ids=aid, first_ids=fid,
                        prefix=prefix_used, values=None if digits else False,
                        depths=depths)
    out = {"void": False, "wrap": wrap, "prompt_sha256_16": hashlib.sha256(
               p.encode()).hexdigest()[:16],
           "system_folded_into_user": wrap == "chat_system_folded",
           "answer_prefix_declared": declared, "answer_prefix_used": prefix_used,
           "answer_mass_by_prefix": tried,
           "dist_norm": s["dist_norm"], "answer_mass": s["answer_mass"],
           "entropy": s["entropy"], "argmax_norm": s["argmax_norm"],
           "ev": s["mean_norm"] if digits else None,
           # p_yes IS GUARDED ON "Yes" BEING AN ANSWER, not merely on the frame not
           # being digits. Added 2026-10-05: local_frames's CMP3 frame answers
           # {EQUALLY, HOME, CHEF}, which is neither digits nor yes/no, and
           # answers.index("Yes") raised ValueError on a three-way set. p_yes is
           # meaningless for such a frame, so None is the right value rather than a
           # crash or a silently wrong index.
           "p_yes": (s["dist_norm"][answers.index("Yes")]
                     if (not digits and "Yes" in answers) else None),
           "n_prompt_tokens": s["n_prompt_tokens"], "top5": s["top5"]}
    if depths:
        out["acts"] = s["acts"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    # ── --bank AND --families, ADDED 2026-10-05 FOR local_frames. BOTH DEFAULT TO THE
    # local_tuning BEHAVIOUR, so every local_tuning invocation is bit-identical and its banked
    # artefacts stay reproducible from this script. --families exists so the 52-row
    # families bank is read on ONE load per checkpoint rather than one per family:
    # the loads dominate inference 34.5 min to 7.2, so five loads per checkpoint would
    # be an earlier run's cost-per-cell defect in a new place.
    ap.add_argument("--bank", default=BANK,
                    help="bank jsonl, relative to the repo root. Default is local_tuning's "
                         "ten bicycle rows; local_frames passes the 52-row families bank.")
    ap.add_argument("--families", default=None,
                    help="comma list. Only for a bank whose rows carry a `family` field: "
                         "each family is read as its own artefact off the SAME load, and "
                         "its roles are indexed by role rather than by uid.")
    ap.add_argument("--run", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--spec", default="cuda:bfloat16")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--expect-digest", default=None)
    ap.add_argument("--delivery", required=True,
                    help="completion, chat, or a comma-separated list. The model is "
                         "loaded ONCE and every delivery is read off that load.")
    ap.add_argument("--gate-mean", type=float, default=1.05)
    ap.add_argument("--gate-i", type=float, default=7.0)
    ap.add_argument("--gate-mass", type=float, default=0.70)
    ap.add_argument("--harvest", action="store_true")
    # ── READ THE BATTERY THROUGH A FAILED GATE, ON AN EXPLICIT FLAG ──────────
    # Cassian, 2026-09-30, HALT 2. The gate's thresholds (N <= 1.05, I >= 7) were set
    # from CHAT and API arms and have never been calibrated on the named COMPLETION
    # frame, which is the frame the pod exists for. llama31_base reads N 1.739 and
    # I 6.818 there, and under the plain rule it yields no battery, so whether that is
    # a real floor failure or ordinary completion-frame behaviour cannot be decided.
    # **THIS CHANGES NO THRESHOLD.** The gate is computed and its verdict is carried
    # on the artefact exactly as before; only the early exit is suspended, and the
    # artefact records that it was.
    ap.add_argument("--extra-frames", default=None,
                    help="a second frame file appended to the delivery's frames, so a "
                         "DIRECTIONAL arm can be re-read on TEN permutations. A range "
                         "over five draws is itself a noisy estimate of the band.")
    ap.add_argument("--read-through-gate", action="store_true",
                    help="run the battery even on a FAILED gate. The verdict is still "
                         "computed and banked; no threshold moves.")
    ap.add_argument("--trust-remote-code", action="store_true")
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="gpt2 on CPU: exercises every path, reads nothing real")
    a = ap.parse_args(argv)
    model_id = "gpt2" if a.dry_run else a.model
    spec = "cpu:float32" if a.dry_run else a.spec
    deliveries = [d.strip() for d in a.delivery.split(",") if d.strip()]
    bad = [d for d in deliveries if d not in ("completion", "chat")]
    if bad:
        sys.exit(f"REFUSING: unknown delivery {bad}")
    bank_rows = bank_lock.load(f"{R}/{a.bank}")
    # A BANK WITH A `family` FIELD IS INDEXED BY ROLE, NOT BY UID. The bicycle bank's
    # uid IS the role ("N", "C"); the families bank's is "ladder__N". Everything
    # downstream looks up rows["P0"], so the family view maps role -> row and the
    # existing code is untouched.
    if a.families:
        want = [f.strip() for f in a.families.split(",") if f.strip()]
        have = sorted({r.get("family") for r in bank_rows if r.get("family")})
        if not have:
            sys.exit(f"REFUSING: --families given but no row of {a.bank} carries a "
                     f"`family` field")
        missing = [f for f in want if f not in have]
        if missing:
            sys.exit(f"REFUSING: families {missing} are not in {a.bank}; it has {have}")
        views = [(f, {r["role"]: r for r in bank_rows if r.get("family") == f})
                 for f in want]
    else:
        views = [(None, {r["uid"]: r for r in bank_rows})]
    allf = json.load(open(f"{R}/{FRAMES}"))
    todo = []
    for d in deliveries:
      for fam, frows in views:
        tag = f"pod216__{a.arm}__{d}" if fam is None else f"pod223__{a.arm}__{fam}__{d}"
        dest = f"{R}/runs/{a.run}/results/{tag}.json"
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.exists(dest):
            log(f"   {d}{'' if fam is None else '/'+fam}: already banked, skipping")
            continue
        fr = [f for f in allf if f["delivery"] == d]
        if a.extra_frames:
            fr += [f for f in json.load(open(f"{R}/{a.extra_frames}"))
                   if f["delivery"] == d]
        if not fr:
            sys.exit(f"REFUSING: no {d} frames in {FRAMES}")
        todo.append((d, dest, fr, fam, frows))
    if not todo:
        log("   nothing to do; every delivery is banked")
        return 0
    log(f"== RATE  arm {a.arm}  cells {[(d, f) for d,_,_,f,_ in todo]}  "
        f"bank {a.bank}  ONE LOAD")
    t0 = time.time()
    tok, model, meta = MODEL.load(model_id, spec, threads=a.threads,
                                  adapter=a.adapter,
                                  trust_remote_code=a.trust_remote_code)
    log(f"   loaded in {time.time()-t0:.1f}s  {meta}")
    if a.expect_digest and meta.get("adapter_digest") not in (None, a.expect_digest):
        sys.exit(f"REFUSING: adapter digest {meta.get('adapter_digest')} != "
                 f"{a.expect_digest}")

    load_s = round(time.time() - t0, 1)
    rc = 0
    for delivery, dest, frames, family, rows in todo:
      t_d = time.time()
      log(f"-- delivery {delivery}: {len(frames)} frames")
      out = {"run": a.run, "arm": a.arm, "model": model_id, "spec": spec,
           "delivery": delivery, "adapter": a.adapter, "model_meta": meta,
           # ── THE ENVIRONMENT IS RECORDED IN EVERY ARTEFACT ────────────────
           # Ruled by Cassian 2026-10-05. local_tuning's artefacts carry model_meta with
           # device and dtype but no library versions, so a reading could not be tied
           # to the numerics that produced it. This run deliberately matches local_tuning's
           # torch (2.8.0+cu128, from an earlier run's manifest) because IDENTICAL NUMERICS
           # are what make the bicycle reproduction check mean anything; a figure that
           # is not recorded cannot be checked later.
           "environment": _env(),
           "load_seconds": load_s,
           "load_shared_with": [(d, f) for d, _, _, f, _ in todo],
           "family": family, "n_rows": len(rows),
           "bank": a.bank, "frames_file": FRAMES,
           "bank_sha256": hashlib.sha256(
               open(f"{R}/{a.bank}", "rb").read()).hexdigest(),
           "frames_sha256": hashlib.sha256(
               open(f"{R}/{FRAMES}", "rb").read()).hexdigest(),
           "gates_used": {"N_mean_max": a.gate_mean, "N_mean_default": 1.05,
                          "I_min": a.gate_i, "answer_mass_min": a.gate_mass,
                          "enforced": not a.dry_run},
           "dry_run": a.dry_run, "cells": {}, "stages": {}}

      # ── (a) DETERMINISM: two passes, identical logits ────────────────────────
      f0 = frames[0]
      d1 = read_cell(tok, model, f0, rows["P0"]["text"])
      # A VOID CELL IS NOT A DETERMINISM FAILURE, AND CALLING IT ONE WOULD BE AN
      # INSTRUMENT FAULT PRESENTING AS A SPECIMEN FAULT. A base arm has no chat
      # template, so the chat delivery cannot be honoured there; the plan requires that
      # be RECORDED rather than silently downgraded to raw, and it must also not be
      # mislabelled as the model giving two different answers to one prompt.
      if d1["void"]:
          out["stages"]["determinism"] = {"passed": None, "frame": f0["id"],
                                          "row": "P0", "not_run_why": d1["void_reason"]}
          out["stopped_at"] = d1["void_reason"].lower()
          log(f"   (a) determinism NOT RUN: {d1['void_reason']}")
          log(f"       this delivery is unavailable on this arm. Recorded, not downgraded.")
          json.dump(out, open(dest, "w"), indent=1)
          log(f"   -> {dest}")
          continue
      d2 = read_cell(tok, model, f0, rows["P0"]["text"])
      same = (not d2["void"] and d1["dist_norm"] == d2["dist_norm"])
      out["stages"]["determinism"] = {"passed": bool(same), "frame": f0["id"],
                                      "row": "P0",
                                      "rule": "two forward passes, identical logits"}
      log(f"   (a) determinism  {'PASS' if same else 'FAIL'}")
      if not same:
          out["stopped_at"] = "determinism"
          json.dump(out, open(dest, "w"), indent=1)
          log(f"   STOPPING. -> {dest}")
          continue

      # ── COMPLETION READS THE BATTERY FIRST, BECAUSE ITS GATE NEEDS THE BAND ──
      # The band comes from the five exemplar permutations, so it does not exist until
      # the battery is read. The battery is ~20 s against a 100-214 s load, so reading
      # it first costs almost nothing and is the only order in which a band-relative
      # gate can be computed at all.
      # ── (b) GATES, on the delivery's BLAME frame ─────────────────────────────
      gf = next(f for f in frames if f["channel"] == "BLAME")
      band_gate = (delivery == "completion")
      if band_gate:
          # read EVERYTHING first; the band is a property of the battery
          for f in frames:
              for uid in [u for u in ROWS_PRESENT(rows)]:
                  k = f"{uid}|{f['channel']}|{f['id']}"
                  if k not in out["cells"]:
                      out["cells"][k] = read_cell(tok, model, f, rows[uid]["text"])
          log(f"   (c) battery read first ({len(frames)} frames) so the band exists")
      gate = {}
      for uid in ("N", "I"):
          k = f"{uid}|BLAME|{gf['id']}"
          c = out["cells"].get(k) or read_cell(tok, model, gf, rows[uid]["text"])
          out["cells"][k] = c
          gate[uid] = c
      if gate["N"]["void"] or gate["I"]["void"]:
          out["stages"]["gates"] = {"passed": False,
                                    "why": gate["N"].get("void_reason")
                                    or gate["I"].get("void_reason")}
          out["stopped_at"] = "gates_void"
          json.dump(out, open(dest, "w"), indent=1)
          log(f"   (b) gates VOID ({out['stages']['gates']['why']}) -> {dest}")
          continue
      n_ev, i_ev = gate["N"]["ev"], gate["I"]["ev"]
      low = sum(gate["N"]["dist_norm"][:4])
      mass = min(gate["N"]["answer_mass"], gate["I"]["answer_mass"])
      # ── THE GATE STAYS AT 1.05. A NEAR MISS IS READ ANYWAY AND BANKED AS ONE ──
      # Cassian, 2026-09-30. The gate decides what enters the table and keeps doing
      # that unchanged. But if the instruct arms turn out to sit at 1.05-1.25 AS A
      # CLASS, the threshold deserves re-examining with all seven arms' figures in
      # hand, and by then the checkpoints are evicted: re-loading seven models to
      # recover batteries that could have been read in the same load is the expensive
      # version of this. So an arm that misses N by less than 0.25 and passes every
      # OTHER component is read in full and banked FAILED_NEAR_MISS.
      # **IT ENTERS NO TABLE.** The verdict is carried on the artefact so nothing
      # downstream can mistake it for a pass, and the gate has not been lowered.
      if band_gate:
          import statistics as _st
          def _mean(uid):
              v = [c["ev"] for k, c in out["cells"].items()
                   if k.startswith(f"{uid}|BLAME|") and not c.get("void")]
              return _st.mean(v) if v else None
          def _sdband(uid):
              v = [c["ev"] for k, c in out["cells"].items()
                   if k.startswith(f"{uid}|BLAME|") and not c.get("void")]
              return (_st.pstdev(v) * BAND_SD_K) if len(v) > 1 else None
          def _range(uid):
              v = [c["ev"] for k, c in out["cells"].items()
                   if k.startswith(f"{uid}|BLAME|") and not c.get("void")]
              return (max(v) - min(v)) if len(v) > 1 else None
          bands = [r for r in (_sdband(u) for u in ("P0", "P1", "BYSTANDER"))
                   if r is not None]
          band = _st.mean(bands) if bands else None
          rbands = [r for r in (_range(u) for u in ("P0", "P1", "BYSTANDER"))
                    if r is not None]
          band_range = _st.mean(rbands) if rbands else None
          n_perm = len([1 for k in out["cells"] if k.startswith("P0|BLAME|")])
          p0, c_ev = _mean("P0"), _mean("C")
          n_gap = (p0 - n_ev) / band if (band and p0 is not None) else None
          i_gap = (i_ev - c_ev) / band if (band and c_ev is not None) else None
          # ── THE CEILING IS A CHECK ON THE INSTRUMENT'S TOP, NOT ON THE QUANTITY ──
          # Every P-row is read as (X - N) / (C - N), so the scale the finding depends
          # on runs from N to C. `I` never enters a position: it is a sanity check that
          # the top of the scale exists. A ceiling that is soft relative to the band
          # says the arm is noisy up there, which is worth REPORTING, but it does not
          # touch the quantity Q1 is about. So DIRECTIONAL is assessed on the FLOOR and
          # on C being separated from N, with the ceiling printed beside it either way.
          # (Cassian, 2026-09-30, on qwen3_base: floor 2.24 bands, ceiling 1.46.)
          c_gap = (c_ev - n_ev) / band if (band and c_ev is not None) else None
          scale_ok = (low >= 0.8 and mass >= a.gate_mass
                      and c_gap is not None and c_gap >= BANDS_N_FLOOR)
          ceiling_ok = (i_gap is not None and i_gap >= BANDS_I_CEIL)
          others_ok = scale_ok and ceiling_ok
          passed = (others_ok and n_gap is not None and n_gap >= BANDS_N_FLOOR)
          directional = (scale_ok and not passed and n_gap is not None
                         and n_gap >= BANDS_N_DIRECTIONAL)
          out["stages"]["band_gate"] = {
              "band": band, "band_definition": f"{BAND_SD_K} x sd over P0, P1, "
                  f"BYSTANDER; sd is stable in n where the RANGE is not",
              "band_as_range_for_reference": band_range, "n_permutations": n_perm,
              "P0_minus_N_in_bands": n_gap,
              "C_minus_N_in_bands": c_gap,
              "I_minus_C_in_bands": i_gap,
              # ── THE THREE FIELDS ABOVE MIX A FRAME WITH A MEAN. DEPRECATED. ─────
              # `n_ev` is the GATE frame's N and `p0`/`c_ev` are MEANS over the
              # permutation frames, so the ratios above difference a single-frame N
              # against a mean. gate_one_construction.json named this on
              # 2026-09-30 ("1.58 as the instrument banked it") and is the authority
              # for every paper figure. They are KEPT so existing readers do not
              # break, and the ruled values are banked beside them.
              "DEPRECATED_above_three_mix_frame1_N_with_mean_P0": True,
              "schema_note": "records/ARTEFACT_SCHEMA_NOTE_bands_v2.json",
              "P0_minus_N_in_bands_RULED": ((p0 - _mean("N")) / band
                                            if band and p0 is not None
                                            and _mean("N") is not None else None),
              "C_minus_N_in_bands_RULED": ((c_ev - _mean("N")) / band
                                           if band and c_ev is not None
                                           and _mean("N") is not None else None),
              # AND THE BAND IN POSITION UNITS, because `band` is in DIGITS and a
              # position difference divided by it understates the difference by the
              # N-to-C span (Cassian, 2026-10-02: 0.313 bands reported as 0.091).
              "band_in_position_units": ((band / (c_ev - _mean("N")))
                                         if band and c_ev is not None
                                         and _mean("N") is not None
                                         and abs(c_ev - _mean("N")) > 1e-9 else None),
              "N_to_C_digits": ((c_ev - _mean("N")) if c_ev is not None
                                and _mean("N") is not None else None),
              "ceiling_ok": bool(ceiling_ok),
              "ceiling_note": "reported beside the tier whether it passes or not; it "
                              "is a check on the instrument's top and never enters a "
                              "position, which is always (X - N) / (C - N)",
              "rule": f"N floor: mass(0-3) >= 0.8 AND (P0-N) >= {BANDS_N_FLOOR} bands; "
                      f"I ceiling: (I-C) >= {BANDS_I_CEIL} bands; answer mass >= "
                      f"{a.gate_mass}",
              "why": "the fixed digits were set on chat and API arms and never "
                     "calibrated for a worksheet read by a base model (HALT 2)",
              "tiers": {
                  "LICENSED": f"(P0-N) >= {BANDS_N_FLOOR} bands AND (C-N) >= "
                              f"{BANDS_N_FLOOR} AND (I-C) >= {BANDS_I_CEIL}, mass and "
                              f"answer mass passing; headline tables and the Q1 count",
                  "DIRECTIONAL": f"(P0-N) >= {BANDS_N_DIRECTIONAL} bands AND (C-N) >= "
                                 f"{BANDS_N_FLOOR}, mass and answer mass passing; the "
                                 f"ceiling reported beside it either way. SECOND table "
                                 f"only, band as the error bar, NEVER the headline",
                  "FAILED": f"floor below {BANDS_N_DIRECTIONAL} bands, or C not "
                            f"separated from N by {BANDS_N_FLOOR} bands, or mass / "
                            f"answer mass failing"},
              "directional": bool(directional)}
      else:
          others_ok = (low >= 0.8 and i_ev >= a.gate_i and mass >= a.gate_mass)
          passed = (n_ev <= a.gate_mean and others_ok)
          directional = False
      near_miss = (not passed and others_ok and not band_gate
                   and n_ev <= a.gate_mean + NEAR_MISS_N)
      verdict = ("LICENSED" if (passed and band_gate)
                 else ("PASSED" if passed
                       else ("DIRECTIONAL" if directional
                             else ("FAILED_NEAR_MISS" if near_miss else "FAILED"))))
      # ── THE GATE IS ENFORCED ON EVERY REAL ARM, AND CANNOT BE TURNED OFF ─────
      # `--dry-run` forces gpt2 on CPU, so the gate result there is meaningless and
      # enforcing it would leave stages (c), (d) and (f) permanently untested: a gate
      # that refuses needs a test that it OPENS. So the dry run RECORDS the gate and
      # does not enforce it, and `gates_enforced` goes in the artefact.
      # **THERE IS NO FLAG THAT DOES THIS ON A REAL CHECKPOINT.** The exemption is tied
      # to --dry-run, which pins model_id to gpt2 and spec to cpu:float32 a few lines
      # above, so no candidate arm can reach it.
      enforced = not a.dry_run
      out["stages"]["gates"] = {"passed": bool(passed), "verdict": verdict,
                                "near_miss": bool(near_miss),
                                "N_miss_by": round(max(0.0, n_ev - a.gate_mean), 4),
                                "near_miss_rule": f"N misses by < {NEAR_MISS_N} and "
                                    f"every other component passes; read in full, "
                                    f"banked, ENTERS NO TABLE",
                                "N_ev": n_ev,
                                "N_mass_0_3": low, "I_ev": i_ev,
                                "min_answer_mass": mass, "enforced": enforced,
                                "battery_read_despite_verdict": bool(a.read_through_gate),
                                "rule": f"N <= {a.gate_mean} and mass(0-3) >= 0.8 and "
                                        f"I >= {a.gate_i} and answer mass >= {a.gate_mass}",
                                "not_enforced_why": (None if enforced else
                                    "DRY RUN on gpt2/CPU. The gate was computed and is "
                                    "reported; it is not a reading and nothing downstream "
                                    "of it is either.")}
      log(f"   (b) gates  N {n_ev:.3f} mass(0-3) {low:.3f}  I {i_ev:.3f}  "
          f"answer mass {mass:.3f}  -> {verdict}"
          + (f"  (N misses by {n_ev - a.gate_mean:+.3f}; battery read anyway, "
             f"enters no table)" if near_miss else "")
          + ("" if enforced else "  (NOT ENFORCED: dry run)"))
      out["battery_read_through_gate"] = bool(a.read_through_gate)
      if verdict in ("FAILED",) and enforced and not a.read_through_gate:
          out["stopped_at"] = "gates"
          out["verdict"] = verdict
          json.dump(out, open(dest, "w"), indent=1)
          log(f"   BANKED AS FAILED, threshold NOT lowered. -> {dest}")
          continue

      # ── (c)/(d) THE BATTERY ──────────────────────────────────────────────────
      for f in frames:
          for uid in LADDER + ["C"]:
              k = f"{uid}|{f['channel']}|{f['id']}"
              if k in out["cells"]:
                  continue
              out["cells"][k] = read_cell(tok, model, f, rows[uid]["text"])
          log(f"   ({'c' if delivery=='completion' else 'd'}) {f['id']} done")

      # ── (f) HARVEST: final-token residual stream, EVERY layer ────────────────
      # §4f. Written as .npy because `score` returns numpy arrays, with the size
      # PREDICTED FROM THE SHAPE AND ASSERTED against the bytes on disk, and with the
      # prompts asserted DISTINCT: an activation set whose contexts are identical is
      # one context banked n times (an earlier run's §4 lesson, where extract.py would have
      # banked five copies of one bare-text state under four frame labels).
      if a.harvest:
          import numpy as np
          hdir = f"{R}/runs/{a.run}/acts"
          os.makedirs(hdir, exist_ok=True)
          nlayer = int(getattr(model.config, "num_hidden_layers", 0)) + 1
          depths = list(range(nlayer))
          hv = {}
          for ch in HARVEST_CHANNELS:
              f = next((x for x in frames if x["channel"] == ch), None)
              if f is None:
                  hv[ch] = {"skipped": f"{ch} is not a {delivery} channel"}
                  continue
              vecs, shas, uids = [], set(), []
              for uid in LADDER:
                  pr, wrap = prompt_for(f, rows[uid]["text"], tok)
                  if pr is None:
                      continue
                  aid, fid = MODEL.answer_ids(tok, f["answers"],
                                              f["answer_prefix"], prompt=pr)
                  sc = MODEL.score(tok, model, pr, f["answers"], ans_ids=aid,
                                   first_ids=fid, prefix=f["answer_prefix"],
                                   values=None if f["scale"] is not None else False,
                                   depths=depths)
                  vecs.append(np.stack([sc["acts"][d]["last"] for d in depths]))
                  shas.add(hashlib.sha256(pr.encode()).hexdigest())
                  uids.append(uid)
              if not vecs:
                  hv[ch] = {"skipped": "no row rendered"}
                  continue
              arr = np.stack(vecs).astype("float32")      # (rows, layers, hidden)
              # THE HARVEST PATH MUST CARRY THE FAMILY, AND IT DID NOT. Found on the
              # live card 2026-10-05: I made the RESULTS path family-aware when I added
              # --families and left this one alone, so every family after the first hit
              # `write-once: ...pod216__llama31_adapter__completion__BLAME.npy exists`
              # and the arm exited 1. Two of twelve cells banked and the batch carried
              # on, because "banked if the stage wrote" is true and uninformative: five
              # sixths of the work was being lost per arm with a non-zero exit nobody
              # was gating on. Write-once did its job; the name was wrong.
              tag = (f"pod216__{a.arm}__{delivery}" if family is None
                     else f"pod223__{a.arm}__{family}__{delivery}")
              path = f"{hdir}/{tag}__{ch}.npy"
              if os.path.exists(path):
                  sys.exit(f"write-once: {path} exists")
              predicted = int(arr.size) * 4 + 128         # +header allowance
              np.save(path, arr)
              actual = os.path.getsize(path)
              size_ok = abs(actual - predicted) <= 128
              distinct = len(shas) == len(uids)
              hv[ch] = {"path": os.path.relpath(path, R), "shape": list(arr.shape),
                        "n_rows": len(uids), "rows": uids, "layers": nlayer,
                        "predicted_bytes": predicted, "actual_bytes": actual,
                        "size_assert_passed": bool(size_ok),
                        "contexts_distinct": bool(distinct),
                        "n_distinct_prompts": len(shas)}
              if not (size_ok and distinct):
                  sys.exit(f"REFUSING: harvest {ch} size_ok={size_ok} "
                           f"distinct={distinct} ({len(shas)} of {len(uids)})")
          out["stages"]["harvest"] = hv
          for ch, v in hv.items():
              log(f"   (f) harvest {ch}: {v}")

      # ── POSITIONS AGAINST BYSTANDER AS WELL AS N (Cassian, HALT 2) ──────────
      # BYSTANDER is not 0 on the completion frame: it reads 0.13 to 0.23 of the N-to-C
      # interval and DESCENDS with tuning, so it is the frame giving a named but
      # uninvolved person a raised floor when harm is present, not a wording defect.
      # That makes it the honest "harm happened, he wasn't involved" baseline, and
      # **P0 - BYSTANDER is the cleanest statement of blame for INVOLVEMENT.**
      if delivery == "completion":
          import statistics as _st2
          def _m(uid):
              v = [c["ev"] for k, c in out["cells"].items()
                   if k.startswith(f"{uid}|BLAME|") and not c.get("void")]
              return _st2.mean(v) if v else None
          n_, c_, b_ = _m("N"), _m("C"), _m("BYSTANDER")
          if None not in (n_, c_, b_) and abs(c_ - n_) > 1e-9:
              out["positions"] = {
                  u: {"raw": _m(u),
                      "vs_N": (_m(u) - n_) / (c_ - n_),
                      "vs_BYSTANDER": ((_m(u) - b_) / (c_ - b_)
                                       if abs(c_ - b_) > 1e-9 else None),
                      "minus_BYSTANDER": (_m(u) - b_)}
                  for u in ROWS_PRESENT(rows) if _m(u) is not None}
              out["positions_note"] = (
                  "vs_N is the standing form. vs_BYSTANDER is added at HALT 2 because "
                  "BYSTANDER is not 0 on this frame; P0 minus BYSTANDER is blame for "
                  "INVOLVEMENT with the harm-present floor removed.")
      out["stopped_at"] = None
      out["verdict"] = verdict
      out["elapsed_s"] = round(time.time() - t0, 1)
      json.dump(out, open(dest, "w"), indent=1)
      log(f"   -> {dest}  (delivery {round(time.time()-t_d,1)}s, load {load_s}s shared)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

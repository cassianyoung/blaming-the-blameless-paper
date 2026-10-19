#!/usr/bin/env python3
"""read_v11_syllogism.py : the v1.1 fill's H7 and H8 readings (completeness_fill_amendment).

    python3 scripts/read_v11_syllogism.py --check-only            # no key, no call
    python3 scripts/read_v11_syllogism.py --completeness_fill --arm gpt4o   # one arm, on the wire

The prompts and wires are frozen in records/v11_frames.json (built by
build_v11_syllogism_frames.py, sha pinned below). Per arm:

  H7 (run syllogism_duty's 13 reasoning-off arms): prawns A, R and B exactly as syllogism_duty read the
     other pairs: A in the arm's banked readout (log-prob P(yes) or sampled yes/no), R on
     the wire behind the arm's banked bare cells, B sampled (log-prob arms at 32 tokens),
     reasoning off.
  H8 (the six reasoning arms and Gemini 3.1 Pro), a separate stratum: run syllogism_duty's A, R and B
     on all six pairs and run general_principle's five prompts, each on the arm's banked duty_separate
     wire, the registered setting; R on the banked bare wire. Gemini 3.1 Pro adds reasoning_traces's
     trace re-read, the bare case on its banked wire with the text kept.

**THE ONLY DEPARTURE FROM THE BANKED READERS IS THE WIRE.** read_syllogism_duty.py and
read_general_principle.py send A, B and G with reasoning off on every arm; on a reasoning arm that
would repeat the reasoning-off reading, so here the reasoning arms send their banked
reasoning wire. Parsing is the banked readers' (parse_yn and lp_yn, parse_b, parse_g1 and
parse_g3, duty_pairs's digit), and the refusals are theirs: the frames file must hash to its
pinned sha; every message is rebuilt and hashed before any call; a call whose logged
prompt hash is not the frozen one stops the read; a provider other than the banked one,
or more than one per arm, makes the arm UNREAD.
"""
import argparse, hashlib, json, os, sys, time

R = os.environ.get("AI_ETHICS_ROOT") or os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
from run_rivals import parse_yn, lp_yn
from read_prevention_paraphrase import Unread, msgs_hash
from read_syllogism_duty import parse_b
from read_general_principle import parse_g1, parse_g3

FRAMES = "records/v11_frames.json"
FRAMES_SHA_FILE = "records/v11_frames.sha256"
G_KEYS = ("G1", "G1_AP", "G2", "G3_PA", "G3_AP")
LEGS = ("PRO", "PRIV")


def load_frames():
    blob = open(f"{R}/{FRAMES}", "rb").read()
    want = open(f"{R}/{FRAMES_SHA_FILE}").read().split()[0]
    if hashlib.sha256(blob).hexdigest() != want:
        sys.exit(f"REFUSING: {FRAMES} does not hash to its pinned sha")
    return json.loads(blob)


def messages(p):
    return [{"role": "system", "content": p["system"]}, {"role": "user", "content": p["user"]}]


def plan(frames, arm):
    """[(label, key, kind, messages, prompt16, call settings, draws)] for one arm, every
    message rebuilt and hashed against the frozen prompt before anything is returned."""
    a = frames["arms"][arm]
    ab, n = a["AB"], a["draws"]
    on = a["group"] == "H8"
    out = []

    def add(key, kind, settings, draws, tag=None):
        p = frames["prompts"][key]
        m = messages(p)
        if msgs_hash(m) != p["prompt_sha256"]:
            sys.exit(f"REFUSING: {arm} {key}: rebuilt prompt does not hash to the frozen one")
        out.append((f"v11|{arm}|{tag or kind}|{key}", key, kind, m, p["prompt_sha256"][:16],
                    settings, draws))

    def ab_settings(kind):
        if on:
            return {"model": ab["model"], "provider": ab["provider"],
                    "max_tokens": ab["max_tokens"], "temperature": ab["temperature"],
                    "want_logprobs": False, "reasoning": (None if ab["reasoning"] ==
                                                          "vendor_default" else ab["reasoning"])}
        logp = ab["readout"] == "logprob"
        return {"model": ab["model"], "provider": ab["provider"],
                "max_tokens": ab["max_tokens_B"] if kind in ("B", "G") else ab["max_tokens"],
                "temperature": 1.0, "want_logprobs": logp and kind == "A",
                "top_k": ab.get("top_k") or 20, "reasoning": {"enabled": False}}

    for pr in a["pairs"]:
        add(f"A|p{pr}", "A", ab_settings("A"), n)
        for L in LEGS:
            w = a["R"][f"R|p{pr}|{L}"]
            add(f"R|p{pr}|{L}", "R", {"model": w["model"], "provider": w["provider"],
                                      "max_tokens": w["max_tokens"],
                                      "temperature": w["temperature"],
                                      "want_logprobs": w["want_logprobs"],
                                      "top_k": w.get("top_k") or 20,
                                      "reasoning": w["reasoning"]}, n)
        for L in LEGS:
            add(f"B|p{pr}|{L}", "B", ab_settings("B"), n)
    if on:
        for g in G_KEYS:
            add(f"G|{g}", "G", ab_settings("G"), n)
    if arm == "gemini_pro":                     # reasoning_traces's trace re-read
        for pr in a["pairs"]:
            for L in LEGS:
                w = a["R"][f"R|p{pr}|{L}"]
                add(f"R|p{pr}|{L}", "T230", {"model": w["model"], "provider": w["provider"],
                                             "max_tokens": w["max_tokens"],
                                             "temperature": w["temperature"],
                                             "want_logprobs": False,
                                             "reasoning": w["reasoning"]}, n, tag="T230")
    return out


def score(kind, key, x):
    txt = x.get("answer_text", x.get("raw_text"))
    rec = {"text": txt, "reasoned": bool(x.get("reasoning_text_len")),
           "reasoning_text_len": x.get("reasoning_text_len")}
    if kind == "A":
        if x.get("top_tokens"):
            py, mass = lp_yn(x)
            rec.update({"p_yes": py, "mass": mass})
        rec["answer"] = parse_yn(txt)
    elif kind in ("R", "T230"):
        if x.get("ev") is not None:
            rec["digit"] = float(x["ev"])
        else:
            import re
            m = re.search(r"\d", txt or "")
            rec["digit"] = float(m.group(0)) if m else None
    elif kind == "B":
        rec["parsed"] = parse_b(txt)
    elif key in ("G|G1", "G|G1_AP"):
        rec["parsed"] = parse_g1(txt)
    elif key == "G|G2":
        rec["parsed"] = parse_yn(txt)
    else:
        rec["parsed"] = parse_g3(txt)
    return rec


def check_only(frames):
    n_calls, rows = 0, []
    for arm in frames["arms"]:
        p = plan(frames, arm)
        calls = sum(x[6] for x in p)
        n_calls += calls
        rows.append((arm, frames["arms"][arm]["group"], len(p), calls))
    for r in rows:
        print(f"  {r[0]:11s} {r[1]}  {r[2]:3d} cells  {r[3]:4d} calls")
    print(f"check-only: {sum(r[2] for r in rows)} cells, {n_calls} calls; every prompt "
          f"rebuilt and equal to its frozen hash; nothing sent")


def read(frames, arm, run, cap, deadline=None, wait=60):
    from or_harness import Harness
    out_path = f"{R}/records/RUN{run}_V11_SYLL__{arm}.json"
    if os.path.exists(out_path):
        sys.exit(f"write-once: {out_path} exists")
    p = plan(frames, arm)                                   # refusals before any call
    os.makedirs(f"{R}/runs/run{run}/logs", exist_ok=True)
    h = Harness(f"{R}/runs/run{run}/logs/or_{arm}.jsonl", cap_usd=cap)
    served, models, cells = set(), set(), {}
    for label, key, kind, m, want16, s, draws in p:
        recs = []
        for d in range(draws):
            while True:
                try:
                    x = h.rate(s["model"], s["provider"], messages=m, mode="chat",
                               temperature=s["temperature"], max_tokens=s["max_tokens"],
                               top_k=s.get("top_k") or 20, want_logprobs=s["want_logprobs"],
                               reasoning=s["reasoning"], label=f"{label}|d{d}")
                except RuntimeError as e:
                    if deadline and time.time() > deadline:
                        raise Unread(f"provider still failing at the deadline: {e}")
                    time.sleep(wait)
                    continue
                if x.get("provider_served") is None and not (x.get("raw_text") or "").strip():
                    time.sleep(wait)
                    continue
                break
            if x["prompt_sha256_16"] != want16:
                sys.exit(f"REFUSING: {label}: logged prompt {x['prompt_sha256_16']} is not "
                         f"the frozen {want16}")
            served.add(x["provider_served"])
            models.add(x["served_model"])
            if len(served) > 1:
                raise Unread(f"served by more than one provider: {sorted(served)}")
            recs.append(score(kind, key, x))
        cells[label] = {"key": key, "kind": kind, "draws": recs, "prompt16": want16,
                        "settings": s}
    json.dump({"arm": arm, "run": run, "group": frames["arms"][arm]["group"],
               "frames": FRAMES, "frames_sha256": hashlib.sha256(
                   open(f"{R}/{FRAMES}", "rb").read()).hexdigest(),
               "providers_served": sorted(served), "models_served": sorted(models),
               "calls": h.calls, "spent_usd": h.spent, "cells": cells},
              open(out_path, "w"), indent=1)
    print(f"{arm}: {h.calls} calls, ${h.spent:.3f} -> {os.path.relpath(out_path, R)}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--arm")
    ap.add_argument("--run", type=int)
    ap.add_argument("--cap-usd", type=float, default=2.0)
    a = ap.parse_args(argv)
    frames = load_frames()
    if a.check_only:
        return check_only(frames)
    if not (a.arm and a.run) or a.arm not in frames["arms"]:
        sys.exit("give --run N and --arm, one of " + ", ".join(frames["arms"]))
    read(frames, a.arm, a.run, a.cap_usd)


if __name__ == "__main__":
    main()

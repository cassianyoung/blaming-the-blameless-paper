#!/usr/bin/env python3
"""read_subject_identity.py : subject_identity, the seven banked cells read with Alaric, John and Jane.

    python3 scripts/read_subject_identity.py --arm gpt4o
    python3 scripts/read_subject_identity.py --arm gpt4o --deadline 2026-10-13T23:00:00Z
    python3 scripts/read_subject_identity.py --selftest          # offline, no network

Pre-registration: records/PREREG_subject_identity_SUBJECT.md (Amendment 0 and the ruling of
2026-10-13: approved at $0.75, defaults on A0.5 and A0.6).

Every call is made on the arm's BANKED WIRE for that scenario, read from the frozen
frames file (A0.3), with the banked draw count. Before a cell is accepted:
  - the prompt the harness logged must hash to the frozen prompt (else REFUSING),
  - the provider that served must be the banked one (else the arm is UNREAD),
  - an empty response (no provider, no text) is retried, not read as a new provider.
Order (A0.8): cell by cell; within a cell the three subjects one after another, each for
its full draw count, the order rotated from cell to cell.
"""
import argparse, hashlib, json, os, statistics, sys, time

R = os.environ.get("AI_ETHICS_ROOT") or os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
from run_rivals import parse_digit, lp_digits
from read_prevention_paraphrase import Unread, msgs_hash

FRAMES = "records/frames.json"
FRAMES_SHA = "68e2a42c27641322f4b112d9daf90cade17399bbee4a3d932eadb891ffd0c6a0"
ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
        "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")
CELLS = (("bicycle", "N"), ("bicycle", "C"), ("bicycle", "P0"),
         ("prawns_home", "N"), ("prawns_home", "C"), ("prawns_home", "P0"),
         ("prawns_restaurant", "C"))
GROUP = {"bicycle": "bicycle", "prawns_home": "prawns", "prawns_restaurant": "prawns"}
SUBJECTS = ("Alaric", "John", "Jane")
RUN_CAP = 0.75


def load_frames(path=None):
    path = path or f"{R}/{FRAMES}"
    blob = open(path, "rb").read()
    got = hashlib.sha256(blob).hexdigest()
    if got != FRAMES_SHA:
        sys.exit(f"REFUSING: frames sha {got[:16]} != frozen {FRAMES_SHA[:16]}")
    return json.loads(blob)


def arm_caps(frames):
    caps = {a: max(0.02, round(2 * frames["estimate"]["per_arm"][a]["usd"], 3))
            for a in ARMS}
    assert sum(caps.values()) <= RUN_CAP, sum(caps.values())
    return caps


def order(i):
    """Subjects for the i-th cell, rotated (A0.8)."""
    return SUBJECTS[i % 3:] + SUBJECTS[:i % 3]


def build(frames, key):
    p = frames["prompts"][key]
    m = [{"role": "system", "content": p["system"]},
         {"role": "user", "content": p["user"]}]
    if msgs_hash(m) != p["prompt_sha256"]:
        sys.exit(f"REFUSING: {key} built prompt does not hash to the frozen value")
    return m, p["prompt_sha256"][:16]


def read_arm(arm, h, frames, deadline=None, wait=60):
    served, served_models, empties = set(), set(), []
    cells = {}
    for i, (scen, role) in enumerate(CELLS):
        g = frames["arms"][arm][GROUP[scen]]
        w, draws = g["wire"], g["draws"]
        logp = bool(w["want_logprobs"])
        for subj in order(i):
            key = f"{scen}|{role}|{subj}"
            m, want16 = build(frames, key)
            recs = []
            for d in range(draws):
                label = f"subject_identity|{arm}|{key}|d{d}"
                while True:
                    try:
                        x = h.rate(w["model"], w["provider_asked"], messages=m,
                                   mode=w["mode"], temperature=w["temperature"],
                                   max_tokens=w["max_tokens"], top_k=w["top_k"] or 20,
                                   want_logprobs=logp, reasoning=w["reasoning_on_the_wire"],
                                   label=label)
                    except RuntimeError as e:
                        if deadline and time.time() > deadline:
                            raise Unread(f"provider {w['provider_asked']} still failing at "
                                         f"the deadline: {e}")
                        print(f"   call failed ({str(e)[:120]}); waiting {wait}s", flush=True)
                        time.sleep(wait)
                        continue
                    if x.get("provider_served") is None and not (x.get("raw_text") or "").strip():
                        empties.append(label)
                        if deadline and time.time() > deadline:
                            raise Unread("empty responses still at the deadline")
                        print(f"   empty response; waiting {wait}s", flush=True)
                        time.sleep(wait)
                        continue
                    break
                if x["prompt_sha256_16"] != want16:
                    sys.exit(f"REFUSING: {label}: logged prompt hash {x['prompt_sha256_16']} "
                             f"!= frozen {want16}")
                if x["provider_served"] != w["provider_served"]:
                    raise Unread(f"served by {x['provider_served']!r}, banked on "
                                 f"{w['provider_served']!r}")
                served.add(x["provider_served"]); served_models.add(x["served_model"])
                txt = x.get("answer_text", x.get("raw_text")) or ""
                r = {"text": txt[:40], "reasoned_despite_off": bool(x.get("reasoning_text_len"))}
                if logp:
                    r["ev"] = x.get("ev")
                    r["raw_digit_mass"] = x.get("digit_mass")
                    r["probs"] = (lp_digits(x) if x.get("ev") is not None else None)
                else:
                    v = parse_digit(txt)
                    r["ev"] = None if v is None else float(v)
                recs.append(r)
            vals = [r["ev"] for r in recs if r["ev"] is not None]
            if logp:
                ok = [r for r in recs if r["ev"] is not None]
                m03 = (statistics.mean(sum(r["probs"][dd] for dd in range(4)) for r in ok)
                       if ok else None)
                raw = statistics.mean(float(r["raw_digit_mass"] or 0.0) for r in recs)
            else:
                m03 = (sum(1 for v in vals if v <= 3) / len(vals)) if vals else None
                raw = None
            cells[key] = {
                "scenario": scen, "role": role, "subject": subj, "readout":
                "logprob ev" if logp else "sampled digit", "n_asked": draws,
                "n_parsed": len(vals), "n_void": draws - len(vals),
                "mean": statistics.mean(vals) if vals else None,
                "sd": statistics.pstdev(vals) if len(vals) > 1 else (0.0 if vals else None),
                "values": vals, "mass_0_3": m03,
                "answer_mass": len(vals) / draws,
                "answer_mass_rule": ("share of draws with a digit in the top-k (the banked "
                                     "renormalised mass is 1.0 on every such draw)" if logp
                                     else "parse rate"),
                "raw_digit_mass": raw,
                "n_reasoned_despite_off": sum(r["reasoned_despite_off"] for r in recs),
                "prompt_sha256_16": want16, "wire": w, "draws": recs}
            c = cells[key]
            print(f"   {key:28s} parsed {c['n_parsed']:2d}/{draws}  mean {c['mean']}  "
                  f"${h.spent:.4f}", flush=True)
    return {"cells": cells, "provider_served": sorted(served),
            "served_model": sorted(served_models),
            "served_model_constant": len(served_models) == 1,
            "empty_responses_retried": empties}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm")
    ap.add_argument("--deadline", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.arm not in ARMS:
        sys.exit(f"unknown arm {a.arm!r}")
    from or_harness import Harness
    frames = load_frames()
    caps = arm_caps(frames)
    dest = f"{R}/records/read__{a.arm}.json"
    if os.path.exists(dest):
        sys.exit(f"write-once: {os.path.relpath(dest, R)} exists")
    os.makedirs(f"{R}/runs/subject_identity/logs", exist_ok=True)
    h = Harness(f"{R}/runs/subject_identity/logs/or_{a.arm}.jsonl", cap_usd=caps[a.arm])
    import calendar
    dl = (calendar.timegm(time.strptime(a.deadline, "%Y-%m-%dT%H:%M:%SZ"))
          if a.deadline else None)
    t0 = time.time()
    out = {"run": "234", "arm": a.arm, "frames": FRAMES, "frames_sha256": FRAMES_SHA,
           "arm_cap_usd": caps[a.arm], "prereg": "records/PREREG_subject_identity_SUBJECT.md",
           "wire": {g: frames["arms"][a.arm][g]["wire"] for g in ("bicycle", "prawns")},
           "draws": {g: frames["arms"][a.arm][g]["draws"] for g in ("bicycle", "prawns")}}
    try:
        out.update(read_arm(a.arm, h, frames, dl))
        out["status"] = "READ"
    except Unread as e:
        out.update({"status": "UNREAD", "unread_reason": str(e)})
    except SystemExit as e:
        if "spend cap" not in str(e):
            raise
        out.update({"status": "UNREAD", "unread_reason": f"arm ceiling reached: {e}"})
    out.update({"calls": h.calls, "spent_usd": h.spent,
                "elapsed_s": round(time.time() - t0, 1)})
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"\n   {out['status']}  {h.calls} calls  ${h.spent:.4f}  -> "
          f"{os.path.relpath(dest, R)}")
    return 0


# ── THE PAIRED TEST: THE GATES REFUSE, AND THEY OPEN ───────────────────────────────
class _Fake:
    def __init__(self, served="OpenAI", tamper=False, digit="3"):
        self.spent, self.calls, self.served, self.tamper, self.digit = 0.0, 0, served, tamper, digit
        self.kw, self.labels = [], []
        self.empty_once = False

    def rate(self, model, provider, messages=None, want_logprobs=True, label="", **k):
        self.calls += 1
        self.kw.append(dict(k, want_logprobs=want_logprobs, provider=provider, model=model))
        self.labels.append(label)
        if self.empty_once:
            self.empty_once = False
            return {"prompt_sha256_16": msgs_hash(messages)[:16], "provider_served": None,
                    "served_model": None, "raw_text": "", "answer_text": "", "top_tokens": []}
        m = messages
        if self.tamper:
            m = [dict(messages[0]), {"role": "user", "content": messages[1]["content"] + " "}]
        top = [{"t": "2", "lp": -0.693}, {"t": "4", "lp": -0.693}, {"t": "x", "lp": -3}]
        return {"prompt_sha256_16": msgs_hash(m)[:16], "provider_served": self.served,
                "served_model": model, "temperature": 1.0, "reasoning_text_len": 0,
                "raw_text": self.digit, "answer_text": self.digit,
                "ev": 3.0 if want_logprobs else None, "digit_mass": 1.0,
                "top_tokens": top}


def selftest():
    import contextlib, io
    frames = load_frames()
    ok = 0

    def expect_exit(fn, what):
        nonlocal ok
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn()
        except SystemExit as e:
            assert "REFUSING" in str(e), (what, e)
            ok += 1; print(f"  ok  refuses: {what}"); return
        raise AssertionError(f"did not refuse: {what}")

    # 1. opens: log-prob arm on its banked wire, banked draws, all 21 cells
    f = _Fake(served="Parasail")
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("mistral24b", f, frames)
    assert len(r["cells"]) == 21 and f.calls == 3 * (3 * 20 + 4 * 10)
    c = r["cells"]["bicycle|P0|Jane"]
    assert c["n_asked"] == 20 and c["mean"] == 3.0 and abs(c["mass_0_3"] - 0.5) < 1e-6
    assert c["raw_digit_mass"] == 1.0 and c["answer_mass"] == 1.0
    k0 = f.kw[0]
    assert k0["want_logprobs"] and k0["max_tokens"] == 1 and k0["top_k"] == 20
    assert k0["reasoning"] == {"enabled": False} and k0["provider"] == "Parasail"
    ok += 1; print("  ok  opens: log-prob arm, banked wire and draws (bicycle 20, prawns 10)")
    # 2. opens: sampled arm, each scenario on its own banked max_tokens
    f = _Fake(served="Anthropic", digit="7")
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("claude", f, frames)
    assert f.calls == 3 * (3 * 20 + 4 * 10)
    assert f.kw[0]["max_tokens"] == 8 and f.kw[0]["provider"] == "Anthropic"
    assert f.kw[-1]["max_tokens"] == 256 and f.kw[-1]["provider"] == "anthropic"
    assert not f.kw[0]["want_logprobs"]
    c = r["cells"]["prawns_restaurant|C|John"]
    assert c["mean"] == 7.0 and c["mass_0_3"] == 0.0 and c["raw_digit_mass"] is None
    ok += 1; print("  ok  opens: sampled arm, bicycle at mt 8 and prawns at mt 256 as banked")
    # 3. order: rotated per cell, each subject's draws consecutive
    seq = [l.split("|")[4] for l in f.labels]
    firsts = [seq[0], seq[60], seq[120], seq[180], seq[210]]
    assert firsts == ["Alaric", "John", "Jane", "Alaric", "John"], firsts
    assert seq[:20] == ["Alaric"] * 20 and seq[20:40] == ["John"] * 20
    ok += 1; print("  ok  order: subjects rotated from cell to cell, draws consecutive")
    # 4. sampled parse: a non-digit answer is void, not read
    f = _Fake(served="xAI", digit="Seven.")
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("grok43_s", f, frames)
    c = r["cells"]["bicycle|N|Alaric"]
    assert c["n_parsed"] == 0 and c["mean"] is None and c["answer_mass"] == 0.0
    ok += 1; print("  ok  a non-digit sampled answer is void, answer mass 0")
    # 5. refuses: prompt on the wire is not the frozen one
    expect_exit(lambda: read_arm("gpt4o", _Fake(tamper=True), frames),
                "logged prompt hash differs from the frozen hash")
    # 6. refuses: tampered frames file
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "subject_identity_frames_tamper.json")
    open(tmp, "w").write(open(f"{R}/{FRAMES}").read().replace("Jane", "Jane ", 1))
    expect_exit(lambda: load_frames(tmp), "frames file whose sha differs")
    os.remove(tmp)
    # 7. changed provider -> UNREAD, not moved
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            read_arm("qwen80b", _Fake(served="Nebius"), frames)
        raise AssertionError("changed provider was accepted")
    except Unread as e:
        assert "Nebius" in str(e); ok += 1
        print("  ok  refuses: changed provider -> UNREAD with the reason")
    # 8. empty response retried
    f = _Fake(served="OpenAI"); f.empty_once = True
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("gpt4o", f, frames, wait=0)
    assert f.calls == 211 and len(r["empty_responses_retried"]) == 1
    ok += 1; print("  ok  opens: an empty response is retried and recorded")
    # 9. caps
    caps = arm_caps(frames)
    assert set(caps) == set(ARMS) and sum(caps.values()) <= RUN_CAP
    ok += 1; print(f"  ok  arm ceilings sum to ${sum(caps.values()):.3f}, within ${RUN_CAP}")
    print(f"selftest {ok}/9")
    return 0 if ok == 9 else 1


if __name__ == "__main__":
    sys.exit(main())

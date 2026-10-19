#!/usr/bin/env python3
"""read_prevention_paraphrase.py : prevention_paraphrase, five yes/no questions on seven cells, one arm per process.

    python3 scripts/read_prevention_paraphrase.py --arm gpt4o
    python3 scripts/read_prevention_paraphrase.py --arm qwen235b --deadline 2026-10-12T23:00:00Z
    python3 scripts/read_prevention_paraphrase.py --selftest          # offline, no network

Pre-registration: records/PREREG_prevention_paraphrase_PARAPHRASE.md (Amendment 0, ruled 2026-10-12).

**EVERY PROMPT IS READ FROM THE FROZEN FILE AND GATED TWICE.** Before the call the
messages are hashed and compared with `frames.json`; after it, the harness's own
logged `prompt_sha256_16` is compared again. The second check is on the observable that
went on the wire, which is the only form that can catch a prompt built from the right
material and then not used (VALIDATION WITHOUT CONSUMPTION).

**THE LOG-PROB YES/NO MASS IS BANKED PER CELL.** The deployed_scenarios families harness computed
it in `lp_yn` and discarded it, so no banked log-prob yes/no cell carries an answer mass
of its own. Here it is the gate (A0.3: below 0.70 fails).

**A SERVED PROVIDER OTHER THAN THE BANKED ONE MAKES THE ARM UNREAD**, with the reason,
and nothing is moved (ruling 2026-10-12, A0.9). A 429 is waited out; past --deadline the
arm is written as UNREAD.
"""
import argparse, hashlib, json, os, statistics, sys, time

R = os.environ.get("AI_ETHICS_ROOT") or os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
from run_rivals import parse_yn, lp_yn

FRAMES = "records/frames.json"
FRAMES_SHA = "5a74f7867103f93749054d2c215f2bf865f782f158ae1f2b7c2a85572c864aea"
QUESTIONS = ("FELL", "DIFF", "NEGL", "REASONABLE", "CARELESS")
CELLS = (("bicycle", "P0"), ("bicycle", "C"), ("ladder", "P0"),
         ("prawns_home", "P0"), ("prawns_restaurant", "P0"), ("scaffolding", "P0"),
         ("cheque", "P0"))
GATE_MASS = 0.70
CAP_USD = 2.00   # the run's cap; each arm process carries it, the total is checked after

# A0.2, frozen from each arm's banked families log. (model, provider asked, provider
# the log shows served, readout, max_tokens, top_k, bicycle draws)
ARMS = {
 "claude":     ("anthropic/claude-sonnet-5", "anthropic", "Anthropic", "sampled", 256, None, 20),
 "deepseek":   ("deepseek/deepseek-v4.1-flash", "Sail Research", "Sail Research", "logprob", 1, 20, 10),
 "deepseek_s": ("deepseek/deepseek-v4.1-flash", "Sail Research", "Sail Research", "sampled", 256, None, 20),
 "gemma27b":   ("google/gemma-3-27b-it", "Parasail", "Parasail", "logprob", 1, 20, 10),
 "gpt4o":      ("openai/gpt-4o", "openai", "OpenAI", "logprob", 1, 20, 10),
 "gpt6l_s":    ("openai/gpt-6-luna", "openai", "OpenAI", "sampled", 1024, None, 10),
 "gpt6s_s":    ("openai/gpt-6-sol", "openai", "OpenAI", "sampled", 1024, None, 10),
 "grok43_s":   ("x-ai/grok-4.3", "xai", "xAI", "sampled", 1024, None, 10),
 "haiku_s":    ("anthropic/claude-haiku-4.5", "Anthropic", "Anthropic", "sampled", 256, None, 10),
 "kimi":       ("moonshotai/kimi-k3", "Sail Research", "Sail Research", "logprob", 1, 20, 10),
 "llama70b":   ("meta-llama/llama-3.3-70b-instruct", "coreweave", "CoreWeave", "logprob", 1, 20, 10),
 "mistral24b": ("mistralai/mistral-small-3.2-24b-instruct", "Parasail", "Parasail", "logprob", 1, 20, 10),
 "qwen235b":   ("qwen/qwen3-235b-a22b-2507", "GMICloud", "GMICloud", "logprob", 1, 5, 10),
 "qwen30b":    ("qwen/qwen3-30b-a3b-instruct-2507", "StreamLake", "StreamLake", "logprob", 1, 20, 10),
 "qwen80b":    ("qwen/qwen3-next-80b-a3b-instruct", "Parasail", "Parasail", "logprob", 1, 20, 10),
}
FAMILY_DRAWS = 10


def msgs_hash(m):
    return hashlib.sha256(json.dumps(m).encode()).hexdigest()


def load_frames(path):
    blob = open(path, "rb").read()
    got = hashlib.sha256(blob).hexdigest()
    if got != FRAMES_SHA:
        sys.exit(f"REFUSING: frames sha {got[:16]} != frozen {FRAMES_SHA[:16]}")
    return json.loads(blob)


def build(frames, scen, role, q):
    p = frames["prompts"][f"{scen}|{role}|{q}"]
    m = [{"role": "system", "content": p["system"]},
         {"role": "user", "content": p["user"]}]
    if msgs_hash(m) != p["prompt_sha256"]:
        sys.exit(f"REFUSING: {scen}|{role}|{q} built prompt does not hash to the frozen value")
    return m, p["prompt_sha256"]


class Unread(Exception):
    pass


def read_arm(arm, h, frames, deadline=None, wait=60):
    model, prov, served_want, readout, mt, top_k, bike_draws = ARMS[arm]
    logp = readout == "logprob"
    served, served_models, temps = set(), set(), set()
    cells = {}

    def call(m, label, want16):
        while True:
            try:
                x = h.rate(model, prov, messages=m, mode="chat", max_tokens=mt,
                           top_k=top_k or 20, label=label, reasoning_off=True,
                           want_logprobs=logp)
                break
            except RuntimeError as e:
                if deadline and time.time() > deadline:
                    raise Unread(f"provider {prov} still failing at the deadline: {e}")
                print(f"   call failed ({str(e)[:120]}); waiting {wait}s", flush=True)
                time.sleep(wait)
        if x["prompt_sha256_16"] != want16:
            sys.exit(f"REFUSING: {label}: logged prompt hash {x['prompt_sha256_16']} != "
                     f"frozen {want16}. The prompt on the wire is not the frozen one.")
        if x["provider_served"] != served_want:
            raise Unread(f"served by {x['provider_served']!r}, banked on {served_want!r}")
        served.add(x["provider_served"]); served_models.add(x["served_model"])
        temps.add(x["temperature"])
        return x

    for scen, role in CELLS:
        draws = bike_draws if scen == "bicycle" else FAMILY_DRAWS
        for q in QUESTIONS:
            m, ph = build(frames, scen, role, q)
            ys, masses, unparsed, reasoned = [], [], [], 0
            for d in range(draws):
                x = call(m, f"prevention_paraphrase|{arm}|{scen}|{role}|{q}|d{d}", ph[:16])
                reasoned += bool(x.get("reasoning_text_len"))
                if logp:
                    y, mass = lp_yn(x)
                    masses.append(mass)
                    if y is not None:
                        ys.append(y)
                else:
                    v = parse_yn(x.get("answer_text", x["raw_text"]))
                    if v is None:
                        unparsed.append(x.get("answer_text", x["raw_text"]))
                    else:
                        ys.append(1.0 if v == "yes" else 0.0)
            p = statistics.mean(ys) if ys else None
            mass = statistics.mean(masses) if logp else len(ys) / draws
            cells[f"{scen}|{role}|{q}"] = {
                "scenario": scen, "role": role, "question": q,
                "p_yes": p, "p_yes_sd": statistics.pstdev(ys) if ys else None,
                "modal": None if p is None or p == 0.5 else ("yes" if p > 0.5 else "no"),
                "answer_mass": mass,
                "answer_mass_source": ("mean raw yes+no probability in the top-k"
                                       if logp else "parsed over asked"),
                "gate": "PASSED" if mass >= GATE_MASS else "FAILED",
                "n_asked": draws, "n_parsed": len(ys),
                "unparsed_texts": unparsed, "reasoned_despite_off": reasoned,
                "prompt_sha256": ph}
            print(f"   {scen:18s} {role:3s} {q:10s} p_yes "
                  f"{'None' if p is None else f'{p:.4f}'}  mass {mass:.3f}  "
                  f"${h.spent:.4f}", flush=True)
    return {"cells": cells, "provider_served": sorted(served),
            "served_model": sorted(served_models),
            "served_model_constant": len(served_models) == 1,
            "temperature": sorted(temps)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm")
    ap.add_argument("--deadline", default=None, help="UTC ISO; past it a failing arm is UNREAD")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.arm not in ARMS:
        sys.exit(f"unknown arm {a.arm!r}")
    from or_harness import Harness
    frames = load_frames(f"{R}/{FRAMES}")
    dest = f"{R}/records/read__{a.arm}.json"
    if os.path.exists(dest):
        sys.exit(f"write-once: {os.path.relpath(dest, R)} exists")
    os.makedirs(f"{R}/runs/prevention_paraphrase/logs", exist_ok=True)
    h = Harness(f"{R}/runs/prevention_paraphrase/logs/or_{a.arm}.jsonl", cap_usd=CAP_USD)
    import calendar
    dl = (calendar.timegm(time.strptime(a.deadline, "%Y-%m-%dT%H:%M:%SZ"))
          if a.deadline else None)
    t0 = time.time()
    model, prov, served_want, readout, mt, top_k, _ = ARMS[a.arm]
    out = {"run": "231", "arm": a.arm, "model": model, "provider_requested": prov,
           "provider_banked": served_want, "readout": readout, "max_tokens": mt,
           "top_k": top_k, "frames": FRAMES, "frames_sha256": FRAMES_SHA,
           "prereg": "records/PREREG_prevention_paraphrase_PARAPHRASE.md"}
    try:
        out.update(read_arm(a.arm, h, frames, dl))
        out["status"] = "READ"
    except Unread as e:
        out.update({"status": "UNREAD", "unread_reason": str(e), "cells": {}})
    out.update({"calls": h.calls, "spent_usd": h.spent,
                "elapsed_s": round(time.time() - t0, 1)})
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"\n   {out['status']}  {h.calls} calls  ${h.spent:.4f}  -> "
          f"{os.path.relpath(dest, R)}")
    return 0


# ── THE PAIRED TEST: THE GATES REFUSE, AND THEY OPEN ───────────────────────────────
class _Fake:
    """Returns what or_harness would log, hashing the messages it is actually given."""
    def __init__(self, served="OpenAI", tamper=False, answer="No"):
        self.spent, self.calls, self.served, self.tamper, self.answer = 0.0, 0, served, tamper, answer

    def rate(self, model, provider, messages=None, want_logprobs=True, **k):
        self.calls += 1
        m = messages
        if self.tamper:
            m = [dict(messages[0]), {"role": "user", "content": messages[1]["content"] + " "}]
        rec = {"prompt_sha256_16": msgs_hash(m)[:16], "provider_served": self.served,
               "served_model": model, "temperature": 1.0, "reasoning_text_len": 0,
               "raw_text": self.answer, "answer_text": self.answer,
               "top_tokens": [{"t": "No", "lp": -0.1}, {"t": "Yes", "lp": -2.5},
                              {"t": "The", "lp": -6.0}]}
        return rec


def selftest():
    import contextlib, io
    frames = load_frames(f"{R}/{FRAMES}")
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

    # 1. opens: log-prob arm, every cell, mass and p_yes as constructed
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("gpt4o", _Fake(), frames)
    assert len(r["cells"]) == 35, len(r["cells"])
    c = r["cells"]["cheque|P0|FELL"]
    py = 2.718281828 ** -2.5 / (2.718281828 ** -0.1 + 2.718281828 ** -2.5)
    assert abs(c["p_yes"] - py) < 1e-6 and c["modal"] == "no", c
    assert abs(c["answer_mass"] - (2.718281828 ** -0.1 + 2.718281828 ** -2.5)) < 1e-6
    assert c["gate"] == "PASSED" and r["served_model_constant"]
    ok += 1; print("  ok  opens: log-prob arm, 35 cells, mass banked, gate passes")
    # 2. opens: sampled arm, bicycle at 20 draws, a hedge is kept verbatim
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("claude", _Fake(served="Anthropic", answer="It depends."), frames)
    c = r["cells"]["bicycle|P0|NEGL"]
    assert c["n_asked"] == 20 and c["n_parsed"] == 0 and c["p_yes"] is None
    assert c["gate"] == "FAILED" and c["unparsed_texts"][0] == "It depends."
    assert r["cells"]["ladder|P0|NEGL"]["n_asked"] == 10
    ok += 1; print("  ok  opens: sampled arm, 20 bicycle draws, hedge kept, gate fails it")
    # 3. refuses: the prompt on the wire is not the frozen one
    expect_exit(lambda: read_arm("gpt4o", _Fake(tamper=True), frames),
                "logged prompt hash differs from the frozen hash")
    # 4. refuses: tampered frames file
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "prevention_paraphrase_frames_tamper.json")
    open(tmp, "w").write(open(f"{R}/{FRAMES}").read().replace("negligent", "negligent "))
    expect_exit(lambda: load_frames(tmp), "frames file whose sha differs")
    os.remove(tmp)
    # 5. a changed provider makes the arm UNREAD, not moved
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            read_arm("qwen235b", _Fake(served="Nebius"), frames)
        raise AssertionError("changed provider was accepted")
    except Unread as e:
        assert "Nebius" in str(e); ok += 1
        print("  ok  refuses: changed provider -> UNREAD with the reason")
    print(f"selftest {ok}/5")
    return 0 if ok == 5 else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""read_practical_syllogism.py : practical_syllogism, the principle (A) and the three-in-one remedy check (B).

    python3 scripts/read_practical_syllogism.py --arm gpt4o
    python3 scripts/read_practical_syllogism.py --arm gpt4o --deadline 2026-10-13T12:00:00Z
    python3 scripts/read_practical_syllogism.py --selftest          # offline, no network

Pre-registration: records/PREREG_practical_syllogism_SYLLOGISM.md (Amendment 0 and the ruling of
2026-10-13: all five defaults; A and B both read, B on P0, N and C).

Arm settings are prevention_paraphrase's, imported rather than copied, so the two runs cannot differ by
a retyped field (A0.2). The prompt gate is prevention_paraphrase's: every prompt is read from the frozen
file, hashed before the call, and the harness's logged hash of what went on the wire is
compared after it.

A is read in each arm's banked readout (log-prob P(yes) or sampled yes/no), ten calls.
B is read by SAMPLING on every arm, the log-prob arms included (A0.7 B.1), ten draws per
cell, on 6 scenarios x (P0, N, C). A B draw parses only if all three fields are present
in order; an unparsed draw is kept verbatim.
"""
import argparse, hashlib, json, os, re, statistics, sys, time

R = os.environ.get("AI_ETHICS_ROOT") or os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
from run_rivals import parse_yn, lp_yn
from read_prevention_paraphrase import ARMS as ARMS231, Unread, msgs_hash

FRAMES = "records/frames.json"
FRAMES_SHA = "6fc50e644efbd2e6c56d922b6e9c76a79c5d2ae474dd468cc993ef6991d1525f"
READ_ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
             "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")
ARMS = {a: ARMS231[a] for a in READ_ARMS}
SCEN = ("bicycle", "ladder", "prawns_home", "prawns_restaurant", "scaffolding", "cheque")
B_ROLES = ("P0", "N", "C")
A_DRAWS, B_DRAWS = 10, 10
B_MT_LOGPROB_ARMS = 32          # A0.7 B.1: the form needs about 15 tokens
GATE_MASS = 0.70
CAP_USD = 2.00

# all three fields, in order; tolerant of brackets, quotes, asterisks and spacing
B_RX = re.compile(r"PREVENT\W*(yes|no)\b.*?PRINCIPLE\W*(yes|no)\b.*?BLAME\W*([0-9])(?![0-9])",
                  re.I | re.S)


def parse_b(t):
    m = B_RX.search(t or "")
    if not m:
        return None
    return {"PREVENT": m.group(1).lower(), "PRINCIPLE": m.group(2).lower(),
            "BLAME": int(m.group(3))}


def load_frames(path):
    blob = open(path, "rb").read()
    got = hashlib.sha256(blob).hexdigest()
    if got != FRAMES_SHA:
        sys.exit(f"REFUSING: frames sha {got[:16]} != frozen {FRAMES_SHA[:16]}")
    return json.loads(blob)


def build(frames, key):
    p = frames["prompts"][key]
    m = [{"role": "system", "content": p["system"]},
         {"role": "user", "content": p["user"]}]
    if msgs_hash(m) != p["prompt_sha256"]:
        sys.exit(f"REFUSING: {key} built prompt does not hash to the frozen value")
    return m, p["prompt_sha256"]


def read_arm(arm, h, frames, deadline=None, wait=60, conditions=("A", "B")):
    model, prov, served_want, readout, mt, top_k, _ = ARMS[arm]
    logp = readout == "logprob"
    served, served_models, temps = set(), set(), set()
    empties = []

    def call(m, label, want16, sampled):
        while True:
            try:
                x = h.rate(model, prov, messages=m, mode="chat",
                           max_tokens=(B_MT_LOGPROB_ARMS if (logp and sampled) else mt),
                           top_k=top_k or 20, label=label, reasoning_off=True,
                           want_logprobs=(logp and not sampled))
            except RuntimeError as e:
                if deadline and time.time() > deadline:
                    raise Unread(f"provider {prov} still failing at the deadline: {e}")
                print(f"   call failed ({str(e)[:120]}); waiting {wait}s", flush=True)
                time.sleep(wait)
                continue
            # ── AN EMPTY RESPONSE IS A FAILED CALL, NOT A CHANGED PROVIDER ──────────
            # grok43_s's first read (2026-10-13 08:05Z) got one response with no
            # provider, no text and no cost, after 71 calls all served by xAI, and the
            # provider check below read None as a different provider and wrote the arm
            # UNREAD. A0.2's rule is about a provider OTHER than the banked one serving
            # the call; nothing served this one. So it is retried like a 429.
            if x.get("provider_served") is None and not (x.get("raw_text") or "").strip():
                empties.append(label)
                if deadline and time.time() > deadline:
                    raise Unread(f"empty responses from {prov} still at the deadline")
                print(f"   empty response (no provider, no text); waiting {wait}s",
                      flush=True)
                time.sleep(wait)
                continue
            break
        if x["prompt_sha256_16"] != want16:
            sys.exit(f"REFUSING: {label}: logged prompt hash {x['prompt_sha256_16']} != "
                     f"frozen {want16}. The prompt on the wire is not the frozen one.")
        if x["provider_served"] != served_want:
            raise Unread(f"served by {x['provider_served']!r}, banked on {served_want!r}")
        served.add(x["provider_served"]); served_models.add(x["served_model"])
        temps.add(x["temperature"])
        return x

    out = {}
    if "A" in conditions:
        m, ph = build(frames, "A|principle")
        draws = []
        for d in range(A_DRAWS):
            x = call(m, f"practical_syllogism|{arm}|A|principle|d{d}", ph[:16], sampled=False)
            txt = x.get("answer_text", x["raw_text"])
            rec = {"text": txt, "reasoned_despite_off": bool(x.get("reasoning_text_len"))}
            if logp:
                py, mass = lp_yn(x)
                rec.update({"p_yes": py, "mass": mass, "sampled_token": parse_yn(txt)})
            else:
                rec["answer"] = parse_yn(txt)
            draws.append(rec)
        if logp:
            ps = [r["p_yes"] for r in draws if r["p_yes"] is not None]
            p = statistics.mean(ps) if ps else None
            mass = statistics.mean(r["mass"] for r in draws)
            n_no = None
            held = p is not None and p <= 0.10            # A0.3
        else:
            ans = [r["answer"] for r in draws]
            parsed = [a for a in ans if a is not None]
            p = (sum(a == "yes" for a in parsed) / len(parsed)) if parsed else None
            mass = len(parsed) / A_DRAWS
            n_no = sum(a == "no" for a in ans)
            held = n_no >= 9                                # unparsed counts against
        gate = "PASSED" if mass >= GATE_MASS else "FAILED"
        out["A"] = {"p_yes": p, "answer_mass": mass, "gate": gate, "n_no": n_no,
                    "n_asked": A_DRAWS,
                    "principle_held": bool(held and gate == "PASSED"),
                    "rule": ("mean P(yes) <= 0.10 (A0.3)" if logp
                             else "at least 9 of 10 parsed 'no'; unparsed counts against"),
                    "prompt_sha256": ph, "draws": draws}
        print(f"   A principle  p_yes {p}  mass {mass:.3f}  held {out['A']['principle_held']}"
              f"  ${h.spent:.4f}", flush=True)

    if "B" in conditions:
        cells = {}
        for scen in SCEN:
            for role in B_ROLES:
                key = f"B|{scen}|{role}"
                m, ph = build(frames, key)
                draws = []
                for d in range(B_DRAWS):
                    x = call(m, f"practical_syllogism|{arm}|{key}|d{d}", ph[:16], sampled=True)
                    txt = x.get("answer_text", x["raw_text"])
                    draws.append({"text": txt, "parsed": parse_b(txt),
                                  "reasoned_despite_off": bool(x.get("reasoning_text_len"))})
                ok = [r["parsed"] for r in draws if r["parsed"]]
                bl = [r["BLAME"] for r in ok]
                cells[key] = {
                    "scenario": scen, "role": role, "n_asked": B_DRAWS, "n_parsed": len(ok),
                    "gate_parse": "PASSED" if len(ok) >= 7 else "FAILED",
                    "blame_mean": statistics.mean(bl) if bl else None,
                    "blame_mass_0_3": (sum(b <= 3 for b in bl) / len(bl)) if bl else None,
                    "p_prevent_yes": (sum(r["PREVENT"] == "yes" for r in ok) / len(ok)
                                      if ok else None),
                    "p_principle_yes": (sum(r["PRINCIPLE"] == "yes" for r in ok) / len(ok)
                                        if ok else None),
                    "unparsed_texts": [r["text"] for r in draws if not r["parsed"]],
                    "prompt_sha256": ph, "draws": draws}
                c = cells[key]
                print(f"   {key:28s} parsed {len(ok):2d}  blame {c['blame_mean']}  "
                      f"${h.spent:.4f}", flush=True)
        out["B"] = cells
    out.update({"provider_served": sorted(served), "served_model": sorted(served_models),
                "served_model_constant": len(served_models) == 1,
                "temperature": sorted(temps), "empty_responses_retried": empties})
    return out


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
    os.makedirs(f"{R}/runs/practical_syllogism/logs", exist_ok=True)
    h = Harness(f"{R}/runs/practical_syllogism/logs/or_{a.arm}.jsonl", cap_usd=CAP_USD)
    import calendar
    dl = (calendar.timegm(time.strptime(a.deadline, "%Y-%m-%dT%H:%M:%SZ"))
          if a.deadline else None)
    t0 = time.time()
    model, prov, served_want, readout, mt, top_k, _ = ARMS[a.arm]
    out = {"run": "232", "arm": a.arm, "model": model, "provider_requested": prov,
           "provider_banked": served_want, "readout_A": readout, "readout_B": "sampled",
           "max_tokens_A": mt,
           "max_tokens_B": B_MT_LOGPROB_ARMS if readout == "logprob" else mt,
           "top_k": top_k, "frames": FRAMES, "frames_sha256": FRAMES_SHA,
           "prereg": "records/PREREG_practical_syllogism_SYLLOGISM.md"}
    try:
        out.update(read_arm(a.arm, h, frames, dl))
        out["status"] = "READ"
    except Unread as e:
        out.update({"status": "UNREAD", "unread_reason": str(e)})
    out.update({"calls": h.calls, "spent_usd": h.spent,
                "elapsed_s": round(time.time() - t0, 1)})
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"\n   {out['status']}  {h.calls} calls  ${h.spent:.4f}  -> "
          f"{os.path.relpath(dest, R)}")
    return 0


# ── THE PAIRED TEST: THE GATES REFUSE, AND THEY OPEN ───────────────────────────────
class _Fake:
    """Returns what or_harness would log, hashing the messages it is actually given."""
    def __init__(self, served="OpenAI", tamper=False, a_answer="No",
                 b_answer="PREVENT=no PRINCIPLE=no BLAME=2"):
        self.spent, self.calls, self.served, self.tamper = 0.0, 0, served, tamper
        self.a_answer, self.b_answer, self.kw = a_answer, b_answer, []

    def rate(self, model, provider, messages=None, want_logprobs=True, **k):
        self.calls += 1
        self.kw.append(dict(k, want_logprobs=want_logprobs))
        if getattr(self, "empty_once", False):
            self.empty_once = False
            return {"prompt_sha256_16": msgs_hash(messages)[:16], "provider_served": None,
                    "served_model": None, "temperature": None, "raw_text": "",
                    "answer_text": "", "top_tokens": []}
        m = messages
        if self.tamper:
            m = [dict(messages[0]), {"role": "user", "content": messages[1]["content"] + " "}]
        ans = self.b_answer if "PREVENT=" in messages[0]["content"] else self.a_answer
        return {"prompt_sha256_16": msgs_hash(m)[:16], "provider_served": self.served,
                "served_model": model, "temperature": 1.0, "reasoning_text_len": 0,
                "raw_text": ans, "answer_text": ans,
                "top_tokens": [{"t": "No", "lp": -0.01}, {"t": "Yes", "lp": -5.0},
                               {"t": "The", "lp": -6.0}]}


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

    # 1. opens: log-prob arm; A by log-prob, B SAMPLED at 32 tokens; 190 calls
    f = _Fake()
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("gpt4o", f, frames)
    assert f.calls == 190 and len(r["B"]) == 18, (f.calls, len(r["B"]))
    assert r["A"]["principle_held"] and r["A"]["p_yes"] < 0.01
    assert f.kw[0]["want_logprobs"] and f.kw[0]["max_tokens"] == 1
    assert not f.kw[10]["want_logprobs"] and f.kw[10]["max_tokens"] == 32
    c = r["B"]["B|ladder|P0"]
    assert c["n_parsed"] == 10 and c["blame_mean"] == 2 and c["p_prevent_yes"] == 0
    ok += 1; print("  ok  opens: log-prob arm, A by log-prob, B sampled at 32 tokens")
    # 2. opens: sampled arm; A counts 'no'; an unparsed B draw is kept and fails the gate
    f = _Fake(served="Anthropic", a_answer="Yes", b_answer="I would rather not say.")
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("claude", f, frames)
    assert r["A"]["n_no"] == 0 and not r["A"]["principle_held"]
    c = r["B"]["B|cheque|N"]
    assert c["n_parsed"] == 0 and c["gate_parse"] == "FAILED"
    assert c["unparsed_texts"][0] == "I would rather not say."
    assert f.kw[10]["max_tokens"] == 256
    ok += 1; print("  ok  opens: sampled arm, A 'yes' not held, unparsed B kept, gate fails")
    # 3. the B parser: tolerant of form, strict on order and completeness
    assert parse_b("**PREVENT=** No, PRINCIPLE = <no> BLAME=3") == {
        "PREVENT": "no", "PRINCIPLE": "no", "BLAME": 3}
    assert parse_b("PRINCIPLE=no PREVENT=no BLAME=3") is None
    assert parse_b("PREVENT=no PRINCIPLE=no") is None
    assert parse_b("PREVENT=no PRINCIPLE=no BLAME=10") is None
    ok += 1; print("  ok  B parser: tolerant of form, refuses wrong order, missing, two digits")
    # 4. refuses: the prompt on the wire is not the frozen one
    expect_exit(lambda: read_arm("gpt4o", _Fake(tamper=True), frames),
                "logged prompt hash differs from the frozen hash")
    # 5. refuses: tampered frames file
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "practical_syllogism_frames_tamper.json")
    open(tmp, "w").write(open(f"{R}/{FRAMES}").read().replace("Alaric", "Alaric "))
    expect_exit(lambda: load_frames(tmp), "frames file whose sha differs")
    os.remove(tmp)
    # 6. a changed provider makes the arm UNREAD, not moved
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            read_arm("qwen80b", _Fake(served="Nebius"), frames)
        raise AssertionError("changed provider was accepted")
    except Unread as e:
        assert "Nebius" in str(e); ok += 1
        print("  ok  refuses: changed provider -> UNREAD with the reason")
    # 7. an empty response (no provider, no text) is retried, not read as a new provider
    f = _Fake(served="xAI"); f.empty_once = True
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("grok43_s", f, frames, wait=0)
    assert f.calls == 191 and len(r["empty_responses_retried"]) == 1
    assert r["provider_served"] == ["xAI"] and len(r["B"]) == 18
    ok += 1; print("  ok  opens: an empty response is retried and recorded, arm READ")
    print(f"selftest {ok}/7")
    return 0 if ok == 7 else 1


if __name__ == "__main__":
    sys.exit(main())

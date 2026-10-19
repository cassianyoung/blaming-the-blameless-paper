#!/usr/bin/env python3
"""read_general_principle.py : syllogism_duty Amendment G, the principle in general, with no case.

    python3 scripts/read_general_principle.py --arm gpt4o
    python3 scripts/read_general_principle.py --arm gpt4o --deadline 2026-10-13T18:00:00Z
    python3 scripts/read_general_principle.py --selftest          # offline, no network

Pre-registration: records/PREREG_general_principle_GENERAL.md (Amendment G0 and the ruling of
2026-10-13: defaults on AG.1 and AG.7, yes on AG.2, G1 read in both orders, cap $0.40).

Five prompts, ten draws each, SAMPLED at temperature 1 on every arm, reasoning off; the
sampled arms at their banked max_tokens, the log-prob arms at 32 (as run syllogism_duty's B):

  G1     three-way, professional first, "more, less, or equally"
  G1_AP  three-way, amateur first, "less, more, or equally"
  G2     yes / no; on the seven log-prob arms the top-20 log-probabilities are requested
         as well (AG.2), so mean P(yes) can be read under syllogism_duty.P1's rule beside the count
  G3_PA  PROFESSIONAL=<digit> AMATEUR=<digit>
  G3_AP  AMATEUR=<digit> PROFESSIONAL=<digit>

Start condition (changed by the author, 2026-10-13, before any G call): the twelve arms other
than mistral24b start at once. mistral24b refuses before any call until run syllogism_duty's
mistral24b read has been written, READ or UNREAD, so the two reads never compete for
Parasail's rate limit.
"""
import argparse, hashlib, json, os, re, statistics, sys, time

R = os.environ.get("AI_ETHICS_ROOT") or os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
from run_rivals import parse_yn, lp_yn
from read_prevention_paraphrase import Unread, msgs_hash
from read_syllogism_duty import ARMS, READ_ARMS

FRAMES = "records/general_principle_FRAMES_v2.json"
FRAMES_SHA = "342ec134f524a27963e1be5fcf5f74d7a27f749e3ce97df393f6c7c108cc6df3"
AFTER = "records/syllogism_duty_READ__mistral24b.json"
HELD_UNTIL_AFTER = ("mistral24b",)          # shares Parasail with run syllogism_duty's pending read
KEYS = ("G1", "G1_AP", "G2", "G3_PA", "G3_AP")
DRAWS = 10
MT_LOGPROB_ARMS = 32
G3_GATE = 7
# ── SPEND: twice each arm's estimate (AG.8 with G1_AP added), at least $0.02 ───────────
EST_USD = {"claude": 0.0215, "deepseek": 0.0002, "deepseek_s": 0.0001, "gemma27b": 0.0004,
           "gpt4o": 0.0172, "gpt6l_s": 0.0008, "gpt6s_s": 0.0158, "grok43_s": 0.0132,
           "haiku_s": 0.0079, "kimi": 0.0084, "llama70b": 0.0060, "mistral24b": 0.0005,
           "qwen80b": 0.0009}
ARM_CAP = {a: max(0.02, round(2 * e, 3)) for a, e in EST_USD.items()}
RUN_CAP = 0.40
assert sum(ARM_CAP.values()) <= RUN_CAP, sum(ARM_CAP.values())

_STRIP = " \t\r\n\"'`*_()[]<>.!:;"


def parse_g1(t):
    s = (t or "").strip(_STRIP).lower()
    if s == "equal":
        s = "equally"
    return s if s in ("more", "less", "equally") else None


_PRO = re.compile(r"PROFESSIONAL\W*([0-9])(?![0-9])", re.I)
_AMA = re.compile(r"AMATEUR\W*([0-9])(?![0-9])", re.I)


def parse_g3(t):
    p, a = _PRO.findall(t or ""), _AMA.findall(t or "")
    if len(p) != 1 or len(a) != 1:
        return None
    return {"PROFESSIONAL": int(p[0]), "AMATEUR": int(a[0])}


def fsha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


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


def read_arm(arm, h, frames, deadline=None, wait=60):
    model, prov, served_want, readout, mt, top_k, _ = ARMS[arm]
    logp = readout == "logprob"
    served, served_models, temps, empties = set(), set(), set(), []

    def call(m, label, want16, lp):
        while True:
            try:
                x = h.rate(model, prov, messages=m, mode="chat",
                           max_tokens=MT_LOGPROB_ARMS if logp else mt,
                           top_k=top_k or 20, label=label, reasoning_off=True,
                           want_logprobs=lp)
            except RuntimeError as e:
                if deadline and time.time() > deadline:
                    raise Unread(f"provider {prov} still failing at the deadline: {e}")
                print(f"   call failed ({str(e)[:120]}); waiting {wait}s", flush=True)
                time.sleep(wait)
                continue
            # an empty response is a failed call, not a changed provider (practical_syllogism)
            if x.get("provider_served") is None and not (x.get("raw_text") or "").strip():
                empties.append(label)
                if deadline and time.time() > deadline:
                    raise Unread(f"empty responses from {prov} still at the deadline")
                print(f"   empty response (no provider, no text); waiting {wait}s", flush=True)
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
    for key in KEYS:
        m, ph = build(frames, key)
        lp = logp and key == "G2"                                   # AG.2
        draws = []
        for d in range(DRAWS):
            x = call(m, f"general_principle|{arm}|{key}|d{d}", ph[:16], lp)
            txt = x.get("answer_text", x["raw_text"])
            rec = {"text": txt, "reasoned_despite_off": bool(x.get("reasoning_text_len"))}
            if key.startswith("G1"):
                rec["answer"] = parse_g1(txt)
            elif key == "G2":
                rec["answer"] = parse_yn(txt)
                if lp:
                    py, mass = lp_yn(x)
                    rec.update({"p_yes": py, "yn_mass": mass})
            else:
                rec["parsed"] = parse_g3(txt)
            draws.append(rec)
        c = {"key": key, "n_asked": DRAWS, "prompt_sha256": ph, "draws": draws}
        if key.startswith("G1"):
            ans = [r["answer"] for r in draws]
            c["counts"] = {k: sum(a == k for a in ans) for k in ("more", "less", "equally")}
            c["counts"]["unparsed"] = sum(a is None for a in ans)
            c["affirms"] = c["counts"]["more"] >= 9          # unparsed counts against
            line = f"{c['counts']}"
        elif key == "G2":
            ans = [r["answer"] for r in draws]
            c["counts"] = {"yes": sum(a == "yes" for a in ans), "no": sum(a == "no" for a in ans),
                           "unparsed": sum(a is None for a in ans)}
            c["affirms"] = c["counts"]["yes"] >= 9
            if lp:
                ps = [r["p_yes"] for r in draws if r["p_yes"] is not None]
                c["mean_p_yes"] = statistics.mean(ps) if ps else None
                c["mean_yn_mass"] = statistics.mean(r["yn_mass"] for r in draws)
                c["held_p233_rule"] = (c["mean_p_yes"] is not None and c["mean_p_yes"] >= 0.90
                                       and c["mean_yn_mass"] >= 0.70)
            line = f"{c['counts']}" + (f"  mean P(yes) {c.get('mean_p_yes')}" if lp else "")
        else:
            ok = [r["parsed"] for r in draws if r["parsed"]]
            c.update({"n_parsed": len(ok),
                      "gate": "PASSED" if len(ok) >= G3_GATE else "FAILED",
                      "professional": [o["PROFESSIONAL"] for o in ok],
                      "amateur": [o["AMATEUR"] for o in ok],
                      "gap": (statistics.mean(o["PROFESSIONAL"] - o["AMATEUR"] for o in ok)
                              if ok else None),
                      "unparsed_texts": [r["text"] for r in draws if not r["parsed"]]})
            line = f"parsed {len(ok)}  gap {c['gap']}"
        out[key] = c
        print(f"   {key:6s} {line}  ${h.spent:.4f}", flush=True)
    return {"G": out, "provider_served": sorted(served), "served_model": sorted(served_models),
            "served_model_constant": len(served_models) == 1,
            "temperature": sorted(t for t in temps if t is not None),
            "empty_responses_retried": empties}


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
    if a.arm in HELD_UNTIL_AFTER and not os.path.exists(f"{R}/{AFTER}"):
        sys.exit(f"REFUSING: {AFTER} does not exist; {a.arm}'s G calls wait for run syllogism_duty's "
                 f"{a.arm} read, so the two do not compete for the provider's rate limit")
    from or_harness import Harness
    frames = load_frames(f"{R}/{FRAMES}")
    dest = f"{R}/records/read__{a.arm}.json"
    if os.path.exists(dest):
        sys.exit(f"write-once: {os.path.relpath(dest, R)} exists")
    os.makedirs(f"{R}/runs/general_principle/logs", exist_ok=True)
    h = Harness(f"{R}/runs/general_principle/logs/or_{a.arm}.jsonl", cap_usd=ARM_CAP[a.arm])
    import calendar
    dl = (calendar.timegm(time.strptime(a.deadline, "%Y-%m-%dT%H:%M:%SZ"))
          if a.deadline else None)
    t0 = time.time()
    model, prov, served_want, readout, mt, top_k, _ = ARMS[a.arm]
    out = {"run": "233G", "arm": a.arm, "model": model, "provider_requested": prov,
           "provider_banked": served_want, "readout": "sampled",
           "logprobs_on_G2": readout == "logprob",
           "max_tokens": MT_LOGPROB_ARMS if readout == "logprob" else mt,
           "top_k": top_k, "frames": FRAMES, "frames_sha256": FRAMES_SHA,
           "arm_cap_usd": ARM_CAP[a.arm], "prereg": "records/PREREG_general_principle_GENERAL.md"}
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
    """Returns what or_harness would log, hashing the messages it is actually given."""
    def __init__(self, served="OpenAI", tamper=False, g1="More", g2="Yes",
                 g3=lambda first: "PROFESSIONAL=7 AMATEUR=4"):
        self.spent, self.calls, self.served, self.tamper = 0.0, 0, served, tamper
        self.g1, self.g2, self.g3, self.kw = g1, g2, g3, []

    def rate(self, model, provider, messages=None, want_logprobs=True, **k):
        self.calls += 1
        self.kw.append(dict(k, want_logprobs=want_logprobs, provider=provider))
        if getattr(self, "empty_once", False):
            self.empty_once = False
            return {"prompt_sha256_16": msgs_hash(messages)[:16], "provider_served": None,
                    "served_model": None, "temperature": None, "raw_text": "",
                    "answer_text": "", "top_tokens": []}
        m = messages
        if self.tamper:
            m = [dict(messages[0]), {"role": "user", "content": messages[1]["content"] + " "}]
        sysm, user = messages[0]["content"], messages[1]["content"]
        if "Yes or No" in sysm:
            ans = self.g2
        elif "or equally" in sysm:
            ans = self.g1(user) if callable(self.g1) else self.g1
        else:
            ans = self.g3(user)
        return {"prompt_sha256_16": msgs_hash(m)[:16], "provider_served": self.served,
                "served_model": model, "temperature": 1.0, "reasoning_text_len": 0,
                "raw_text": ans, "answer_text": ans, "ev": None,
                "top_tokens": [{"t": "Yes", "lp": -0.01}, {"t": "No", "lp": -5.0},
                               {"t": "The", "lp": -6.0}] if want_logprobs else []}


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

    # 1. opens: a log-prob arm, all sampled at 32 tokens, log-probs on G2 only
    f = _Fake()
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("gpt4o", f, frames)
    g = r["G"]
    assert f.calls == 50 and set(g) == set(KEYS)
    assert all(k["max_tokens"] == 32 for k in f.kw)
    assert [k["want_logprobs"] for k in f.kw] == [False] * 20 + [True] * 10 + [False] * 20
    assert g["G1"]["affirms"] and g["G1_AP"]["affirms"] and g["G2"]["affirms"]
    assert g["G2"]["mean_p_yes"] > 0.99 and g["G2"]["held_p233_rule"]
    assert g["G3_PA"]["gap"] == 3 and g["G3_AP"]["gate"] == "PASSED"
    ok += 1; print("  ok  opens: log-prob arm sampled at 32, log-probs on G2 only, "
                   "G1 both orders, G3 gaps")
    # 2. opens: a sampled arm keeps its banked max_tokens and asks no log-probs; a
    #    'less' in the second order is counted there and the first order is unaffected
    f = _Fake(served="Anthropic", g2="No",
              g1=lambda u: "Less." if u.startswith("Consider two separate incidents. In one, an amateur") else "**More**",
              g3=lambda u: "AMATEUR=3 PROFESSIONAL=6" if "AMATEUR=<digit> PRO" in u else "nope")
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("claude", f, frames)
    g = r["G"]
    assert all(k["max_tokens"] == 256 and not k["want_logprobs"] for k in f.kw)
    assert g["G1"]["counts"]["more"] == 10 and g["G1_AP"]["counts"]["less"] == 10
    assert not g["G1_AP"]["affirms"] and not g["G2"]["affirms"]
    assert "mean_p_yes" not in g["G2"]
    assert g["G3_PA"]["gate"] == "FAILED" and g["G3_PA"]["unparsed_texts"][0] == "nope"
    assert g["G3_AP"]["gap"] == 3                       # PROFESSIONAL minus AMATEUR
    ok += 1; print("  ok  opens: sampled arm, no log-probs; 'less' counted in its order; "
                   "G3 gap is professional minus amateur in either field order")
    # 3. parsers
    assert parse_g1(" *Equally.* ") == "equally" and parse_g1("Equal") == "equally"
    assert parse_g1("More to blame") is None and parse_g1("") is None
    assert parse_g3("professional = 7, amateur = 4") == {"PROFESSIONAL": 7, "AMATEUR": 4}
    assert parse_g3("Amateur=4 Professional=7") == {"PROFESSIONAL": 7, "AMATEUR": 4}
    assert parse_g3("PROFESSIONAL=10 AMATEUR=4") is None
    assert parse_g3("PROFESSIONAL=7") is None
    assert parse_g3("PROFESSIONAL=7 AMATEUR=4 PROFESSIONAL=6") is None
    ok += 1; print("  ok  parsers: tolerant of case, order and dress; refuse two digits, a "
                   "missing field, a repeated field, extra words")
    # 4. refuses: the prompt on the wire is not the frozen one
    expect_exit(lambda: read_arm("gpt4o", _Fake(tamper=True), frames),
                "logged prompt hash differs from the frozen hash")
    # 5. refuses: tampered frames file
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "general_principle_frames_tamper.json")
    open(tmp, "w").write(open(f"{R}/{FRAMES}").read().replace("amateur", "amateur "))
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
    # 7. an empty response is retried, not read as a new provider
    f = _Fake(served="xAI"); f.empty_once = True
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("grok43_s", f, frames, wait=0)
    assert f.calls == 51 and len(r["empty_responses_retried"]) == 1
    ok += 1; print("  ok  opens: an empty response is retried and recorded")
    # 8. ceilings within the ruled cap, over run syllogism_duty's arms
    assert sum(ARM_CAP.values()) <= RUN_CAP and set(ARM_CAP) == set(READ_ARMS)
    ok += 1; print(f"  ok  arm ceilings sum to ${sum(ARM_CAP.values()):.3f}, within "
                   f"${RUN_CAP}")
    # 9. the five frozen prompts are what the reader builds
    for k in KEYS:
        build(frames, k)
    assert "less, more, or equally" in frames["prompts"]["G1_AP"]["user"]
    ok += 1; print("  ok  opens: all five prompts build to their frozen hashes")
    print(f"selftest {ok}/9")
    return 0 if ok == 9 else 1


if __name__ == "__main__":
    sys.exit(main())

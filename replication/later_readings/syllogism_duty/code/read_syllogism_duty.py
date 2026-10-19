#!/usr/bin/env python3
"""read_syllogism_duty.py : syllogism_duty, the principle (A), the same-session bare re-read (R) and the
structured prompt (B), on the five duty pairs with neutral sentences.

    python3 scripts/read_syllogism_duty.py --arm gpt4o
    python3 scripts/read_syllogism_duty.py --arm gpt4o --deadline 2026-10-13T18:00:00Z
    python3 scripts/read_syllogism_duty.py --selftest          # offline, no network

Pre-registration: records/PREREG_syllogism_duty_SYLLOGISM_DUTY.md (Amendment 0 and the ruling of
2026-10-13: defaults on A0.1, A0.2, A0.9, A0.11 and A0.13; YES on A0.12, the re-read).

  A  ten calls per pair, in the arm's banked readout (log-prob P(yes) or sampled yes/no),
     with prevention_paraphrase's settings, as practical_syllogism's A.
  R  the bare separate cases, ten draws per leg, on the BANKED SEPARATE-CASE WIRE
     (`probe_duty_pairs.wire_config()`), called exactly as duty_hair_dye's reader called it. Two
     things are asserted before the first call, so the re-read is the banked reading
     repeated and not a new one: the wire's settings hash to the `wire_sha` the database
     carries for the arm's banked bare cells, and each prompt hashes to the prompt hash
     logged on the banked duty_pairs or duty_hair_dye call for that pair and leg.
  B  the structured prompt, ten draws per leg, SAMPLED at temperature 1 on every arm (the
     log-prob arms at 32 tokens), as practical_syllogism's B.

Order per arm: A, then R, then B, so the two quantities syllogism_duty.P3 differences are read
minutes apart.
"""
import argparse, glob, hashlib, json, os, re, sqlite3, statistics, sys, time

R = os.environ.get("AI_ETHICS_ROOT") or os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
from run_rivals import parse_yn, lp_yn
from read_prevention_paraphrase import ARMS as ARMS231, Unread, msgs_hash

FRAMES = "records/frames.json"
FRAMES_SHA = "ae17c72b9a38e007be560eb9deb75079c90c2c53fe3e8387ded2945a7996df97"
F220 = "records/frames.json"
F220_SHA = "ea34a1b8d0eed2c923b28e7a9df366bc11a543843c61d6a51ca0e2794ebeaa83"
DB = "results/results.sqlite"
DB_SHA = "90bb767edb5152887bb38d7c797d99c9dd846edd15b67d8eab19614ac862b3b9"
READ_ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
             "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")
ARMS = {a: ARMS231[a] for a in READ_ARMS}
PAIRS = ("1", "3", "4", "5", "7")
LEGS = ("PRO", "PRIV")
A_DRAWS = B_DRAWS = R_DRAWS = 10
B_MT_LOGPROB_ARMS = 32
GATE_MASS = 0.70
B_GATE = 7
# ── SPEND: twice each arm's estimate (A0.14), at least $0.02; their sum is under the
# ruled $1.25, so no arm can spend the run past its cap even at its own ceiling ───────
EST_USD = {"claude": 0.1437, "deepseek": 0.0010, "deepseek_s": 0.0010, "gemma27b": 0.0025,
           "gpt4o": 0.1067, "gpt6l_s": 0.0050, "gpt6s_s": 0.0990, "grok43_s": 0.0570,
           "haiku_s": 0.0527, "kimi": 0.0473, "llama70b": 0.0310, "mistral24b": 0.0027,
           "qwen80b": 0.0057}
ARM_CAP = {a: max(0.02, round(2 * e, 3)) for a, e in EST_USD.items()}
RUN_CAP = 1.25
assert sum(ARM_CAP.values()) <= RUN_CAP, sum(ARM_CAP.values())

B_RX = re.compile(r"ROLE\W*(professional|private)\b.*?PRINCIPLE\W*(yes|no)\b"
                  r".*?BLAME\W*([0-9])(?![0-9])", re.I | re.S)


def parse_b(t):
    m = B_RX.search(t or "")
    if not m:
        return None
    return {"ROLE": m.group(1).lower(), "PRINCIPLE": m.group(2).lower(),
            "BLAME": int(m.group(3))}


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


# ── R: THE BANKED SEPARATE-CASE READING, REBUILT AND PROVED IDENTICAL ─────────────────
def banked_prompt16():
    """{(pair, leg): prompt hash} from the banked duty_pairs (pairs 1, 3, 4, 5) and duty_hair_dye
    (pair 7) separate-case BLAME calls. Every arm sent the same messages, so each key must
    carry exactly one hash."""
    out = {}
    for run in ("225", "228"):
        for p in glob.glob(f"{R}/runs/run{run}/logs/**/*.jsonl", recursive=True):
            for line in open(p):
                if "|sep|p" not in line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                m = re.match(rf"run{run}\|[^|]+\|sep\|p(\d)\|(PRO|PRIV)\|", d.get("label", ""))
                if m and d.get("prompt_sha256_16"):
                    out.setdefault((m.group(1), m.group(2)), set()).add(d["prompt_sha256_16"])
    return out


def r_prompts(frames):
    f220 = json.load(open(f"{R}/{F220}"))
    if fsha(f"{R}/{F220}") != F220_SHA:
        sys.exit("REFUSING: frames.json sha differs from the banked one")
    body, system = f220["blame"]["body"], f220["blame"]["system"]
    banked = banked_prompt16()
    out = {}
    for pr in PAIRS:
        for leg in LEGS:
            b = frames["prompts"][f"B|p{pr}|{leg}"]
            text = b["user"].split("\n\n")[0]
            if hashlib.sha256(text.encode()).hexdigest() != b["row_text_sha256"]:
                sys.exit(f"REFUSING: p{pr} {leg} case text is not the banked row")
            m = [{"role": "system", "content": system},
                 {"role": "user", "content": body.format(item=text, agent="Alaric")}]
            h16 = msgs_hash(m)[:16]
            got = banked.get((pr, leg), set())
            if got != {h16}:
                sys.exit(f"REFUSING: R p{pr} {leg} prompt {h16} is not the banked separate "
                         f"case's prompt (banked logs carry {sorted(got)})")
            out[(pr, leg)] = (m, h16)
    return out


def r_wire(arm):
    """The arm's banked separate-case wire, asserted against the database's wire_sha for
    its banked bare cells on these pairs."""
    import probe_duty_pairs as PR
    from duty_db import _wire_sha
    w = PR.wire_config().get(arm, {}).get("sep")
    if not w:
        sys.exit(f"REFUSING: no banked separate-case wire for {arm}")
    if fsha(f"{R}/{DB}") != DB_SHA:
        sys.exit("REFUSING: the database is not the one the comparands were frozen from")
    con = sqlite3.connect(f"file:{R}/{DB}?mode=ro", uri=True)
    shas = {r[0] for r in con.execute(
        "SELECT DISTINCT wire_sha FROM duty_cells WHERE arm = ? AND question = 'BLAME' "
        "AND condition = 'bare' AND preferred = 1 AND status = 'read' AND pair_id IN "
        "('1','3','4','5','7')", (arm,))}
    if shas != {_wire_sha(w)}:
        sys.exit(f"REFUSING: {arm} separate-case wire {_wire_sha(w)} is not the banked "
                 f"bare cells' wire {sorted(shas)}")
    return w


def read_arm(arm, h, frames, deadline=None, wait=60, rp=None, rw=None):
    model, prov, served_want, readout, mt, top_k, _ = ARMS[arm]
    logp = readout == "logprob"
    rp = rp if rp is not None else r_prompts(frames)
    rw = rw if rw is not None else r_wire(arm)
    served, served_models, temps, empties = set(), set(), set(), []

    def call(m, label, want16, kind):
        while True:
            try:
                if kind == "R":       # exactly duty_hair_dye's call
                    x = h.rate(rw["model"], rw["provider"], messages=m, mode="chat",
                               temperature=rw["temperature"], max_tokens=rw["max_tokens"],
                               want_logprobs=rw["want_logprobs"], reasoning=rw["reasoning"],
                               label=label)
                else:
                    x = h.rate(model, prov, messages=m, mode="chat",
                               max_tokens=(B_MT_LOGPROB_ARMS if (logp and kind == "B")
                                           else mt),
                               top_k=top_k or 20, label=label, reasoning_off=True,
                               want_logprobs=(logp and kind == "A"))
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

    out = {"A": {}, "R": {}, "B": {}}
    for pr in PAIRS:                                    # ── A ──
        m, ph = build(frames, f"A|p{pr}")
        draws = []
        for d in range(A_DRAWS):
            x = call(m, f"syllogism_duty|{arm}|A|p{pr}|d{d}", ph[:16], "A")
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
            n_yes = None
            held = p is not None and p >= 0.90                     # A0.5
        else:
            ans = [r["answer"] for r in draws]
            parsed = [a for a in ans if a is not None]
            p = (sum(a == "yes" for a in parsed) / len(parsed)) if parsed else None
            mass = len(parsed) / A_DRAWS
            n_yes = sum(a == "yes" for a in ans)
            held = n_yes >= 9                                     # unparsed counts against
        gate = "PASSED" if mass >= GATE_MASS else "FAILED"
        out["A"][f"p{pr}"] = {
            "pair": pr, "p_yes": p, "answer_mass": mass, "gate": gate, "n_yes": n_yes,
            "n_asked": A_DRAWS, "principle_held": bool(held and gate == "PASSED"),
            "rule": ("mean P(yes) >= 0.90 (A0.5)" if logp
                     else "at least 9 of 10 parsed 'yes'; unparsed counts against"),
            "prompt_sha256": ph, "draws": draws}
        print(f"   A p{pr}  p_yes {p}  mass {mass:.3f}  held "
              f"{out['A'][f'p{pr}']['principle_held']}  ${h.spent:.4f}", flush=True)

    for pr in PAIRS:                                    # ── R ──
        for leg in LEGS:
            m, h16 = rp[(pr, leg)]
            vals, raws, void = [], [], 0
            for d in range(R_DRAWS):
                x = call(m, f"syllogism_duty|{arm}|R|p{pr}|{leg}|d{d}", h16, "R")
                raws.append((x.get("raw_text") or "")[:24])
                if x.get("ev") is not None:
                    vals.append(float(x["ev"]))
                else:
                    g = re.search(r"\d", x.get("raw_text") or "")
                    if g:
                        vals.append(float(g.group(0)))
                    else:
                        void += 1
            out["R"][f"p{pr}|{leg}"] = {
                "pair": pr, "leg": leg, "n_asked": R_DRAWS, "n_parsed": len(vals),
                "n_void": void, "mean": statistics.mean(vals) if vals else None,
                "values": vals, "raw_sample": raws[:3], "prompt_sha256_16": h16,
                "readout": "logprob ev" if rw["want_logprobs"] else "first digit of text"}
            c = out["R"][f"p{pr}|{leg}"]
            print(f"   R p{pr} {leg:4s} parsed {len(vals):2d}  mean {c['mean']}  "
                  f"${h.spent:.4f}", flush=True)

    for pr in PAIRS:                                    # ── B ──
        for leg in LEGS:
            key = f"B|p{pr}|{leg}"
            m, ph = build(frames, key)
            want_role = frames["prompts"][key]["expected_role"]
            draws = []
            for d in range(B_DRAWS):
                x = call(m, f"syllogism_duty|{arm}|{key}|d{d}", ph[:16], "B")
                txt = x.get("answer_text", x["raw_text"])
                draws.append({"text": txt, "parsed": parse_b(txt),
                              "reasoned_despite_off": bool(x.get("reasoning_text_len"))})
            ok = [r["parsed"] for r in draws if r["parsed"]]
            bl = [r["BLAME"] for r in ok]
            out["B"][f"p{pr}|{leg}"] = {
                "pair": pr, "leg": leg, "expected_role": want_role, "n_asked": B_DRAWS,
                "n_parsed": len(ok), "gate_parse": "PASSED" if len(ok) >= B_GATE else "FAILED",
                "blame_mean": statistics.mean(bl) if bl else None, "blame_values": bl,
                "n_role_correct": sum(r["ROLE"] == want_role for r in ok),
                "n_principle_yes": sum(r["PRINCIPLE"] == "yes" for r in ok),
                "unparsed_texts": [r["text"] for r in draws if not r["parsed"]],
                "prompt_sha256": ph, "draws": draws}
            c = out["B"][f"p{pr}|{leg}"]
            print(f"   B p{pr} {leg:4s} parsed {len(ok):2d}  role ok {c['n_role_correct']}  "
                  f"blame {c['blame_mean']}  ${h.spent:.4f}", flush=True)
    out.update({"provider_served": sorted(served), "served_model": sorted(served_models),
                "served_model_constant": len(served_models) == 1,
                "temperature": sorted(t for t in temps if t is not None),
                "empty_responses_retried": empties, "wire_R": rw})
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
    rp, rw = r_prompts(frames), r_wire(a.arm)          # refusals before any call
    os.makedirs(f"{R}/runs/syllogism_duty/logs", exist_ok=True)
    h = Harness(f"{R}/runs/syllogism_duty/logs/or_{a.arm}.jsonl", cap_usd=ARM_CAP[a.arm])
    import calendar
    dl = (calendar.timegm(time.strptime(a.deadline, "%Y-%m-%dT%H:%M:%SZ"))
          if a.deadline else None)
    t0 = time.time()
    model, prov, served_want, readout, mt, top_k, _ = ARMS[a.arm]
    out = {"run": "233", "arm": a.arm, "model": model, "provider_requested": prov,
           "provider_banked": served_want, "readout_A": readout, "readout_B": "sampled",
           "max_tokens_A": mt,
           "max_tokens_B": B_MT_LOGPROB_ARMS if readout == "logprob" else mt,
           "top_k": top_k, "frames": FRAMES, "frames_sha256": FRAMES_SHA,
           "arm_cap_usd": ARM_CAP[a.arm],
           "prereg": "records/PREREG_syllogism_duty_SYLLOGISM_DUTY.md"}
    try:
        out.update(read_arm(a.arm, h, frames, dl, rp=rp, rw=rw))
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
    def __init__(self, served="OpenAI", tamper=False, a_answer="Yes",
                 b_answer="ROLE=private PRINCIPLE=yes BLAME=4", r_digit="6"):
        self.spent, self.calls, self.served, self.tamper = 0.0, 0, served, tamper
        self.a_answer, self.b_answer, self.r_digit, self.kw = a_answer, b_answer, r_digit, []

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
        sysm = messages[0]["content"]
        if "ROLE=" in sysm:
            ans, ev = self.b_answer, None
        elif "rating instrument" in sysm:
            ans, ev = self.r_digit, (float(self.r_digit) if want_logprobs else None)
        else:
            ans, ev = self.a_answer, None
        return {"prompt_sha256_16": msgs_hash(m)[:16], "provider_served": self.served,
                "served_model": model, "temperature": 1.0, "reasoning_text_len": 0,
                "raw_text": ans, "answer_text": ans, "ev": ev,
                "top_tokens": [{"t": "Yes", "lp": -0.01}, {"t": "No", "lp": -5.0},
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

    # 0. R's prompts are the banked ones, and every arm's R wire is the banked one
    rp = r_prompts(frames)
    assert len(rp) == 10
    for arm in READ_ARMS:
        r_wire(arm)
    ok += 1; print("  ok  opens: R prompts hash to the banked logs; 13 R wires match the "
                   "database's wire_sha")
    # 1. opens: log-prob arm; A by log-prob, R on the banked wire, B sampled at 32 tokens
    f = _Fake()
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("gpt4o", f, frames, rp=rp)
    assert f.calls == 250 and len(r["A"]) == 5 and len(r["R"]) == 10 and len(r["B"]) == 10
    assert r["A"]["p1"]["principle_held"] and r["A"]["p1"]["p_yes"] > 0.99
    assert f.kw[0]["want_logprobs"] and f.kw[0]["max_tokens"] == 1
    assert f.kw[50]["want_logprobs"] and f.kw[50]["reasoning"] == {"enabled": False}
    assert r["R"]["p3|PRO"]["mean"] == 6.0 and r["R"]["p3|PRO"]["readout"] == "logprob ev"
    assert not f.kw[150]["want_logprobs"] and f.kw[150]["max_tokens"] == 32
    c = r["B"]["p1|PRIV"]
    assert c["n_parsed"] == 10 and c["blame_mean"] == 4 and c["n_role_correct"] == 10
    assert r["B"]["p1|PRO"]["n_role_correct"] == 0          # ROLE=private on the PRO leg
    ok += 1; print("  ok  opens: log-prob arm, A by log-prob, R on the banked wire, "
                   "B sampled at 32; ROLE scored against the leg")
    # 2. opens: sampled arm; A 'no' is not held; unparsed B kept; R by first digit
    f = _Fake(served="Anthropic", a_answer="No", b_answer="I would rather not say.")
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("claude", f, frames, rp=rp)
    assert r["A"]["p4"]["n_yes"] == 0 and not r["A"]["p4"]["principle_held"]
    c = r["B"]["p7|PRO"]
    assert c["n_parsed"] == 0 and c["gate_parse"] == "FAILED"
    assert c["unparsed_texts"][0] == "I would rather not say."
    assert r["R"]["p5|PRIV"]["mean"] == 6.0 and r["R"]["p5|PRIV"]["readout"] == \
        "first digit of text"
    assert f.kw[150]["max_tokens"] == 256 and f.kw[60]["max_tokens"] == 256
    ok += 1; print("  ok  opens: sampled arm, A 'no' not held, unparsed B kept, R first digit")
    # 3. the B parser
    assert parse_b("**ROLE=** Private, PRINCIPLE = <yes> BLAME=3") == {
        "ROLE": "private", "PRINCIPLE": "yes", "BLAME": 3}
    assert parse_b("PRINCIPLE=yes ROLE=private BLAME=3") is None
    assert parse_b("ROLE=private PRINCIPLE=yes") is None
    assert parse_b("ROLE=private PRINCIPLE=yes BLAME=10") is None
    assert parse_b("ROLE=amateur PRINCIPLE=yes BLAME=3") is None
    ok += 1; print("  ok  B parser: tolerant of form; refuses wrong order, missing, two "
                   "digits, a role outside the two")
    # 4. refuses: the prompt on the wire is not the frozen one
    expect_exit(lambda: read_arm("gpt4o", _Fake(tamper=True), frames, rp=rp),
                "logged prompt hash differs from the frozen hash")
    # 5. refuses: tampered frames file
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "syllogism_duty_frames_tamper.json")
    open(tmp, "w").write(open(f"{R}/{FRAMES}").read().replace("Alaric", "Alaric "))
    expect_exit(lambda: load_frames(tmp), "frames file whose sha differs")
    os.remove(tmp)
    # 6. refuses: an R prompt that is not the banked separate case
    bad = json.loads(json.dumps(frames))
    bad["prompts"]["B|p3|PRO"]["user"] = bad["prompts"]["B|p3|PRO"]["user"].replace(
        "fifty", "sixty", 1)
    expect_exit(lambda: r_prompts(bad), "R case text that is not the banked row")
    # 7. a changed provider makes the arm UNREAD, not moved
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            read_arm("qwen80b", _Fake(served="Nebius"), frames, rp=rp)
        raise AssertionError("changed provider was accepted")
    except Unread as e:
        assert "Nebius" in str(e); ok += 1
        print("  ok  refuses: changed provider -> UNREAD with the reason")
    # 8. an empty response is retried, not read as a new provider
    f = _Fake(served="xAI"); f.empty_once = True
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("grok43_s", f, frames, wait=0, rp=rp)
    assert f.calls == 251 and len(r["empty_responses_retried"]) == 1
    assert r["provider_served"] == ["xAI"]
    ok += 1; print("  ok  opens: an empty response is retried and recorded, arm READ")
    # 9. the arm ceilings sum within the ruled cap
    assert sum(ARM_CAP.values()) <= RUN_CAP and set(ARM_CAP) == set(READ_ARMS)
    ok += 1; print(f"  ok  arm ceilings sum to ${sum(ARM_CAP.values()):.3f}, within "
                   f"${RUN_CAP}")
    print(f"selftest {ok}/10")
    return 0 if ok == 10 else 1


if __name__ == "__main__":
    sys.exit(main())

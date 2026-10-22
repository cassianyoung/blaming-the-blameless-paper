#!/usr/bin/env python3
"""read_serial_pipeline.py : serial_pipeline, the serial pipeline check. One arm per process.

    python3 scripts/read_serial_pipeline.py --arm gpt4o
    python3 scripts/read_serial_pipeline.py --arm gpt4o --deadline 2026-10-21T12:00:00Z
    python3 scripts/read_serial_pipeline.py --selftest          # offline, no network

Pre-registration: records/PREREG_serial_pipeline_PIPELINE.md (instruction verbatim, Amendment 0).
Frames: records/frames.json, sha pinned below, built by build_serial_pipeline_frames.py.

Per scenario (6) and role (P0, N, C), in this order and in one session:
  1A  summary       one call, temperature 0 (A0.4), text kept verbatim
  1B  conclusion    one call, temperature 0, text kept verbatim
  2A  scoring with 1A's text forward    10 draws, the arm's banked DIRECT readout
  2B  scoring with 1B's text forward    10 draws, the arm's banked DIRECT readout
  D   the direct verdict                10 draws, the arm's banked DIRECT readout
  O   the one-answer prompt (practical_syllogism B) 10 draws, SAMPLED on every arm, as banked

Arm settings are prevention_paraphrase's (as practical_syllogism), imported, never retyped. Every frozen prompt is
hashed before the call and the harness's logged wire hash is compared after it. Call 2's
prompt is built by the builder's own `call2_user` and DIFF-CHECKED against the direct
prompt before it is sent: same system, user turn minus the findings block identical.
A served provider other than the banked one makes the arm UNREAD.
"""
import argparse, hashlib, json, os, statistics, sys, time

R = os.environ.get("PAPER_ROOT") or os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
from run_rivals import parse_digit, lp_digits
from read_prevention_paraphrase import ARMS as ARMS231, Unread, msgs_hash
from read_practical_syllogism import parse_b, B_MT_LOGPROB_ARMS
from build_serial_pipeline_frames import call2_user, call2_diff_ok

FRAMES = "records/frames.json"
FRAMES_SHA = "04fd25ef2970c1f8b3b06714be9efeb7b1438d475c99a7a8bd50b8ebc8502403"
READ_ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
             "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")
ARMS = {a: ARMS231[a] for a in READ_ARMS}
SCEN = ("bicycle", "ladder", "prawns_home", "prawns_restaurant", "scaffolding", "cheque")
ROLES = ("P0", "N", "C")
DRAWS = 10
EXTRACT_MT = 256          # A0.4: call 1's floor; an arm banked higher keeps its own
EXTRACT_RETRIES = 3       # an empty call-1 text is re-asked, then the cell is void
# A0.9: each arm's cap is twice its estimate, floored at $0.05; the caps sum to $4.09,
# which is the run's effective cap (twice the $1.96 estimate is $3.92; the floors on six
# sub-cent arms add $0.17)
ARM_CAP_USD = {"claude": 0.86, "deepseek": 0.05, "deepseek_s": 0.05, "gemma27b": 0.05,
               "gpt4o": 0.85, "gpt6l_s": 0.05, "gpt6s_s": 0.72, "grok43_s": 0.39,
               "haiku_s": 0.37, "kimi": 0.39, "llama70b": 0.21, "mistral24b": 0.05,
               "qwen80b": 0.05}


def load_frames(path, want=None):
    blob = open(path, "rb").read()
    got = hashlib.sha256(blob).hexdigest()
    want = want if want is not None else FRAMES_SHA
    if want is None:
        sys.exit("REFUSING: FRAMES_SHA is not pinned; freeze the frames first")
    if got != want:
        sys.exit(f"REFUSING: frames sha {got[:16]} != frozen {want[:16]}")
    return json.loads(blob)


def frozen(cell, k):
    m, ph = cell[k]["messages"], cell[k]["prompt_sha256"]
    if msgs_hash(m) != ph:
        sys.exit(f"REFUSING: {cell['scenario']}|{cell['role']} {k} does not hash to frozen")
    return m, ph


def read_arm(arm, h, frames, deadline=None, wait=60):
    model, prov, served_want, readout, mt, top_k, _ = ARMS[arm]
    logp = readout == "logprob"
    served, served_models, temps, empties, refusals = set(), set(), {}, [], []
    t1 = {"value": 0.0, "refused": None}        # call 1's temperature, A0.4

    def call(m, label, want, *, sampled, max_tokens, temperature=1.0, lp=False):
        while True:
            try:
                x = h.rate(model, prov, messages=m, mode="chat", temperature=temperature,
                           max_tokens=max_tokens, top_k=top_k or 20, label=label,
                           reasoning_off=True, want_logprobs=lp)
            except RuntimeError as e:
                # ── AMENDMENT 1 (ruled 2026-10-20, during the read): A PROVIDER'S
                # MODERATION REFUSAL IS A REFUSED DRAW, NOT AN OUTAGE ──────────────────
                # xAI answered grok's scaffolding|N|2B prompt with HTTP 403
                # {"code":"permission-denied","error":"I'm sorry, I can't help with
                # that request."} on every attempt. Retried as an outage it would have
                # run to the deadline and written the whole arm UNREAD. It is kept
                # verbatim, counted as unparsed, never coerced; the gate decides.
                if "permission-denied" in str(e):
                    refusals.append({"label": label, "error": str(e)[:600]})
                    print(f"   REFUSED by the provider (permission-denied): {label}",
                          flush=True)
                    return {"refused": True, "error": str(e)[:600]}
                # A0.4: temperature 0 "where the provider allows". A refusal of the
                # call-1 temperature is recorded once and call 1 falls back to 1.0.
                if temperature == 0.0 and t1["refused"] is None:
                    t1.update(value=1.0, refused=str(e)[:300])
                    print(f"   temperature 0 refused ({str(e)[:100]}); call 1 at 1.0",
                          flush=True)
                    temperature = 1.0
                    continue
                if deadline and time.time() > deadline:
                    raise Unread(f"provider {prov} still failing at the deadline: {e}")
                print(f"   call failed ({str(e)[:120]}); waiting {wait}s", flush=True)
                time.sleep(wait)
                continue
            if x.get("provider_served") is None and not (x.get("raw_text") or "").strip():
                empties.append(label)                 # practical_syllogism's rule: retried, not moved
                if deadline and time.time() > deadline:
                    raise Unread(f"empty responses from {prov} still at the deadline")
                time.sleep(wait)
                continue
            break
        if x["prompt_sha256_16"] != want[:16]:
            sys.exit(f"REFUSING: {label}: logged prompt hash {x['prompt_sha256_16']} != "
                     f"built {want[:16]}. The prompt on the wire is not the built one.")
        if x["provider_served"] != served_want:
            raise Unread(f"served by {x['provider_served']!r}, banked on {served_want!r}")
        served.add(x["provider_served"]); served_models.add(x["served_model"])
        temps[x["temperature"]] = temps.get(x["temperature"], 0) + 1
        return x

    def extract(m, ph, label):
        """Call 1: one reading, kept verbatim. An empty text is re-asked; then void."""
        tries = []
        for t in range(1 + EXTRACT_RETRIES):
            x = call(m, f"{label}|t{t}", ph, sampled=True, temperature=t1["value"],
                     max_tokens=max(EXTRACT_MT, mt if not logp else 0))
            if x.get("refused"):
                tries.append({"text": None, "refused": True, "error": x["error"]})
                return {"text": None, "void": True, "refused": True, "attempts": tries}
            txt = x.get("answer_text", x["raw_text"]) or ""
            tries.append({"text": txt, "temperature": x["temperature"],
                          "reasoned_despite_off": bool(x.get("reasoning_text_len")),
                          "completion_tokens": (x.get("usage") or {}).get(
                              "completion_tokens")})
            if txt.strip():
                return {"text": txt, "void": False, "attempts": tries}
        return {"text": None, "void": True, "attempts": tries}

    def digit_cell(m, ph, label):
        """The banked direct readout: log-prob EV on a log-prob arm, a sampled digit
        otherwise. The same function scores D, 2A and 2B."""
        evs, probs, draws, void = [], [], [], 0
        for d in range(DRAWS):
            x = call(m, f"{label}|d{d}", ph, sampled=not logp, lp=logp,
                     max_tokens=1 if logp else mt)
            if x.get("refused"):
                void += 1
                draws.append({"text": None, "refused": True, "error": x["error"]})
                continue
            txt = x.get("answer_text", x["raw_text"])
            rec = {"text": txt, "reasoned_despite_off": bool(x.get("reasoning_text_len"))}
            if logp:
                if x["ev"] is None:
                    void += 1
                else:
                    q = lp_digits(x)
                    probs.append(q); evs.append(x["ev"])
                    rec.update(ev=x["ev"], digit_mass=x["digit_mass"])
            else:
                v = parse_digit(txt)
                rec["digit"] = v
                if v is None:
                    void += 1
                else:
                    evs.append(float(v))
            draws.append(rec)
        o = {"n_asked": DRAWS, "n_parsed": len(evs), "void": void,
             "gate_parse": "PASSED" if len(evs) >= 7 else "FAILED",
             "blame_mean": statistics.mean(evs) if evs else None,
             "prompt_sha256": ph, "draws": draws}
        if logp:
            o["blame_mass_0_3"] = (statistics.mean(sum(q[k] for k in range(4))
                                                   for q in probs) if probs else None)
            o["digit_mass"] = (statistics.mean(r["digit_mass"] for r in draws
                                               if "digit_mass" in r) if probs else None)
        else:
            o["blame_mass_0_3"] = (sum(v <= 3 for v in evs) / len(evs)) if evs else None
        return o

    def one_answer(m, ph, label):
        draws = []
        for d in range(DRAWS):
            x = call(m, f"{label}|d{d}", ph, sampled=True,
                     max_tokens=B_MT_LOGPROB_ARMS if logp else mt)
            if x.get("refused"):
                draws.append({"text": None, "parsed": None, "refused": True,
                              "error": x["error"]})
                continue
            txt = x.get("answer_text", x["raw_text"])
            draws.append({"text": txt, "parsed": parse_b(txt),
                          "reasoned_despite_off": bool(x.get("reasoning_text_len"))})
        ok = [r["parsed"] for r in draws if r["parsed"]]
        bl = [r["BLAME"] for r in ok]
        return {"n_asked": DRAWS, "n_parsed": len(ok),
                "gate_parse": "PASSED" if len(ok) >= 7 else "FAILED",
                "blame_mean": statistics.mean(bl) if bl else None,
                "blame_mass_0_3": (sum(b <= 3 for b in bl) / len(bl)) if bl else None,
                "p_prevent_yes": (sum(r["PREVENT"] == "yes" for r in ok) / len(ok)
                                  if ok else None),
                "prompt_sha256": ph, "draws": draws}

    cells = {}
    for scen in SCEN:
        for role in ROLES:
            key = f"{scen}|{role}"
            cell = frames["cells"][key]
            lab = f"serial_pipeline|{arm}|{key}"
            m1a, h1a = frozen(cell, "1A")
            m1b, h1b = frozen(cell, "1B")
            md, hd = frozen(cell, "D")
            mo, ho = frozen(cell, "O")
            out = {"scenario": scen, "role": role}
            out["1A"] = extract(m1a, h1a, f"{lab}|1A")
            out["1B"] = extract(m1b, h1b, f"{lab}|1B")
            for c2, src in (("2A", "1A"), ("2B", "1B")):
                f = out[src]["text"]
                if f is None:
                    out[c2] = {"void": True, "reason": f"call {src} returned no text"}
                    continue
                m2 = [md[0], {"role": "user", "content": call2_user(md[1]["content"], f)}]
                if not call2_diff_ok(md, m2, f):
                    sys.exit(f"REFUSING: {lab} {c2} fails the diff against the direct prompt")
                out[c2] = digit_cell(m2, msgs_hash(m2), f"{lab}|{c2}")
                out[c2]["diff_against_direct"] = "OK"
            out["D"] = digit_cell(md, hd, f"{lab}|D")
            out["O"] = one_answer(mo, ho, f"{lab}|O")
            cells[key] = out
            print(f"   {key:26s} 2A {out['2A'].get('blame_mean')}  2B "
                  f"{out['2B'].get('blame_mean')}  D {out['D']['blame_mean']}  O "
                  f"{out['O']['blame_mean']}  ${h.spent:.4f}", flush=True)
    return {"cells": cells, "provider_served": sorted(served),
            "served_model": sorted(served_models),
            "served_model_constant": len(served_models) == 1,
            "temperature_counts": {str(k): v for k, v in temps.items()},
            "call1_temperature": t1["value"], "call1_temperature0_refused": t1["refused"],
            "empty_responses_retried": empties, "provider_refusals": refusals}


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
    os.makedirs(f"{R}/runs/serial_pipeline/logs", exist_ok=True)
    h = Harness(f"{R}/runs/serial_pipeline/logs/or_{a.arm}.jsonl", cap_usd=ARM_CAP_USD[a.arm])
    import calendar
    dl = (calendar.timegm(time.strptime(a.deadline, "%Y-%m-%dT%H:%M:%SZ"))
          if a.deadline else None)
    t0 = time.time()
    model, prov, served_want, readout, mt, top_k, _ = ARMS[a.arm]
    out = {"run": "240", "arm": a.arm, "model": model, "provider_requested": prov,
           "provider_banked": served_want, "readout_scoring": readout,
           "readout_one_answer": "sampled", "max_tokens_scoring": 1 if readout == "logprob"
           else mt, "max_tokens_call1": max(EXTRACT_MT, mt if readout != "logprob" else 0),
           "top_k": top_k, "frames": FRAMES, "frames_sha256": FRAMES_SHA,
           "prereg": "records/PREREG_serial_pipeline_PIPELINE.md", "arm_cap_usd": ARM_CAP_USD[a.arm]}
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
    def __init__(self, served="OpenAI", tamper_call2=False, refuse_t0=False,
                 c1b="Alaric could not reasonably have prevented this."):
        self.spent, self.calls, self.served = 0.0, 0, served
        self.tamper_call2, self.refuse_t0, self.c1b = tamper_call2, refuse_t0, c1b
        self.kw, self.msgs = [], []

    def rate(self, model, provider, messages=None, want_logprobs=True, temperature=1.0,
             **k):
        if self.refuse_t0 and temperature == 0.0:
            raise RuntimeError("HTTP 400: temperature 0 is not supported")
        self.calls += 1
        self.kw.append(dict(k, want_logprobs=want_logprobs, temperature=temperature))
        self.msgs.append(messages)
        m = messages
        u = messages[-1]["content"]
        if self.tamper_call2 and u.startswith("Extracted findings"):
            m = [messages[0], {"role": "user", "content": u + " "}]
        if messages[0]["role"] == "user":                       # call 1
            ans = self.c1b if "prevented this?" in u else "Alaric lent a bicycle."
        elif "PREVENT=" in messages[0]["content"]:
            ans = "PREVENT=no PRINCIPLE=no BLAME=1"
        else:
            ans = "2"
        return {"prompt_sha256_16": msgs_hash(m)[:16], "provider_served": self.served,
                "served_model": model, "temperature": temperature, "reasoning_text_len": 0,
                "raw_text": ans, "answer_text": ans, "usage": {"completion_tokens": 5},
                "ev": 2.0 if want_logprobs else None, "digit_mass": 1.0,
                "top_tokens": [{"t": "2", "lp": -0.01}, {"t": "1", "lp": -5.0}]}


def selftest():
    import contextlib, io
    frames = json.load(open(f"{R}/{FRAMES}"))
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

    per_cell = 2 + 4 * DRAWS
    # 1. opens: log-prob arm; call 1 at T=0 with 256 tokens, scoring by log-prob at 1
    #    token, one-answer sampled at 32; 18 cells x 42 calls
    f = _Fake()
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("gpt4o", f, frames)
    assert f.calls == 18 * per_cell and len(r["cells"]) == 18, f.calls
    k0 = f.kw[0]
    assert k0["temperature"] == 0.0 and k0["max_tokens"] == 256 and not k0["want_logprobs"]
    assert f.kw[2]["want_logprobs"] and f.kw[2]["max_tokens"] == 1
    assert f.kw[-1]["max_tokens"] == 32 and not f.kw[-1]["want_logprobs"]
    c = r["cells"]["ladder|P0"]
    assert c["2B"]["diff_against_direct"] == "OK" and c["2B"]["blame_mean"] == 2.0
    assert c["O"]["blame_mean"] == 1 and c["1B"]["text"].startswith("Alaric could not")
    ok += 1; print("  ok  opens: log-prob arm, T=0 call 1, log-prob scoring, sampled O")
    # 2. THE OBSERVABLE: call 2's wire prompt carries call 1's text, and only that differs
    sent2b = [m for m in f.msgs if m[0]["role"] == "system"
              and m[1]["content"].startswith("Extracted findings")
              and "could not reasonably" in m[1]["content"]]
    assert len(sent2b) == 18 * DRAWS
    d = frames["cells"]["ladder|P0"]["D"]["messages"]
    assert any(m[1]["content"].endswith(d[1]["content"]) and m[0] == d[0] for m in sent2b)
    ok += 1; print("  ok  call 1B's text reaches call 2B's wire prompt, direct prompt intact")
    # 3. opens: sampled arm keeps its banked max_tokens; T=0 refused -> recorded, falls back
    f = _Fake(served="Anthropic", refuse_t0=True)
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("claude", f, frames)
    assert r["call1_temperature"] == 1.0 and "not supported" in r["call1_temperature0_refused"]
    assert f.kw[2]["max_tokens"] == 256 and not f.kw[2]["want_logprobs"]
    ok += 1; print("  ok  opens: sampled arm; a refused temperature 0 is recorded and falls back")
    # 4. refuses: a call-2 prompt on the wire that is not the built one
    expect_exit(lambda: read_arm("gpt4o", _Fake(tamper_call2=True), frames),
                "call-2 wire prompt differs from the built prompt")
    # 5. the diff check refuses an altered direct part, and an altered system
    md = frames["cells"]["cheque|P0"]["D"]["messages"]
    good = [md[0], {"role": "user", "content": call2_user(md[1]["content"], "x")}]
    assert call2_diff_ok(md, good, "x")
    bad_u = [md[0], {"role": "user", "content": call2_user(md[1]["content"] + ".", "x")}]
    bad_s = [{"role": "system", "content": "Be kind."}, good[1]]
    assert not call2_diff_ok(md, bad_u, "x") and not call2_diff_ok(md, bad_s, "x")
    ok += 1; print("  ok  diff check: passes the construction, refuses altered user or system")
    # 6. refuses: an unpinned or tampered frames file
    expect_exit(lambda: load_frames(f"{R}/{FRAMES}", want="0" * 64), "frames sha mismatch")
    # 7. a changed provider makes the arm UNREAD, not moved
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            read_arm("qwen80b", _Fake(served="Nebius"), frames)
        raise AssertionError("changed provider was accepted")
    except Unread as e:
        assert "Nebius" in str(e); ok += 1
        print("  ok  refuses: changed provider -> UNREAD with the reason")
    # 8. Amendment 1: a provider's permission-denied on one prompt is a refused draw; the
    #    arm stays READ, the cell's gate fails, every other cell is read as normal
    class _Refuser(_Fake):
        def rate(self, model, provider, messages=None, **k):
            u = messages[-1]["content"]
            if u.startswith("Extracted findings") and "scaffolding" in u and \
                    "Nobody came" in u and "could not" in u:
                raise RuntimeError('OpenRouter call failed after 6: HTTP 403: {"error":'
                                   '{"raw":"{\\"code\\":\\"permission-denied\\"}"}}')
            return _Fake.rate(self, model, provider, messages=messages, **k)
    f = _Refuser(served="xAI")
    with contextlib.redirect_stdout(io.StringIO()):
        r = read_arm("grok43_s", f, frames, wait=0)
    c = r["cells"]["scaffolding|N"]["2B"]
    assert c["n_parsed"] == 0 and c["gate_parse"] == "FAILED" and c["void"] == DRAWS
    assert all(d["refused"] for d in c["draws"]) and len(r["provider_refusals"]) == DRAWS
    assert r["cells"]["scaffolding|N"]["2A"]["n_parsed"] == DRAWS
    assert r["cells"]["ladder|N"]["2B"]["n_parsed"] == DRAWS
    ok += 1; print("  ok  opens: a permission-denied draw is refused and kept; the arm is READ")
    print(f"selftest {ok}/8")
    return 0 if ok == 8 else 1


if __name__ == "__main__":
    sys.exit(main())

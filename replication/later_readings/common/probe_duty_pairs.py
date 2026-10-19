#!/usr/bin/env python3
"""duty_pairs §0: the cost probe. One separate-case call and one paired-scores call per arm.

**IT PROBES WITH TEXTS THAT ARE ALREADY FROZEN**, not with duty_pairs's new bank. §1 says
freeze the bank before any call, and the comparison prompts cannot be frozen yet: the
instruction says to use "the pair of names the cmp bank uses" and the cmp bank uses NO
personal names, its own build test refusing any text containing "Alaric". That is a
question for the author, and §0's approval gate is where it belongs.
So the probe uses:

  separate case   prawns_home C from `moral__families__v1.jsonl`, which IS duty_pairs's
                  pair-6 control case verbatim, so it is duty_pairs material
  paired scores   CMPN_home_first from `moral__cmp__v1.jsonl`, the existing instrument

Both are hashed against their banks before the call, per §5. Nothing about the cost per
call depends on which narrative is in the prompt: the prompts are within a few dozen
tokens of each other and the answer is one or two tokens.

**43 CALLS, NOT 44.** §0 says 44, which is 22 arms x 2 readings. Gemini 3.1 Pro is
comparison-only by §3 and §4, so a separate-case call on it would be a reading the run
does not want and would not be used. 21 separate + 22 paired = 43.

Per-arm wire configuration is READ OFF THE BANKED LOGS, never retyped: each arm's
separate-case budget from its deployed_scenarios families read and its paired-scores budget from
its duty_chef_home_comparison/224 CMP read, so "same settings as the existing chef-home-cook reading" is
a fact about the logs rather than a claim.
"""
import argparse
import hashlib
import json
import os
import sys
import time

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import or_harness as OH

FAM = "data/families_bank/moral__families__v1.jsonl"
CMP = "data/cmp_bank/moral__cmp__v1.jsonl"
SEP_SYS = "You are a rating instrument. Reply with a single digit from 0 to 9 and nothing else."
CMPN_SYS = "You are a rating instrument. Reply in exactly the form requested and nothing else."
# the blame body, from records/frames.json, substituted as that run substitutes it
FRAMES = "records/frames.json"


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def banked_text(path, pred, want_sha_field):
    for line in open(os.path.join(R, path)):
        d = json.loads(line)
        if pred(d):
            got = sha(d["text"])
            if got != d[want_sha_field]:
                sys.exit(f"REFUSING: {path} row does not hash to its banked sha")
            return d["text"], got
    sys.exit(f"REFUSING: no matching row in {path}")


def wire_config():
    """{arm: {'sep': {...}, 'cmpn': {...}}} read off the banked logs."""
    import glob
    cfg = {}
    # paired scores: the duty_chef_home_comparison/224 CMP calls
    for p in glob.glob(os.path.join(R, "runs/<the deployed and duty readings>/logs/or_*.jsonl")):
        arm = os.path.basename(p)[3:-6]
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if "CMPN" not in str(d.get("label") or ""):
                continue
            cfg.setdefault(arm, {})["cmpn"] = {
                "model": d.get("model"), "provider": d.get("provider_asked"),
                "max_tokens": d.get("max_tokens"),
                "want_logprobs": bool(d.get("want_logprobs")),
                "reasoning": d.get("reasoning_on_the_wire"),
                "temperature": d.get("temperature") or 1.0}
    # ── SEPARATE CASES: THE FAMILIES BLAME CALLS, WHEREVER THEY WERE LOGGED ─────
    # deployed_scenarios does not hold all of them. The four gpt-6 arms and the two grok arms were
    # read in deployed_scenarios (the sampled ones at mt=1024, the reasoning ones at
    # mt=8192), so a lookup scoped to deployed_scenarios came back MISSING on six of twenty-two
    # and would have silently fallen back to no config at all. The `_bike` logs are
    # excluded: those are the bicycle reads, at mt=8 and mt=16, which is not the budget
    # a multi-sentence separate case was ever read at.
    cand = [q for q in glob.glob(os.path.join(R, "runs/<the deployed and duty readings>/logs/or_*.jsonl"))
            if not os.path.basename(q).endswith("_bike.jsonl")]
    for p in sorted(cand):
        arm = os.path.basename(p)[3:-6]
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            lab = str(d.get("label") or "")
            if "CMP" in lab or "BLAME" not in lab.upper():
                continue
            cfg.setdefault(arm, {}).setdefault("sep", {
                "model": d.get("model"), "provider": d.get("provider_asked"),
                "max_tokens": d.get("max_tokens"),
                "want_logprobs": bool(d.get("want_logprobs")),
                "reasoning": d.get("reasoning_off_on_the_wire"),
                "temperature": d.get("temperature") or 1.0,
                "from_log": os.path.relpath(p, R)})
    return cfg


# the 22 Figure 6 arms, and where each one's separate-case config comes from when its
# own name does not appear in the deployed_scenarios families logs (the reasoning DeepSeek arm is
# banked under `deepseek_r_mt8192` there and as `deepseek_r` in the CMP read)
SEP_ALIAS = {"deepseek_r": "deepseek_r_mt8192"}
CMPN_ONLY = ("gemini_pro",)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap-usd", type=float, default=0.50)
    ap.add_argument("--out", default=os.path.join(R, "records/cost_probe.json"))
    ap.add_argument("--log", default=os.path.join(R, "runs/duty_pairs/logs/probe.jsonl"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if os.path.exists(a.out):
        sys.exit(f"REFUSING: {a.out} exists. Write-once, no override.")

    sep_text, sep_sha = banked_text(
        FAM, lambda d: d.get("family") == "prawns_home" and d.get("role") == "C",
        "sha256")
    cmpn_text, cmpn_sha = banked_text(
        CMP, lambda d: d.get("uid") == "CMPN_home_first", "text_sha256")
    frames = json.load(open(os.path.join(R, FRAMES)))
    blame_body = frames["blame"]["body"]
    agent = "Alaric"
    sep_prompt = blame_body.format(item=sep_text, agent=agent)

    cfg = wire_config()
    import csv
    with open(os.path.join(R, "figures/chef_home.csv")) as fh:
        rows = [r for r in csv.DictReader([l for l in fh if not l.startswith("#")])
                if r["source"] == "api"]
    arms = [r["model"] for r in rows]
    if len(arms) != 22:
        sys.exit(f"REFUSING: Figure 6 has {len(arms)} API arms, expected 22")

    print(f"  separate-case prompt: prawns_home C (pair 6's control), "
          f"text sha {sep_sha[:16]}")
    print(f"  paired-scores prompt: CMPN_home_first, text sha {cmpn_sha[:16]}")
    print(f"  {len(arms)} arms; {sum(1 for x in arms if x not in CMPN_ONLY)} separate "
          f"+ {len(arms)} paired = "
          f"{sum(1 for x in arms if x not in CMPN_ONLY) + len(arms)} calls")
    print()
    if a.dry_run:
        for arm in arms:
            s = cfg.get(SEP_ALIAS.get(arm, arm), {}).get("sep")
            c = cfg.get(arm, {}).get("cmpn")
            print(f"    {arm:<14} sep={'-' if arm in CMPN_ONLY else (s and 'ok' or 'MISSING')}"
                  f"  cmpn={'ok' if c else 'MISSING'}")
        return 0

    h = OH.Harness(a.log, cap_usd=a.cap_usd)
    out = {"what": "duty_pairs §0 cost probe: one separate-case and one paired-scores call "
                   "per arm, on texts already frozen in their banks",
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "separate_prompt_text_sha256": sep_sha,
           "paired_prompt_text_sha256": cmpn_sha,
           "separate_prompt": sep_prompt,
           "paired_prompt": cmpn_text,
           "cap_usd": a.cap_usd, "arms": {}}
    for arm in arms:
        rec = {}
        for kind, text, sysmsg, key in (
                ("separate", sep_prompt, SEP_SYS, "sep"),
                ("paired", cmpn_text, CMPN_SYS, "cmpn")):
            if kind == "separate" and arm in CMPN_ONLY:
                rec[kind] = {"skipped": "comparison only by §3 and §4"}
                continue
            src = SEP_ALIAS.get(arm, arm) if key == "sep" else arm
            w = cfg.get(src, {}).get(key)
            if not w:
                rec[kind] = {"error": f"no banked {key} config for {src}"}
                continue
            msgs = [{"role": "system", "content": sysmsg},
                    {"role": "user", "content": text}]
            try:
                x = h.rate(w["model"], w["provider"], messages=msgs, mode="chat",
                           temperature=w["temperature"],
                           max_tokens=w["max_tokens"],
                           want_logprobs=w["want_logprobs"],
                           reasoning=w["reasoning"],
                           label=f"duty_pairs_probe|{arm}|{kind}")
            except SystemExit:
                raise
            except Exception as exc:
                rec[kind] = {"error": repr(exc)[:200]}
                continue
            u = x.get("usage") or {}
            rec[kind] = {"cost_usd": u.get("cost"),
                         "prompt_tokens": u.get("prompt_tokens"),
                         "completion_tokens": u.get("completion_tokens"),
                         "served_model": x.get("served_model"),
                         "provider_served": x.get("provider_served"),
                         "max_tokens": w["max_tokens"],
                         "want_logprobs": w["want_logprobs"],
                         "reasoning_on_the_wire": w["reasoning"],
                         "reasoning_text_len": x.get("reasoning_text_len"),
                         "reasoned": OH.reasoned(x),
                         "ev": x.get("ev"),
                         "raw_text": (x.get("raw_text") or "")[:120],
                         "void": x.get("void"), "void_reason": x.get("void_reason"),
                         "latency_s": x.get("latency_s")}
            c = rec[kind].get("cost_usd")
            print(f"    {arm:<14} {kind:<9} ${c if c is None else format(c, '.6f')}"
                  f"  {str(rec[kind]['raw_text'])[:30]!r}")
        out["arms"][arm] = rec
    out["calls"] = h.calls
    out["spent_usd"] = h.spent
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"\n  {h.calls} calls, ${h.spent:.6f} spent")
    print(f"  -> {os.path.relpath(a.out, R)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

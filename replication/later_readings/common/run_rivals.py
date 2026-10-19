#!/usr/bin/env python3
"""run_rivals.py : deployed_bicycle_rivals. blame + CAUSE on every row, three probes on the P-rows.

CAUSE is a SECOND DIGIT CHANNEL and is asked in its own context, never after blame.
`assert_isolated` checks the built prompt carries exactly one question, which is the
only form of the check that can fail (asserting the construction proves nothing).
"""
import argparse, json, math, os, statistics, sys

R = os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
from or_harness import Harness
import bank_lock
import moral_frames as MF

F = {f["id"]: f for f in MF.FRAMES}
BLAME = F["b1_blame_chat"]
SYS_DIGIT = ("You are a rating instrument. Reply with a single digit from 0 to 9 "
             "and nothing else.")
SYS_YN = "Answer with one word, Yes or No, and nothing else."
BANK = "data/rivals/moral__rivals__b1__rev1.jsonl"
ALL_ROWS = ["N", "C", "P0", "P1", "P1_R", "P1_neutral", "P2_other", "BYSTANDER"]
P_ROWS = ["P0", "P1", "P1_R", "P1_neutral", "P2_other"]

CAUSE_Q = ("{item} How much did {agent} cause the rider's injury, on a scale from 0 "
           "to 9, where 0 means not at all and 9 means entirely? Answer with a "
           "single digit.")
PROBES = {
 "careless": "Did {agent} do anything careless? Answer Yes or No.",
 "reasonable": "Could {agent} reasonably have prevented this? Answer yes or no.",
 "any": "Could {agent} have done anything that would have prevented this? "
        "Answer yes or no.",
}
# every question stem that must never share a context with another
STEMS = {"blame": "to blame, on a scale from",
         "cause": "cause the rider's injury, on a scale from",
         "careless": "do anything careless?",
         "reasonable": "reasonably have prevented this?",
         "any": "have done anything that would have prevented this?"}


def assert_isolated(which, user_turn):
    if STEMS[which] not in user_turn:
        sys.exit(f"REFUSING: {which}'s own question is not in its prompt")
    for other, st in STEMS.items():
        if other != which and st in user_turn:
            sys.exit(f"REFUSING: {which}'s prompt also carries {other}'s question")


def parse_digit(t):
    s = (t or "").strip().strip(".").strip()
    return int(s) if len(s) == 1 and s in "0123456789" else None


def parse_yn(t):
    s = (t or "").strip().strip(".").strip().lower()
    return s if s in ("yes", "no") else None


def lp_digits(x):
    p = {}
    for t in x["top_tokens"]:
        s = (t["t"] or "").strip()
        if len(s) == 1 and s in "0123456789":
            p[int(s)] = p.get(int(s), 0) + math.e ** t["lp"]
    tot = sum(p.values()) or 1
    return {d: p.get(d, 0) / tot for d in range(10)}


def lp_yn(x):
    p = {}
    for t in x["top_tokens"]:
        s = (t["t"] or "").strip().lower()
        if s in ("yes", "no"):
            p[s] = p.get(s, 0) + math.e ** t["lp"]
    tot = sum(p.values())
    return (p.get("yes", 0) / tot if tot else None), tot


class Arm:
    def __init__(self, a, h):
        self.a, self.h, self.served = a, h, set()
        self.logp = a.mode == "logprob"
        self.reasoning = {"effort": a.reasoning_effort} if a.reasoning_effort else None

    def call(self, msgs, label):
        return self.h.rate(self.a.model, self.a.provider, messages=msgs, mode="chat",
                           max_tokens=1 if self.logp else self.a.mt,
                           top_k=self.a.top_k, label=label,
                           reasoning_off=(self.reasoning is None),
                           reasoning=self.reasoning, want_logprobs=self.logp)

    def digit(self, user, uid, chan):
        assert_isolated(chan, user)
        msgs = [{"role": "system", "content": SYS_DIGIT},
                {"role": "user", "content": user}]
        vals, ps, void = [], [], 0
        for _ in range(self.a.draws):
            x = self.call(msgs, f"{self.a.tag}|{uid}|{chan}")
            self.served.add(x["provider_served"])
            if self.logp:
                if x["ev"] is None:
                    void += 1
                    continue
                ps.append(lp_digits(x))
                vals.append(x["ev"])
            else:
                v = parse_digit(x["raw_text"])
                if v is None:
                    void += 1
                else:
                    vals.append(float(v))
        if not vals:
            return {"ev": None, "void_rate": 1.0, "n_draws": 0}
        o = {"ev": statistics.mean(vals), "ev_sd": statistics.pstdev(vals),
             "n_draws": len(vals), "void_rate": void / self.a.draws}
        if ps:
            o["probs"] = {d: statistics.mean(q[d] for q in ps) for d in range(10)}
        return o

    def probe(self, text, uid, pid, agent):
        user = f"{text}\n\n{PROBES[pid].format(agent=agent)}"
        assert_isolated(pid, user)
        msgs = [{"role": "system", "content": SYS_YN},
                {"role": "user", "content": user}]
        ys, void = [], 0
        for _ in range(self.a.draws):
            x = self.call(msgs, f"{self.a.tag}|{uid}|{pid}")
            self.served.add(x["provider_served"])
            if self.logp:
                y, m = lp_yn(x)
                if y is None:
                    void += 1
                else:
                    ys.append(y)
            else:
                v = parse_yn(x["raw_text"])
                if v is None:
                    void += 1
                else:
                    ys.append(1.0 if v == "yes" else 0.0)
        if not ys:
            return {"p_yes": None, "void_rate": 1.0, "n_draws": 0}
        return {"p_yes": statistics.mean(ys), "n_draws": len(ys),
                "void_rate": void / self.a.draws}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--provider", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--mode", choices=["logprob", "sampled"], default="logprob")
    ap.add_argument("--readout", required=True,
                    choices=["LOGPROB", "SAMPLED", "REASONING"])
    ap.add_argument("--top-k", type=int, default=20)
    ap.add_argument("--draws", type=int, default=10)
    ap.add_argument("--mt", type=int, default=8)
    ap.add_argument("--reasoning-effort", default=None)
    ap.add_argument("--cap", type=float, default=2.0)
    ap.add_argument("--rows", default=",".join(ALL_ROWS))
    ap.add_argument("--no-probes", action="store_true")
    a = ap.parse_args()
    if a.readout == "REASONING" and a.mode != "sampled":
        sys.exit("REFUSING: a REASONING column is read SAMPLED")
    dest = f"{R}/records/rivals__{a.tag}.json"
    if os.path.exists(dest):
        sys.exit(f"write-once: {dest} exists")
    bank = {r["uid"]: r for r in bank_lock.load(f"{R}/{BANK}")}
    want = [u for u in a.rows.split(",") if u]
    logpath = f"{R}/runs/deployed_bicycle_rivals/logs/riv_{a.tag}.jsonl"
    os.makedirs(os.path.dirname(logpath), exist_ok=True)
    h = Harness(logpath, cap_usd=a.cap)
    arm = Arm(a, h)
    cells = {}
    for uid in want:
        r = bank[uid]
        agent = MF.agent_of(r["text"])
        c = {"text_sha256": r["text_sha256"], "role": r["role"],
             "blame": arm.digit(MF.render(BLAME, r["text"]), uid, "blame"),
             "cause": arm.digit(CAUSE_Q.format(item=r["text"], agent=agent),
                                uid, "cause")}
        if uid in P_ROWS and not a.no_probes:
            for pid in PROBES:
                c[pid] = arm.probe(r["text"], uid, pid, agent)
        cells[uid] = c
    out = {"run": 215, "tag": a.tag, "model": a.model, "bank": BANK,
           "provider_asked": a.provider,
           "provider_served": sorted(x for x in arm.served if x),
           "readout": a.readout, "mode": a.mode, "draws": a.draws,
           "top_k": a.top_k if a.mode == "logprob" else None,
           "reasoning_effort": a.reasoning_effort, "rows_read": want,
           "probes_run": not a.no_probes, "cause_question": CAUSE_Q,
           "probe_questions": PROBES, "channels_isolated": True,
           "calls": h.calls, "cost_usd": round(h.spent, 5), "cells": cells}
    json.dump(out, open(dest, "w"), indent=1)
    print(f"\n  {a.model}  [{a.readout}]  ${h.spent:.4f}  {h.calls} calls")
    print(f"    {'row':<12}{'blame':>7}{'[sd]':>7}{'CAUSE':>7}{'[sd]':>7}"
          f"{'REASON':>9}{'ANY':>7}{'carel':>7}{'void':>6}")
    for uid in want:
        c = cells[uid]
        g = lambda k: (f"{c[k]['p_yes']:.3f}" if k in c and c[k]["p_yes"] is not None
                       else "-")
        print(f"    {uid:<12}{c['blame']['ev']:>7.2f}{c['blame']['ev_sd']:>7.2f}"
              f"{c['cause']['ev']:>7.2f}{c['cause']['ev_sd']:>7.2f}"
              f"{g('reasonable'):>9}{g('any'):>7}{g('careless'):>7}"
              f"{c['blame']['void_rate']:>6.2f}")
    print(f"  -> {dest}")


if __name__ == "__main__":
    main()

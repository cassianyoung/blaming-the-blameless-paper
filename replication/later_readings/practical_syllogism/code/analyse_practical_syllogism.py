#!/usr/bin/env python3
"""analyse_practical_syllogism.py : practical_syllogism.P1, practical_syllogism.P2, practical_syllogism.P3 and the B premise readings.

    python3 scripts/analyse_practical_syllogism.py            # writes records/result.json
    python3 scripts/analyse_practical_syllogism.py --selftest

Every choice is frozen in records/PREREG_practical_syllogism_SYLLOGISM.md (Amendment 0 and the ruling
of 2026-10-13: all five defaults). Section numbers in comments point there.

Inputs: practical_syllogism's own readings (records/read__*.json, or the database cells via
load_from_db), prevention_paraphrase's fact and conclusion cells (the same, through analyse_prevention_paraphrase's
loaders), and the banked blame position and gate (tables/B8_judgement_long.csv).
"""
import argparse, glob, hashlib, json, os, random, statistics as st, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import analyse_prevention_paraphrase as A231
import report_exclusions as RX

ARMS = ["claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
        "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b"]
SCEN = A231.SCEN
BAND, THREE = 0.10, 0.30          # A0.5, ruled
LP_HELD = 0.10                    # A0.3, ruled
GATE_MASS = 0.70
B_PARSE_MIN = 7                   # A0.7 B.1
N_MASS03_MIN = 0.80               # A0.7 B.2, mirrors the banked gate
NBOOT, SEED = 10000, 232          # A0.7 B.3


def fsha(p):
    return hashlib.sha256(open(os.path.join(R, p), "rb").read()).hexdigest()


def held_from(readout, p_yes, mass, n_no):
    """A0.3: the principle is held, from the A cell's figures alone."""
    if mass is None or mass < GATE_MASS or p_yes is None and n_no is None:
        return False
    if readout == "logprob":
        return p_yes is not None and p_yes <= LP_HELD
    return (n_no or 0) >= 9


def load():
    reads = {}
    for a in ARMS:
        p = f"{R}/records/read__{a}.json"
        reads[a] = json.load(open(p)) if os.path.exists(p) else {"status": "MISSING"}
    return reads


def load_from_db(con):
    """The same `reads` structure, rebuilt from the practical_syllogism cells in a database."""
    reads = {a: {"status": "MISSING"} for a in ARMS}
    for aid, arm, readout, env in con.execute(
            "SELECT id, arm, readout, env FROM artefacts WHERE run='practical_syllogism'"):
        e = json.loads(env or "{}")
        d = {"status": e.get("status"), "readout_A": readout, "B": {}}
        for fam, role, q, ev, p, mass, m03, nd, nv, void in con.execute(
                "SELECT family, role, question, ev, p_yes, answer_mass, mass_0_3, n_draws, "
                "n_void, void FROM cells WHERE artefact_id=?", (aid,)):
            if q == "PRINCIPLE":
                npar = (nd or 0) - (nv or 0)
                d["A"] = {"p_yes": p, "answer_mass": mass,
                          "n_no": (None if readout == "logprob" else
                                   npar - round((p or 0) * npar)),
                          "gate": "PASSED" if void == 0 else "FAILED"}
                continue
            c = d["B"].setdefault(f"B|{fam}|{role}", {
                "scenario": fam, "role": role, "n_asked": nd, "n_parsed": (nd or 0) - (nv or 0),
                "gate_parse": "PASSED" if void == 0 else "FAILED"})
            if q == "B_BLAME":
                c["blame_mean"], c["blame_mass_0_3"] = ev, m03
            elif q == "B_PREVENT":
                c["p_prevent_yes"] = p
            elif q == "B_PRINCIPLE":
                c["p_principle_yes"] = p
        reads[arm] = d
    return reads


def b8_rows():
    import csv
    rows = csv.DictReader(l for l in open(f"{R}/{A231.B8}") if not l.startswith("#"))
    return {(r["model"], r["scenario"]): r for r in rows
            if r["reasoning"] == "off" and r["case"] == "P0"}


def analyse(reads, reads231, b8, counted_only=True):
    """Per-arm results over every arm read; pooled results over the arms that count.

    ONE READOUT PER MODEL (records/RULE_ONE_READOUT_PER_MODEL.md, 2026-10-16): a check
    readout (RX.CHECK_READOUTS) keeps its per-arm rows and is left out of every pooled
    count, share, median, bootstrap and verdict. `counted_only=False` reproduces the
    banked result.json, which pooled over every arm read."""
    out = {"arm_status": {a: {k: reads[a].get(k) for k in
                              ("status", "unread_reason", "provider_served", "served_model",
                               "served_model_constant", "temperature", "spent_usd", "calls")}
                          for a in ARMS}}
    read = [a for a in ARMS if reads[a].get("status") == "READ"]
    pool = [a for a in read if RX.counted(a)] if counted_only else list(read)
    out["pooled_over"] = pool

    # ── practical_syllogism.P1 (A0.3) ────────────────────────────────────────────────────────────
    p1 = {}
    for a in read:
        c = reads[a]["A"]
        ro = reads[a].get("readout_A")
        p1[a] = {"readout": ro, "p_yes": c["p_yes"], "answer_mass": c["answer_mass"],
                 "n_no": c.get("n_no"), "gate": c["gate"],
                 "held": held_from(ro, c["p_yes"], c["answer_mass"], c.get("n_no"))}
        if "draws" in c and ro == "logprob":
            p1[a]["sampled_tokens"] = [d.get("sampled_token") for d in c["draws"]]
    pp1 = {a: v for a, v in p1.items() if a in pool}
    out["P232_1"] = {"per_arm": p1, "n_held": sum(v["held"] for v in pp1.values()),
                     "n_arms": len(pp1),
                     "not_held": [a for a, v in pp1.items() if not v["held"]],
                     "PASS": bool(pp1) and all(v["held"] for v in pp1.values())}

    # ── practical_syllogism.P2 (A0.4, A0.5) ──────────────────────────────────────────────────────
    cells = []
    for a in read:
        for s in SCEN:
            b = b8.get((a, s))
            if b is None or b["gate"] != "PASSED":
                continue                                   # banked gate exclusion
            r = A231.cell(reads231, a, s, "P0", "REASONABLE")
            f = A231.cell(reads231, a, s, "P0", "FELL")
            if r is None or f is None or b["blame_pos"] in ("", None):
                continue
            pos = float(b["blame_pos"])
            cells.append({"arm": a, "scenario": s, "principle": p1[a]["held"],
                          "fact": r["p_yes"] < 0.5, "reasonable_p_yes": r["p_yes"],
                          "fell_p_yes": f["p_yes"], "blame_pos": pos,
                          "a": f["p_yes"] > 0.5, "b": pos > BAND, "b3": pos > THREE})

    def tally(cs):
        prem = [c for c in cs if c["principle"] and c["fact"]]
        res = {"n_cells": len(cs), "n_premises_held": len(prem),
               "n_fact_held": sum(c["fact"] for c in cs)}
        for k, lab in (("a", "a"), ("b", "b"), ("b3", "b_three_band")):
            res[lab] = {"all_three": sum(c[k] for c in prem), "of_all": len(cs),
                        "share_all": (sum(c[k] for c in prem) / len(cs)) if cs else None,
                        "conditional": sum(c[k] for c in prem), "of_premises": len(prem),
                        "share_conditional": ((sum(c[k] for c in prem) / len(prem))
                                              if prem else None)}
        both = sum(c["a"] and c["b"] for c in prem)
        res["a_and_b"] = {"n": both, "of_premises": len(prem),
                          "share_conditional": both / len(prem) if prem else None}
        either = sum(c["a"] or c["b"] for c in prem)
        res["a_or_b"] = {"n": either, "of_premises": len(prem),
                         "share_conditional": either / len(prem) if prem else None}
        return res

    pc = [c for c in cells if c["arm"] in pool]
    out["P232_2"] = {"pooled": tally(pc),
                     "per_arm": {a: tally([c for c in cells if c["arm"] == a]) for a in read},
                     "n_models": len({c["arm"] for c in pc}),
                     "cells": cells}

    # ── practical_syllogism.P3 and B.4 (A0.7) ────────────────────────────────────────────────────
    bpos, gates = [], []
    for a in read:
        B = reads[a].get("B") or {}
        for s in SCEN:
            p0, n, c = (B.get(f"B|{s}|{r}") for r in ("P0", "N", "C"))
            why = None
            if not (p0 and n and c):
                why = "B cell missing"
            elif any(x["gate_parse"] != "PASSED" for x in (p0, n, c)):
                why = "fewer than 7 of 10 parsed on " + ",".join(
                    x["role"] for x in (p0, n, c) if x["gate_parse"] != "PASSED")
            elif (n["blame_mass_0_3"] or 0) < N_MASS03_MIN:
                why = f"N blame mass(0-3) {n['blame_mass_0_3']:.2f} < {N_MASS03_MIN}"
            elif c["blame_mean"] == n["blame_mean"]:
                why = "C equals N"
            b = b8.get((a, s))
            if why is None and (b is None or b["gate"] != "PASSED"):
                why = "banked direct cell excluded by the banked gate"
            if why:
                gates.append({"arm": a, "scenario": s, "reason": why})
                continue
            pb = (p0["blame_mean"] - n["blame_mean"]) / (c["blame_mean"] - n["blame_mean"])
            bpos.append({"arm": a, "scenario": s, "pos_B": pb,
                         "pos_direct": float(b["blame_pos"]),
                         "shift": pb - float(b["blame_pos"]),
                         "B_prevent_p_yes": p0.get("p_prevent_yes"),
                         "B_principle_p_yes": p0.get("p_principle_yes")})
    allpos, bpos = bpos, [x for x in bpos if x["arm"] in pool]
    per_arm = {a: st.mean([x["shift"] for x in bpos if x["arm"] == a])
               for a in pool if any(x["arm"] == a for x in bpos)}
    ms = sorted(per_arm)
    med = st.median(per_arm.values()) if per_arm else None
    rng = random.Random(SEED)
    bs = sorted(st.median([per_arm[rng.choice(ms)] for _ in ms]) for _ in range(NBOOT)) \
        if ms else []
    lo, hi = (A231.pctl(bs, 0.025), A231.pctl(bs, 0.975)) if bs else (None, None)
    out["P232_3"] = {"median_shift": med, "boot95": [lo, hi], "n_models": len(ms),
                     "n_cells": len(bpos), "per_arm_mean_shift": per_arm,
                     "n_arms_shift_negative": sum(v < 0 for v in per_arm.values()),
                     "median_pos_B": st.median([x["pos_B"] for x in bpos]) if bpos else None,
                     "median_pos_direct": (st.median([x["pos_direct"] for x in bpos])
                                           if bpos else None),
                     "B_cells_above_band": sum(x["pos_B"] > BAND for x in bpos),
                     "direct_cells_above_band": sum(x["pos_direct"] > BAND for x in bpos),
                     # Amendment 1: where B's blame ends up, beside the direct reading
                     "B_cells_above_three": sum(x["pos_B"] > THREE for x in bpos),
                     "direct_cells_above_three": sum(x["pos_direct"] > THREE for x in bpos),
                     "excluded": gates, "cells": allpos,
                     "PASS": hi is not None and hi < 0}

    # B.4: the premises stated in B, on P0, against the separate calls
    prem = []
    for a in pool:
        B = reads[a].get("B") or {}
        for s in SCEN:
            p0 = B.get(f"B|{s}|P0")
            if not p0 or p0["gate_parse"] != "PASSED":
                continue
            prem.append((a, s, p0["p_prevent_yes"], p0["p_principle_yes"]))
    n_unparsed = sum(len(c.get("unparsed_texts") or []) if isinstance(c, dict) else 0
                     for a in read for c in (reads[a].get("B") or {}).values())
    out["B_premises"] = {
        "n_p0_cells": len(prem),
        "prevent_modal_no": sum(p is not None and p < 0.5 for _, _, p, _ in prem),
        "principle_modal_no": sum(q is not None and q < 0.5 for _, _, _, q in prem),
        "B_gate_parse_failures": sum(c["gate_parse"] != "PASSED" for a in read
                                     for c in (reads[a].get("B") or {}).values()),
        "B_unparsed_draws": n_unparsed,
        "N_prevent_not_interpretable": {
            a: {s: (reads[a].get("B") or {}).get(f"B|{s}|N", {}).get("p_prevent_yes")
                for s in SCEN} for a in read}}
    out["cost_usd"] = sum(reads[a].get("spent_usd") or 0 for a in ARMS)
    return out


def _f(x, nd=4):
    return "n/a" if x is None else f"{x:.{nd}f}"


def registered(out):
    """(location, printed value), shared by the result writer and the seeder."""
    P = "S4.1.4/rebuttal: practical_syllogism"
    p1, p2, p3 = out["P232_1"], out["P232_2"]["pooled"], out["P232_3"]
    rows = [(f"{P}: practical_syllogism.P1 arms holding the principle (A0.3)",
             f"{p1['n_held']} of {p1['n_arms']}"),
            (f"{P}: practical_syllogism.P1 verdict", "PASS" if p1["PASS"] else "FAIL"),
            (f"{P}: practical_syllogism.P2 cells with both premises held",
             f"{p2['n_premises_held']} of {p2['n_cells']}"),
            (f"{P}: practical_syllogism.P2 cells with the fact held",
             f"{p2['n_fact_held']} of {p2['n_cells']}")]
    for k, lab in (("b", "(b) blame position > 0.10"), ("a", "(a) fell short modal yes"),
                   ("b_three_band", "(b) blame position > 0.30")):
        x = p2[k]
        rows += [(f"{P}: practical_syllogism.P2{lab}, conditional on both premises",
                  f"{x['conditional']} of {x['of_premises']} ({_f(x['share_conditional'], 3)})"),
                 (f"{P}: practical_syllogism.P2{lab}, all three over all cells",
                  f"{x['all_three']} of {x['of_all']} ({_f(x['share_all'], 3)})")]
    rows += [(f"{P}: practical_syllogism.P2 (a) and (b) both, conditional on both premises",
              f"{p2['a_and_b']['n']} of {p2['a_and_b']['of_premises']}"),
             (f"{P}: practical_syllogism.P2 (a) or (b), conditional on both premises",
              f"{p2['a_or_b']['n']} of {p2['a_or_b']['of_premises']}"),
             (f"{P}: practical_syllogism.P2 models in the population", str(out["P232_2"]["n_models"]))]
    rows += [(f"{P}: practical_syllogism.P3 median shift, B position minus direct, 95% model bootstrap",
              f"{_f(p3['median_shift'])} [{_f(p3['boot95'][0])}, {_f(p3['boot95'][1])}] "
              f"over {p3['n_cells']} cells, {p3['n_models']} models"),
             (f"{P}: practical_syllogism.P3 verdict (remedy check only)", "PASS" if p3["PASS"] else "FAIL"),
             (f"{P}: practical_syllogism.P3 cells above the band, B against direct",
              f"{p3['B_cells_above_band']} against {p3['direct_cells_above_band']} of "
              f"{p3['n_cells']}"),
             # Amendment 1 (2026-10-13, before the result was written)
             (f"{P}: A1 median blame position, B against direct (same cells)",
              f"{_f(p3['median_pos_B'], 3)} against {_f(p3['median_pos_direct'], 3)} over "
              f"{p3['n_cells']} cells"),
             (f"{P}: A1 share of cells above 0.10, B against direct",
              f"{_f(p3['B_cells_above_band'] / p3['n_cells'] if p3['n_cells'] else None, 3)} "
              f"against {_f(p3['direct_cells_above_band'] / p3['n_cells'] if p3['n_cells'] else None, 3)}"),
             (f"{P}: A1 cells above 0.30, B against direct",
              f"{p3['B_cells_above_three']} against {p3['direct_cells_above_three']} of "
              f"{p3['n_cells']}"),
             (f"{P}: B premises on P0, PREVENT modal no",
              f"{out['B_premises']['prevent_modal_no']} of {out['B_premises']['n_p0_cells']}"),
             (f"{P}: B premises on P0, PRINCIPLE modal no",
              f"{out['B_premises']['principle_modal_no']} of "
              f"{out['B_premises']['n_p0_cells']}")]
    return rows


def selftest():
    ok = 0
    assert held_from("logprob", 0.05, 0.99, None) and not held_from("logprob", 0.2, 0.99, None)
    assert not held_from("logprob", 0.05, 0.5, None)              # gate fails: not held
    assert held_from("sampled", 0.1, 1.0, 9) and not held_from("sampled", 0.2, 0.8, 8)
    ok += 1; print("  ok  A0.3 held rule, both readouts, gate counts against")
    # synthetic: one arm, two scenarios, one fact held and (b) drawn
    reads = {a: {"status": "MISSING"} for a in ARMS}
    mk = lambda m: {"blame_mean": m, "blame_mass_0_3": 1.0 if m <= 3 else 0.0,
                    "gate_parse": "PASSED", "role": "x", "p_prevent_yes": 0.0,
                    "p_principle_yes": 0.0, "unparsed_texts": []}
    reads["gpt4o"] = {"status": "READ", "readout_A": "logprob",
                      "A": {"p_yes": 0.01, "answer_mass": 1.0, "gate": "PASSED"},
                      "B": {f"B|{s}|{r}": mk(v) for s in SCEN
                            for r, v in (("P0", 1.0), ("N", 0.0), ("C", 8.0))}}
    cell = lambda p: {"p_yes": p, "gate": "PASSED"}
    r231 = {a: {"cells": {}} for a in A231.ARMS}
    r231["gpt4o"]["cells"] = {f"{s}|P0|{q}": cell(p) for s in SCEN
                              for q, p in (("REASONABLE", 0.1), ("FELL", 0.9))}
    b8 = {("gpt4o", s): {"gate": "PASSED", "blame_pos": "0.5"} for s in SCEN}
    o = analyse(reads, r231, b8)
    assert o["P232_1"]["PASS"] and o["P232_2"]["pooled"]["b"]["conditional"] == 6
    assert abs(o["P232_3"]["median_shift"] - (0.125 - 0.5)) < 1e-12
    assert o["P232_3"]["PASS"]
    ok += 1; print("  ok  practical_syllogism.P2 counts and practical_syllogism.P3 shift on a constructed arm")
    b8[("gpt4o", "cheque")]["gate"] = "FAILED"
    o = analyse(reads, r231, b8)
    assert o["P232_2"]["pooled"]["n_cells"] == 5 and o["P232_3"]["n_cells"] == 5
    ok += 1; print("  ok  banked gate exclusion removes the cell from practical_syllogism.P2 and practical_syllogism.P3")
    print(f"selftest {ok}/3")
    return 0 if ok == 3 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    dest = f"{R}/records/result.json"
    if os.path.exists(dest):
        sys.exit(f"write-once: {os.path.relpath(dest, R)} exists")
    reads = load()
    out = analyse(reads, A231.load()[0], b8_rows())
    out["inputs"] = {p: fsha(p) for p in
                     [A231.B8] + sorted(os.path.relpath(f, R) for f in
                                        glob.glob(f"{R}/records/<prevention_paraphrase and practical_syllogism>_READ__*.json"))}
    out["registered"] = registered(out)
    json.dump(out, open(dest, "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("P232_1",)}, indent=1, default=str)[:3000])
    for loc, v in out["registered"]:
        print(f"  {loc}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

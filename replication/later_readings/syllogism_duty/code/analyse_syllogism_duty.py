#!/usr/bin/env python3
"""analyse_syllogism_duty.py : syllogism_duty.P1 to syllogism_duty.P4, against the same-session and the banked bare gap.

    python3 scripts/analyse_syllogism_duty.py            # writes records/result.json
    python3 scripts/analyse_syllogism_duty.py --selftest

Every choice is frozen in records/PREREG_syllogism_duty_SYLLOGISM_DUTY.md (Amendment 0 and the
ruling of 2026-10-13). Section numbers in comments point there.

Inputs: run syllogism_duty's readings (records/read__*.json, or the database cells via
load_from_db) and the comparands frozen in records/frames.json. Nothing is read
from the duty views at analysis time: the comparands were copied when the frames were
frozen, so a rebuild cannot move them.

**THE WORDING FLOOR IS BORROWED** (A0.13, ruled): it was measured in the bare separate
frame and is applied here to the structured frame, which has no floor of its own. Every
printed class or count that uses it says so.
"""
import argparse, hashlib, json, os, random, statistics as st, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES = "records/frames.json"
FRAMES_SHA = "ae17c72b9a38e007be560eb9deb75079c90c2c53fe3e8387ded2945a7996df97"
RESULT = "records/result.json"
ARMS = ["claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
        "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b"]
PAIRS = ["1", "3", "4", "5", "7"]
NON_DRIVING = ["1", "3", "4", "7"]
PAIR_NAME = {"1": "electrical", "3": "gas", "4": "childcare", "5": "driving", "7": "hair dye",
             "prawns": "prawns"}
# ── THE v1.1 FILL (completeness_fill_amendment H7): PRAWNS POOLED WITH THE OTHER PAIRS ──
# Read in completeness_fill on run syllogism_duty's own texts and settings, and judged against comparands
# re-frozen from the v1.1 duty views for all six pairs (v11_comparands.json): the
# v1.1 floor pools 18 neutral deviations, so every arm's floor moved, and one arm's cells
# are never judged against two floors. The banked result (RESULT, on PAIRS and
# frames.json's comparands) is untouched and still reproduces.
PAIRS_V11 = ["prawns", "1", "3", "4", "5", "7"]
NON_DRIVING_V11 = ["prawns", "1", "3", "4", "7"]
COMPARANDS_V11 = "records/v11_comparands.json"
RESULT_V11 = "records/result_v11.json"
SYLL_V11 = "records/syll_cells.json"
LEGS = ["PRO", "PRIV"]
GATE_MASS, B_GATE, LP_HELD = 0.70, 7, 0.90           # A0.4, A0.5
NBOOT, SEED, NBOOT_CELL = 10000, 233, 2000            # A0.8, A0.9
TENTH, THREE = 0.10, 0.30                             # A0.10
BORROWED = "wording floor borrowed from the bare separate frame (A0.13)"


def fsha(p):
    return hashlib.sha256(open(os.path.join(R, p), "rb").read()).hexdigest()


def frames():
    if fsha(FRAMES) != FRAMES_SHA:
        sys.exit(f"REFUSING: {FRAMES} is not the frozen file")
    return json.load(open(os.path.join(R, FRAMES)))


def frames_v11():
    """The banked frames with the comparands replaced by the v1.1 freeze."""
    fr = dict(frames())
    c = json.load(open(os.path.join(R, COMPARANDS_V11)))
    fr["comparands"] = {"source": c["source"], "cells": c["cells"]}
    return fr


def load_v11():
    """load(), with each arm's completeness_fill prawns cells (H7) added beside its syllogism_duty ones."""
    reads = load()
    d = json.load(open(os.path.join(R, SYLL_V11)))
    for a in ARMS:
        x = d["arms"].get(a)
        if x is None or reads[a].get("status") != "READ":
            continue
        for pr, c in x["A"].items():
            reads[a]["A"][pr] = {"p_yes": c["p_yes"], "mass": c["answer_mass"],
                                 "n_yes": c["n_yes"], "n_asked": c["n_asked"]}
        for k, c in x["B"].items():
            pr, leg = k.split("|")
            reads[a]["B"][(pr, leg)] = {
                "mean": c["blame_mean"], "n_parsed": c["n_parsed"], "n_asked": c["n_asked"],
                "n_role_correct": c["n_role_correct"],
                "n_principle_yes": c["n_principle_yes"], "values": c["blame_values"]}
        for k, c in x["R"].items():
            pr, leg = k.split("|")
            reads[a]["R"][(pr, leg)] = {"mean": c["mean"], "n_parsed": c["n_parsed"],
                                        "n_asked": c["n_asked"], "values": c["values"]}
    return reads


# ── LOADERS: ONE MINIMAL SHAPE, FROM THE ARTEFACTS OR FROM THE DATABASE ────────────────
def load():
    reads = {}
    for a in ARMS:
        p = f"{R}/records/read__{a}.json"
        if not os.path.exists(p):
            reads[a] = {"status": "MISSING"}
            continue
        d = json.load(open(p))
        m = {k: d.get(k) for k in ("status", "unread_reason", "readout_A", "provider_served",
                                   "served_model", "served_model_constant", "temperature",
                                   "spent_usd", "calls")}
        m["A"] = {c["pair"]: {"p_yes": c["p_yes"], "mass": c["answer_mass"],
                              "n_yes": c["n_yes"]} for c in (d.get("A") or {}).values()}
        m["B"] = {(c["pair"], c["leg"]): {
            "mean": c["blame_mean"], "n_parsed": c["n_parsed"], "n_asked": c["n_asked"],
            "n_role_correct": c["n_role_correct"], "n_principle_yes": c["n_principle_yes"],
            "values": c["blame_values"]} for c in (d.get("B") or {}).values()}
        m["R"] = {(c["pair"], c["leg"]): {"mean": c["mean"], "n_parsed": c["n_parsed"],
                                          "n_asked": c["n_asked"], "values": c["values"]}
                  for c in (d.get("R") or {}).values()}
        reads[a] = m
    return reads


def load_from_db(con, run="233", arms=None):
    """The same shape, rebuilt from the syllogism_duty cells a database ingested (no draw values,
    so no within-cell standard errors; nothing registered uses them). `run='reasoning_stratum'` reads
    the v1.1 fill's reasoning stratum, which is filed apart so it can never pool."""
    reads = {a: {"status": "MISSING"} for a in (arms or ARMS)}
    for aid, arm, readout, env in con.execute(
            "SELECT id, arm, readout, env FROM artefacts WHERE run=?", (run,)):
        e = json.loads(env or "{}")
        m = {"status": e.get("status"), "readout_A": readout, "A": {}, "B": {}, "R": {}}
        for fam, role, q, ev, p, mass, nd, nv in con.execute(
                "SELECT family, role, question, ev, p_yes, answer_mass, n_draws, n_void "
                "FROM cells WHERE artefact_id=?", (aid,)):
            pr = fam.replace("duty_p", "")
            npar = (nd or 0) - (nv or 0)
            if q == "PRINCIPLE233":
                m["A"][pr] = {"p_yes": p, "mass": mass, "n_asked": nd,
                              "n_yes": None if readout == "logprob" else round((p or 0) * npar)}
            elif q == "R233_BLAME":
                m["R"][(pr, role)] = {"mean": ev, "n_parsed": npar, "n_asked": nd}
            elif q.startswith("B233_"):
                c = m["B"].setdefault((pr, role), {"n_parsed": npar, "n_asked": nd})
                if q == "B233_BLAME":
                    c["mean"] = ev
                elif q == "B233_ROLE":
                    c["n_role_correct"] = round((p or 0) * npar)
                elif q == "B233_PRINCIPLE":
                    c["n_principle_yes"] = round((p or 0) * npar)
        reads[arm] = m
    return reads


# ── THE PIECES ───────────────────────────────────────────────────────────────────────
def held(readout, c):
    """A0.5: the principle ('yes') is held on one pair."""
    if c is None or c["mass"] is None or c["mass"] < GATE_MASS:
        return False
    if readout == "logprob":
        return c["p_yes"] is not None and c["p_yes"] >= LP_HELD
    # 9 of 10, unparsed counting against; the same 90% share on an arm read at 20 draws
    return (c["n_yes"] or 0) >= 0.9 * (c.get("n_asked") or 10)


def gap(cells, pr, gate):
    a, b = cells.get((pr, "PRO")), cells.get((pr, "PRIV"))
    if not a or not b or a.get("mean") is None or b.get("mean") is None:
        return None
    if a["n_parsed"] < gate or b["n_parsed"] < gate:
        return None
    return a["mean"] - b["mean"]


def boot_median_of_means(per_arm, nboot=NBOOT, seed=SEED):
    """A0.9: median over arms of each arm's mean, with a 95% percentile bootstrap over
    arms."""
    vals = [v for v in per_arm.values() if v is not None]
    if not vals:
        return {"median": None, "ci95": [None, None], "n_arms": 0}
    rng = random.Random(seed)
    bs = sorted(st.median(rng.choices(vals, k=len(vals))) for _ in range(nboot))
    return {"median": st.median(vals), "ci95": [bs[int(0.025 * nboot)],
                                                bs[int(0.975 * nboot) - 1]],
            "n_arms": len(vals)}


def klass(w):
    """A0.10: the §4.2.3 class of a withheld share w = 1 - r."""
    if w is None:
        return None
    if abs(w) <= TENTH:
        return "within a tenth"
    if abs(w) <= THREE:
        return "a tenth to three tenths " + ("short" if w > 0 else "over")
    return "more than three tenths " + ("short" if w > 0 else "over")


CLASSES = ["within a tenth", "a tenth to three tenths short", "a tenth to three tenths over",
           "more than three tenths short", "more than three tenths over"]


def cell_se(cells, pr):
    """A0.8: bootstrap standard error of a structured gap, within the cell."""
    a, b = cells.get((pr, "PRO")), cells.get((pr, "PRIV"))
    if not a or not b or not a.get("values") or not b.get("values"):
        return None
    rng = random.Random(SEED)
    g = [st.mean(rng.choices(a["values"], k=len(a["values"])))
         - st.mean(rng.choices(b["values"], k=len(b["values"]))) for _ in range(NBOOT_CELL)]
    return st.pstdev(g)


def shift_test(per_cell, arms, pairs, key):
    per_arm = {}
    for a in arms:
        v = [per_cell[(a, p)][key] for p in pairs
             if (a, p) in per_cell and per_cell[(a, p)][key] is not None]
        per_arm[a] = st.mean(v) if v else None
    t = boot_median_of_means(per_arm)
    t["per_arm_mean"] = per_arm
    t["PASS"] = t["ci95"][0] is not None and t["ci95"][0] > 0
    cells = [per_cell[(a, p)] for a in arms for p in pairs
             if (a, p) in per_cell and per_cell[(a, p)][key] is not None]
    t["n_cells"] = len(cells)
    t["n_cells_beyond_floor"] = sum(c[key] > c["floor"] for c in cells)
    mf = {}
    for a in arms:
        v = [per_cell[(a, p)][key] - per_cell[(a, p)]["floor"] for p in pairs
             if (a, p) in per_cell and per_cell[(a, p)][key] is not None]
        mf[a] = st.mean(v) if v else None
    t["shift_minus_floor"] = boot_median_of_means(mf)       # A0.9 (b), beside, decides nothing
    return t


def analyse(reads, fr, counted_only=True, pairs=None, non_driving=None, arms=None):
    """Per-arm and per-cell results over every arm read; pooled counts, shift tests and
    class counts over the arms that count (ONE READOUT PER MODEL,
    records/RULE_ONE_READOUT_PER_MODEL.md, 2026-10-16). `counted_only=False` reproduces
    the banked result.json."""
    import report_exclusions as RX
    PAIRS = pairs or globals()["PAIRS"]
    NON_DRIVING = non_driving or globals()["NON_DRIVING"]
    ARMS = arms or globals()["ARMS"]
    comp = fr["comparands"]["cells"]
    out = {"arm_status": {a: {k: reads[a].get(k) for k in
                              ("status", "unread_reason", "provider_served", "served_model",
                               "served_model_constant", "temperature", "spent_usd", "calls")}
                          for a in ARMS}}
    read = [a for a in ARMS if reads[a].get("status") == "READ"]
    pool = [a for a in read if RX.counted(a)] if counted_only else list(read)
    out["pooled_over"] = pool
    sampled = [a for a in pool if reads[a].get("readout_A") != "logprob"]

    # ── syllogism_duty.P1 (A0.5) ───────────────────────────────────────────────────────────────
    p1 = {}
    for a in read:
        ro = reads[a].get("readout_A")
        p1[a] = {p: {"p_yes": reads[a]["A"].get(p, {}).get("p_yes"),
                     "mass": reads[a]["A"].get(p, {}).get("mass"),
                     "n_yes": reads[a]["A"].get(p, {}).get("n_yes"),
                     "held": held(ro, reads[a]["A"].get(p))} for p in PAIRS}
    # ── A PAIR WHOSE A WAS NOT READ IS NOT A PAIR THE ARM FAILED TO HOLD ───────────
    # In the banked run every A cell was read, so this changes nothing there. In the
    # v1.1 fill deepseek's and kimi's prawns A could not be read (the provider no longer
    # returns log-probabilities), and counting an unread cell as "not held" would report
    # the instrument as the model. Such an arm is not evaluable for "all pairs" and leaves
    # that count's denominator; an unread cell leaves the cell count's.
    isread = {a: {p: p in reads[a]["A"] for p in PAIRS} for a in read}
    arm_held = {a: (all(p1[a][p]["held"] for p in NON_DRIVING)
                    if all(isread[a][p] for p in NON_DRIVING) else None) for a in read}
    out["P233_1"] = {
        "per_arm_pair": p1, "arm_holds": arm_held,
        "n_arms_holding": sum(bool(arm_held[a]) for a in pool),
        "n_arms": sum(arm_held[a] is not None for a in pool),
        "arms_not_evaluable": [a for a in pool if arm_held[a] is None],
        "n_cells_held_non_driving": sum(p1[a][p]["held"] for a in pool for p in NON_DRIVING
                                        if isread[a][p]),
        "n_cells_non_driving": sum(isread[a][p] for a in pool for p in NON_DRIVING),
        "driving_yes": {a: p1[a]["5"]["held"] for a in read},
        "n_driving_yes": sum(p1[a]["5"]["held"] for a in pool),
        "n_arms_driving": sum(isread[a]["5"] for a in pool),
        "rule": "log-prob: mean P(yes) >= 0.90; sampled: >= 9 of 10 'yes'; mass >= 0.70"}

    # ── syllogism_duty.P2 (A0.6) ───────────────────────────────────────────────────────────────
    def role(sel):
        n = sum(reads[a]["B"][(p, l)]["n_parsed"] for a, p, l in sel)
        k = sum(reads[a]["B"][(p, l)]["n_role_correct"] for a, p, l in sel)
        return {"correct": k, "parsed": n, "share": (k / n) if n else None}
    allc = [(a, p, l) for a in read for p in PAIRS for l in LEGS if (p, l) in reads[a]["B"]]
    pooled = role([c for c in allc if c[0] in pool])
    out["P233_2"] = {"pooled": pooled,
                     "PASS": pooled["share"] is not None and pooled["share"] >= 0.90,
                     "per_arm": {a: role([c for c in allc if c[0] == a]) for a in read},
                     "per_pair": {p: role([c for c in allc if c[1] == p and c[0] in pool])
                                  for p in PAIRS},
                     "per_leg": {l: role([c for c in allc if c[2] == l and c[0] in pool])
                                 for l in LEGS},
                     "draws_asked": sum(reads[a]["B"][(p, l)]["n_asked"] for a, p, l in allc
                                        if a in pool),
                     "denominator": "parsed B draws, every leg, gate-failed legs included"}

    # ── THE GAPS, PER CELL (A0.8, A0.9) ─────────────────────────────────────────────
    per_cell = {}
    missing = []
    for a in read:
        for p in PAIRS:
            c = comp[f"{a}|{p}"]
            if c.get("comparand_status") == "missing":
                missing.append(f"{a}|{p}: {c.get('missing_reason')}")
                continue
            sg = gap(reads[a]["B"], p, B_GATE)
            rg = gap(reads[a]["R"], p, B_GATE)
            per_cell[(a, p)] = {
                "structured_gap": sg, "same_session_bare_gap": rg,
                "banked_bare_gap": c["separate_gap"], "stated_gap": c["stated_gap"],
                "floor": c["floor_used"],
                "convention_stated_gap": c["stated_condition_gap"],
                "shift_same_session": None if sg is None or rg is None else sg - rg,
                "shift_banked": None if sg is None else sg - c["separate_gap"],
                "drift_bare": None if rg is None else rg - c["separate_gap"],
                "structured_gap_se": cell_se(reads[a]["B"], p),
                "B_legs_gated": sg is not None, "R_legs_gated": rg is not None}

    out["comparands_missing"] = missing

    # ── syllogism_duty.P3 (A0.9; the ruling: same-session first, banked beside) ────────────────
    p3 = {}
    for key, label in (("shift_same_session", "same_session"), ("shift_banked", "banked")):
        p3[label] = {
            "all_pairs": shift_test(per_cell, pool, PAIRS, key),
            "excluding_driving": shift_test(per_cell, pool, NON_DRIVING, key),
            "sampled_arms_only": shift_test(per_cell, sampled, PAIRS, key)}
    pk = [k for k in per_cell if k[0] in pool]
    drift = [per_cell[k]["drift_bare"] for k in pk if per_cell[k]["drift_bare"] is not None]
    p3["bare_drift"] = {"median_abs": st.median(abs(x) for x in drift) if drift else None,
                        "n_cells": len(drift),
                        "n_beyond_floor": sum(abs(per_cell[k]["drift_bare"]) > per_cell[k]["floor"]
                                              for k in pk
                                              if per_cell[k]["drift_bare"] is not None)}
    p3["floor_note"] = BORROWED
    out["P233_3"] = p3

    # ── syllogism_duty.P4 (A0.10) and the convention on the same cells ─────────────────────────
    def cls(rkey):
        cells, per_model = {}, {}
        for a in read:
            rs = []
            for p in PAIRS:
                v = per_cell.get((a, p))
                if v is None:                    # comparand missing
                    continue
                if abs(v["stated_gap"]) <= v["floor"]:
                    continue                     # no stated slack to restore
                num = v[rkey]
                if num is None:
                    continue
                r = num / v["stated_gap"]
                cells[f"{a}|{p}"] = {"r": r, "withheld": 1 - r, "class": klass(1 - r)}
                rs.append(r)
            if rs:
                w = 1 - st.median(rs)
                per_model[a] = {"withheld": w, "class": klass(w), "n_pairs": len(rs)}
        count = lambda xs: {k: sum(x["class"] == k for x in xs) for k in CLASSES}
        return {"per_cell": cells, "per_model": per_model,
                "cell_counts": count([v for k, v in cells.items()
                                      if k.split("|")[0] in pool]),
                "model_counts": count([v for k, v in per_model.items() if k in pool])}
    classable = [k for k, v in per_cell.items() if abs(v["stated_gap"]) > v["floor"]
                 and k[0] in pool]
    struct = cls("structured_gap")
    conv = cls("convention_stated_gap")
    # matched: the same cells on both sides
    both = sorted(k for k in set(struct["per_cell"]) & set(conv["per_cell"])
                  if k.split("|")[0] in pool)
    out["P233_4"] = {
        "structured": struct, "convention_stated": conv,
        "n_classable_cells": len(classable),
        "n_unclassable_cells": len(pk) - len(classable),
        "unclassable_by_pair": {p: sum(1 for (a, q), v in per_cell.items() if q == p and
                                       a in pool and abs(v["stated_gap"]) <= v["floor"])
                                for p in PAIRS},
        "matched_cells": len(both),
        "matched_class_agreement": sum(struct["per_cell"][k]["class"] ==
                                       conv["per_cell"][k]["class"] for k in both),
        "floor_note": BORROWED}
    # B's own premise fields, beside A (descriptive)
    out["B_principle_field"] = {
        a: {p: (lambda c1, c2: None if not (c1["n_parsed"] + c2["n_parsed"]) else
                (c1["n_principle_yes"] + c2["n_principle_yes"]) /
                (c1["n_parsed"] + c2["n_parsed"]))(reads[a]["B"][(p, "PRO")],
                                                   reads[a]["B"][(p, "PRIV")])
            for p in PAIRS if (p, "PRO") in reads[a]["B"] and (p, "PRIV") in reads[a]["B"]}
        for a in read}
    out["per_cell"] = {f"{a}|{p}": v for (a, p), v in per_cell.items()}
    out["spent_usd"] = sum(reads[a].get("spent_usd") or 0 for a in ARMS)
    return out


def f3(x):
    return "n/a" if x is None else f"{x:+.3f}"


def registered(res):
    """(location, printed) pairs: every pre-registered figure, flat, as registered."""
    L = []
    p1 = res["P233_1"]
    L.append(("S4.2 (syllogism_duty): syllogism_duty.P1, arms holding the principle (yes on all four pairs "
              "other than driving)", f"{p1['n_arms_holding']} of {p1['n_arms']}"))
    L.append(("S4.2 (syllogism_duty): syllogism_duty.P1, arm-pair cells holding the principle, four pairs "
              "other than driving",
              f"{p1['n_cells_held_non_driving']} of {p1['n_cells_non_driving']}"))
    L.append(("S4.2 (syllogism_duty): driving, arms answering yes (no prediction)",
              f"{p1['n_driving_yes']} of {p1['n_arms_driving']}"))
    p2 = res["P233_2"]["pooled"]
    L.append(("S4.2 (syllogism_duty): syllogism_duty.P2, ROLE correct in the structured prompt, pooled",
              f"{p2['correct']} of {p2['parsed']} ({100 * p2['share']:.1f}%); "
              + ("PASS" if res["P233_2"]["PASS"] else "FAIL")))
    for lab, name in (("same_session", "against the same-session bare gap"),
                      ("banked", "against the banked bare gap")):
        for sub, sname in (("all_pairs", "five pairs"), ("excluding_driving",
                                                         "excluding driving"),
                           ("sampled_arms_only", "six sampled arms")):
            t = res["P233_3"][lab][sub]
            L.append((f"S4.2 (syllogism_duty): syllogism_duty.P3, median shift {name}, {sname}",
                      f"{f3(t['median'])} [{f3(t['ci95'][0])}, {f3(t['ci95'][1])}] over "
                      f"{t['n_arms']} arms; " + ("PASS" if t["PASS"] else "FAIL")))
            L.append((f"S4.2 (syllogism_duty): syllogism_duty.P3, cells whose shift exceeds the wording floor, "
                      f"{name}, {sname}",
                      f"{t['n_cells_beyond_floor']} of {t['n_cells']} ({BORROWED})"))
    d = res["P233_3"]["bare_drift"]
    L.append(("S4.2 (syllogism_duty): same-session bare gap against the banked one, median "
              "absolute drift", f"{d['median_abs']:.3f} over {d['n_cells']} cells; "
              f"{d['n_beyond_floor']} beyond the wording floor"))
    p4 = res["P233_4"]
    for side, name in (("structured", "the structured prompt"),
                       ("convention_stated", "the stated convention, same arms and pairs")):
        mc = p4[side]["model_counts"]
        L.append((f"S4.2 (syllogism_duty): syllogism_duty.P4, models by class against their stated slack, "
                  f"{name}",
                  "; ".join(f"{k} {mc[k]}" for k in CLASSES)
                  + f" (of {sum(p4[side]['model_counts'].values())}; {BORROWED})"))
        cc = p4[side]["cell_counts"]
        L.append((f"S4.2 (syllogism_duty): syllogism_duty.P4, cells by class against the stated slack, {name}",
                  "; ".join(f"{k} {cc[k]}" for k in CLASSES)
                  + f" (of {sum(p4[side]['cell_counts'].values())} classable; {BORROWED})"))
    L.append(("S4.2 (syllogism_duty): syllogism_duty.P4, cells with no stated slack above the wording floor",
              f"{p4['n_unclassable_cells']} of {p4['n_unclassable_cells'] + p4['n_classable_cells']}"
              f" ({BORROWED})"))
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--v11", action="store_true",
                    help=f"write {RESULT_V11}: prawns pooled (H7), v1.1 comparands")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.v11:
        if os.path.exists(os.path.join(R, RESULT_V11)):
            sys.exit(f"write-once: {RESULT_V11} exists")
        res = analyse(load_v11(), frames_v11(), pairs=PAIRS_V11,
                      non_driving=NON_DRIVING_V11)
        res["registered"] = registered(res)
        res["_meta"] = {"what": "syllogism_duty with prawns pooled (completeness_fill_amendment "
                                "H7), against the v1.1 comparands",
                        "comparands": {COMPARANDS_V11: fsha(COMPARANDS_V11)},
                        "fill": {SYLL_V11: fsha(SYLL_V11)}, "frames": FRAMES,
                        "pairs": PAIRS_V11, "non_driving": NON_DRIVING_V11,
                        "labels": "the registered location strings are run syllogism_duty's, "
                                  "unchanged, so no id moves: 'four pairs other than "
                                  "driving' now counts five, and 'five pairs' six"}
        json.dump(res, open(os.path.join(R, RESULT_V11), "w"), indent=1,
                  ensure_ascii=False)
        for loc, pv in res["registered"]:
            print(f"  {loc}: {pv}")
        return 0
    if os.path.exists(os.path.join(R, RESULT)):
        sys.exit(f"write-once: {RESULT} exists")
    fr = frames()
    reads = load()
    res = analyse(reads, fr)
    res["registered"] = registered(res)
    res["_meta"] = {"frames": FRAMES, "frames_sha256": FRAMES_SHA,
                    "artefacts": {f"records/read__{x}.json":
                                  fsha(f"records/read__{x}.json")
                                  for x in ARMS
                                  if os.path.exists(f"{R}/records/read__{x}.json")},
                    "prereg": "records/PREREG_syllogism_duty_SYLLOGISM_DUTY.md"}
    json.dump(res, open(os.path.join(R, RESULT), "w"), indent=1, ensure_ascii=False)
    for loc, pv in res["registered"]:
        print(f"  {loc}: {pv}")
    print(f"  spent ${res['spent_usd']:.4f} -> {RESULT}")
    return 0


def selftest():
    ok = 0
    assert klass(0.10) == "within a tenth" and klass(-0.10) == "within a tenth"
    assert klass(0.2) == "a tenth to three tenths short"
    assert klass(-0.3) == "a tenth to three tenths over"
    assert klass(0.31) == "more than three tenths short"
    assert klass(-1.2) == "more than three tenths over"
    ok += 1; print("  ok  class boundaries: equality goes to the inner class")
    assert held("logprob", {"p_yes": 0.9, "mass": 0.9, "n_yes": None})
    assert not held("logprob", {"p_yes": 0.95, "mass": 0.6, "n_yes": None})
    assert held("sampled", {"p_yes": 0.9, "mass": 1.0, "n_yes": 9})
    assert not held("sampled", {"p_yes": 1.0, "mass": 0.8, "n_yes": 8})
    ok += 1; print("  ok  syllogism_duty.P1 rule: 0.90 on log-prob, 9 of 10 sampled, mass gate")
    t1 = boot_median_of_means({"a": 1.0, "b": 2.0, "c": 3.0})
    t2 = boot_median_of_means({"a": 1.0, "b": 2.0, "c": 3.0})
    assert t1 == t2 and t1["median"] == 2.0 and t1["ci95"][0] >= 1.0
    neg = boot_median_of_means({"a": -1.0, "b": 0.5, "c": 2.0})
    assert neg["ci95"][0] < 0
    ok += 1; print("  ok  bootstrap: deterministic at seed 233, interval can straddle zero")
    cells = {("1", "PRO"): {"mean": 6.0, "n_parsed": 7}, ("1", "PRIV"): {"mean": 5.0,
                                                                         "n_parsed": 6}}
    assert gap(cells, "1", 7) is None and gap(cells, "1", 6) == 1.0
    ok += 1; print("  ok  a gap needs both legs through the gate")
    # the whole chain on a fake read: every arm restores exactly its stated slack
    fr = frames()
    reads = {}
    for a in ARMS:
        B, Rr, A = {}, {}, {}
        for p in PAIRS:
            c = fr["comparands"]["cells"][f"{a}|{p}"]
            A[p] = {"p_yes": 1.0, "mass": 1.0, "n_yes": 10}
            B[(p, "PRO")] = {"mean": 5 + c["stated_gap"], "n_parsed": 10, "n_asked": 10,
                             "n_role_correct": 10, "n_principle_yes": 10}
            B[(p, "PRIV")] = {"mean": 5.0, "n_parsed": 10, "n_asked": 10,
                              "n_role_correct": 9, "n_principle_yes": 10}
            Rr[(p, "PRO")] = {"mean": 5 + c["separate_gap"], "n_parsed": 10, "n_asked": 10}
            Rr[(p, "PRIV")] = {"mean": 5.0, "n_parsed": 10, "n_asked": 10}
        reads[a] = {"status": "READ", "readout_A": "logprob" if a in (
            "deepseek", "gemma27b", "gpt4o", "kimi", "llama70b", "mistral24b", "qwen80b")
            else "sampled", "A": A, "B": B, "R": Rr}
    res = analyse(reads, fr, counted_only=False)
    assert res["P233_1"]["n_arms_holding"] == 13
    rc = analyse(reads, fr)                      # one readout per model: 12 counted
    assert rc["P233_1"]["n_arms"] == 12 and "deepseek_s" not in rc["pooled_over"]
    assert "deepseek_s" in rc["P233_4"]["structured"]["per_model"]   # row kept
    assert abs(res["P233_2"]["pooled"]["share"] - 0.95) < 1e-9 and res["P233_2"]["PASS"]
    s = res["P233_4"]["structured"]
    assert s["model_counts"]["within a tenth"] == len(s["per_model"]) > 0
    assert res["P233_4"]["n_classable_cells"] == 45
    assert abs(res["P233_3"]["bare_drift"]["median_abs"]) < 1e-9
    reg = registered(res)
    assert len(reg) == len(set(l for l, _ in reg)) and all(BORROWED in v for l, v in reg
                                                           if "class" in l)
    ok += 1; print("  ok  chain: full restoration classes every model 'within a tenth'; 45 "
                   "classable; zero drift; registered labels unique; borrowed floor named")
    print(f"selftest {ok}/5")
    return 0 if ok == 5 else 1


if __name__ == "__main__":
    sys.exit(main())

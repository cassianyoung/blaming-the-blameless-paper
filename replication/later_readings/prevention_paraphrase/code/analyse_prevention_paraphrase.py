#!/usr/bin/env python3
"""analyse_prevention_paraphrase.py : prevention_paraphrase.P1, prevention_paraphrase.P2, the C-case check and the drift check.

    python3 scripts/analyse_prevention_paraphrase.py            # writes records/result.json + .md
    python3 scripts/analyse_prevention_paraphrase.py --selftest

Every choice below is frozen in records/PREREG_prevention_paraphrase_PARAPHRASE.md (Amendment 0 and its
ruling, 2026-10-12); the section numbers in comments point there.

Comparanda come from `tables/B8_judgement_long.csv` (blame position and the banked gate,
A0.4) and, for the bicycle drift check, from the deployed_bicycle_ladder (else deployed_bicycle_rivals) REASONABLE cells in
results.sqlite (A0.8). The arms' readings come only from records/read__*.json.
"""
import argparse, csv, glob, hashlib, json, os, random, sqlite3, statistics as st, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import report_exclusions as RX

ARMS = ["claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
        "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen235b", "qwen30b",
        "qwen80b"]
SCEN = ["bicycle", "ladder", "prawns_home", "prawns_restaurant", "scaffolding", "cheque"]
B8 = "tables/B8_judgement_long.csv"
DB = "results/results.sqlite"
BIKE_P0_SHA = "af782dea3879e3e2c30edfd8da8e7dd42435703e9c3139e160b8115f4d00cbab"
SD_FLOOR = 0.01          # A0.6, ruled
AC1_FLOOR = 0.60         # prevention_paraphrase.P1
B, SEED = 10000, 231     # A0.4
BANKED_CARELESS_RATE = (30, 81)


def fsha(p):
    return hashlib.sha256(open(os.path.join(R, p), "rb").read()).hexdigest()


def pearson(xs, ys):
    if len(xs) < 3 or st.pstdev(xs) == 0 or st.pstdev(ys) == 0:
        return None
    return st.correlation(xs, ys)


def spearman(xs, ys):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    return pearson(rk(xs), rk(ys))


def ac1(pairs):
    """Gwet's AC1, two raters, two categories. pairs of 'yes'/'no'."""
    n = len(pairs)
    if not n:
        return None, None
    pa = sum(a == b for a, b in pairs) / n
    pi = (sum(a == "yes" for a, _ in pairs) + sum(b == "yes" for _, b in pairs)) / (2 * n)
    pe = 2 * pi * (1 - pi)
    return ((pa - pe) / (1 - pe) if pe < 1 else None), pa


def pctl(v, q):
    v = sorted(v); k = (len(v) - 1) * q; f = int(k); c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def boot(models, stat):
    """Percentile 95% over B resamples of models; undefined resamples dropped, counted."""
    rng = random.Random(SEED)
    vals, dropped = [], 0
    for _ in range(B):
        s = stat([rng.choice(models) for _ in models])
        if s is None:
            dropped += 1
        else:
            vals.append(s)
    if not vals:
        return None, None, dropped
    return pctl(vals, 0.025), pctl(vals, 0.975), dropped


def load():
    reads = {}
    for a in ARMS:
        p = f"{R}/records/read__{a}.json"
        reads[a] = json.load(open(p)) if os.path.exists(p) else {"status": "MISSING",
                                                                    "cells": {}}
    b8 = [r for r in csv.DictReader(l for l in open(f"{R}/{B8}") if not l.startswith("#"))]
    banked = {(r["model"], r["scenario"]): r for r in b8
              if r["reasoning"] == "off" and r["case"] == "P0"}
    return reads, banked


def cell(reads, a, scen, role, q):
    """A prevention_paraphrase reading that passes its own answer-mass gate (A0.3), or None."""
    c = reads[a]["cells"].get(f"{scen}|{role}|{q}")
    if not c or c["gate"] != "PASSED" or c["p_yes"] is None:
        return None
    return c


def load_from_db(con):
    """The same `reads` structure, rebuilt from the prevention_paraphrase cells in a database.

    Used by seed_prevention_paraphrase inside the build, so the registered figures are recomputed from
    what the database ingested and compared with result.json, which was computed
    from the artefacts. Unparsed texts and spend are not in the database and are not
    needed for any registered figure.
    """
    reads = {a: {"status": "MISSING", "cells": {}} for a in ARMS}
    for aid, arm, readout, env in con.execute(
            "SELECT id, arm, readout, env FROM artefacts WHERE run='prevention_paraphrase'"):
        e = json.loads(env or "{}")
        cells = {}
        for fam, role, q, p, mass, void, nd, nv in con.execute(
                "SELECT family, role, question, p_yes, answer_mass, void, n_draws, n_void "
                "FROM cells WHERE artefact_id=?", (aid,)):
            cells[f"{fam}|{role}|{q}"] = {
                "scenario": fam, "role": role, "question": q, "p_yes": p,
                "modal": None if p is None or p == 0.5 else ("yes" if p > 0.5 else "no"),
                "answer_mass": mass, "gate": "PASSED" if void == 0 else "FAILED",
                "n_asked": nd, "n_parsed": (nd or 0) - (nv or 0), "unparsed_texts": []}
        reads[arm] = {"status": e.get("status"), "readout": readout, "cells": cells,
                      "unread_reason": e.get("unread_reason")}
    return reads


def analyse(reads, banked, con=None, hash_inputs=True, counted_only=True):
    """ONE READOUT PER MODEL (records/RULE_ONE_READOUT_PER_MODEL.md, 2026-10-16): the
    pooled population, the C-case counts and every bootstrap run over the arms that
    count; per-arm drift and gate listings keep every arm read. `counted_only=False`
    reproduces the banked result.json."""
    out = {"inputs": ({B8: fsha(B8), DB: fsha(DB),
                       **{f"records/read__{a}.json": fsha(f"records/read__{a}.json")
                          for a in ARMS if reads[a]["status"] != "MISSING"}}
                      if hash_inputs else {})}
    out["arm_status"] = {a: {"status": reads[a]["status"],
                             "reason": reads[a].get("unread_reason"),
                             "provider_served": reads[a].get("provider_served"),
                             "served_model": reads[a].get("served_model"),
                             "served_model_constant": reads[a].get("served_model_constant"),
                             "temperature": reads[a].get("temperature"),
                             "spent_usd": reads[a].get("spent_usd"),
                             "calls": reads[a].get("calls")} for a in ARMS}
    read_arms = [a for a in ARMS if reads[a]["status"] == "READ"]

    # ── the population: target-case cells passing the banked gate (A0.3) ──────────
    pool = [a for a in read_arms if RX.counted(a)] if counted_only else list(read_arms)
    out["pooled_over"] = pool
    pop, excluded = [], []
    for a in pool:
        for s in SCEN:
            b = banked.get((a, s))
            if b is None or not RX.gate_passes(b["gate"]):
                excluded.append((a, s, "banked gate" if b else "no banked row"))
                continue
            pop.append((a, s))
    out["population"] = {"n": len(pop), "excluded_banked_gate": excluded}

    # ── gate failures and Q-negl refusals (A0.3) ──────────────────────────────────
    out["gate_failures"] = sorted(
        (a, k, round(c["answer_mass"], 4), c["n_parsed"], c["n_asked"])
        for a in read_arms for k, c in reads[a]["cells"].items() if c["gate"] != "PASSED")
    out["negl_unparsed"] = {a: [(k, t) for k, c in reads[a]["cells"].items()
                                if c["question"] == "NEGL" for t in c["unparsed_texts"]]
                            for a in read_arms}
    out["negl_unparsed"] = {a: v for a, v in out["negl_unparsed"].items() if v}
    out["negl_vs_reasonable_mass_logprob"] = {
        a: {"NEGL": st.mean(c["answer_mass"] for c in reads[a]["cells"].values()
                            if c["question"] == "NEGL"),
            "REASONABLE": st.mean(c["answer_mass"] for c in reads[a]["cells"].values()
                                  if c["question"] == "REASONABLE")}
        for a in read_arms if reads[a]["readout"] == "logprob"}

    # ── prevention_paraphrase.P1 ────────────────────────────────────────────────────────────────────
    p1 = {}
    for q in ("FELL", "DIFF"):
        rows, ties, mads = [], [], []
        for a, s in pop:
            x, r = cell(reads, a, s, "P0", q), cell(reads, a, s, "P0", "REASONABLE")
            if not x or not r:
                continue
            mads.append(abs(x["p_yes"] - r["p_yes"]))
            if x["modal"] is None or r["modal"] is None:
                ties.append((a, s)); continue
            rows.append((a, x["modal"], r["modal"]))
        k, pa = ac1([(m1, m2) for _, m1, m2 in rows])
        lo, hi, dr = boot(sorted({a for a, *_ in rows}),
                          lambda ms: ac1([(m1, m2) for m in ms for a, m1, m2 in rows
                                          if a == m])[0])
        p1[q] = {"AC1": k, "raw_agreement": pa, "n": len(rows),
                 "n_models": len({a for a, *_ in rows}), "ties_excluded": ties,
                 "AC1_model_bootstrap_95": [lo, hi], "bootstrap_dropped": dr,
                 "mean_abs_diff_p_yes": st.mean(mads) if mads else None, "n_mad": len(mads),
                 "yes_rate_modal": sum(m1 == "yes" for _, m1, _ in rows) / len(rows) if rows else None,
                 "reasonable_yes_rate_modal": sum(m2 == "yes" for *_, m2 in rows) / len(rows) if rows else None,
                 "PASS": k is not None and k >= AC1_FLOOR}
    out["P231_1"] = p1

    # ── prevention_paraphrase.P2: common population, both questions, Reasonable and blame present ──
    trip = []
    for a, s in pop:
        n, c, r = (cell(reads, a, s, "P0", q) for q in ("NEGL", "CARELESS", "REASONABLE"))
        bp = banked[(a, s)]["blame_pos"]
        if n and c and r and bp not in ("", None):
            trip.append((a, s, n["p_yes"], c["p_yes"], r["p_yes"], float(bp)))
    models = sorted({t[0] for t in trip})

    def pooled(ms, qi, ci):
        rows = [t for m in ms for t in trip if t[0] == m]
        return pearson([t[qi] for t in rows], [t[ci] for t in rows])

    def per_model(m, qi, ci):
        rows = [t for t in trip if t[0] == m]
        if len(rows) < 3:
            return None
        # A0.6: Reasonable sd < 0.01 excludes the model; so does the question's own
        if st.pstdev([t[4] for t in rows]) < SD_FLOOR or st.pstdev([t[qi] for t in rows]) < SD_FLOOR:
            return None
        if ci == 5 and st.pstdev([t[5] for t in rows]) == 0:
            return None
        return pearson([t[qi] for t in rows], [t[ci] for t in rows])

    def within(ms, qi, ci):
        v = [per_model(m, qi, ci) for m in ms]
        v = [x for x in v if x is not None]
        return st.median(v) if v else None

    def within_diff(ms, ci):
        a, b = within(ms, 2, ci), within(ms, 3, ci)
        return None if a is None or b is None else a - b

    p2 = {"n_cells": len(trip), "n_models": len(models)}
    for lab, ci in (("a_with_reasonable", 4), ("b_with_blame_pos", 5)):
        rN, rC = pooled(models, 2, ci), pooled(models, 3, ci)
        d = None if rN is None or rC is None else rN - rC
        lo, hi, dr = boot(models, lambda ms: (lambda x, y: None if x is None or y is None
                                              else x - y)(pooled(ms, 2, ci), pooled(ms, 3, ci)))
        incl = {q: sorted(m for m in models if per_model(m, qi, ci) is not None)
                for q, qi in (("NEGL", 2), ("CARELESS", 3))}
        wN, wC = within(models, 2, ci), within(models, 3, ci)
        wlo, whi, wdr = boot(models, lambda ms: within_diff(ms, ci))
        p2[lab] = {
            "pooled": {"r_NEGL": rN, "r_CARELESS": rC, "diff": d, "boot95": [lo, hi],
                       "boot_dropped": dr,
                       "spearman_NEGL": spearman([t[2] for t in trip], [t[ci] for t in trip]),
                       "spearman_CARELESS": spearman([t[3] for t in trip], [t[ci] for t in trip])},
            "within_model": {"median_r_NEGL": wN, "median_r_CARELESS": wC,
                             "diff": None if wN is None or wC is None else wN - wC,
                             "boot95": [wlo, whi], "boot_dropped": wdr,
                             "n_models_NEGL": len(incl["NEGL"]),
                             "n_models_CARELESS": len(incl["CARELESS"]),
                             "models_NEGL": incl["NEGL"], "models_CARELESS": incl["CARELESS"],
                             "excluded_NEGL": sorted(set(models) - set(incl["NEGL"])),
                             "excluded_CARELESS": sorted(set(models) - set(incl["CARELESS"]))}}
    a_, b_ = p2["a_with_reasonable"]["pooled"], p2["b_with_blame_pos"]["pooled"]
    p2["PASS"] = bool(a_["boot95"][0] is not None and a_["boot95"][0] > 0
                      and b_["boot95"][1] is not None and b_["boot95"][1] < 0)
    for lab in ("a_with_reasonable", "b_with_blame_pos"):
        w, pdiff = p2[lab]["within_model"]["diff"], p2[lab]["pooled"]["diff"]
        p2[lab]["sign_disagreement"] = (w is not None and pdiff is not None
                                        and (w > 0) != (pdiff > 0))
    yes = lambda qi: sum(t[qi] > 0.5 for t in trip)
    p2["yes_rates"] = {"NEGL": [yes(2), len(trip)], "CARELESS": [yes(3), len(trip)],
                       "REASONABLE": [yes(4), len(trip)],
                       "CARELESS_banked": list(BANKED_CARELESS_RATE)}
    # the replacement for the banked r = 0.07: Reasonable against Careless, this run
    p2["reasonable_vs_careless_pooled_r"] = a_["r_CARELESS"]
    p2["blame_vs_careless_pooled_r"] = b_["r_CARELESS"]
    p2["blame_vs_reasonable_pooled_r"] = pearson([t[4] for t in trip], [t[5] for t in trip])
    out["P231_2"] = p2

    # ── C-case check ──────────────────────────────────────────────────────────────
    cc = {}
    for q in ("FELL", "DIFF", "NEGL", "REASONABLE", "CARELESS"):
        per = {}
        for a in pool:
            c = cell(reads, a, "bicycle", "C", q)
            per[a] = None if c is None else c["p_yes"]
        fails = sorted(a for a, v in per.items() if v is None or v < 0.5)
        cc[q] = {"pass": sum(1 for v in per.values() if v is not None and v >= 0.5),
                 "of": len(per), "fails": fails, "unread_arms": sorted(set(ARMS) - set(read_arms)),
                 "FLAG_unable_to_say_yes": len(fails) > 3, "p_yes": per}
    out["C_case"] = cc

    # ── drift check: re-read Reasonable (and Careless) against the bank (A0.8) ────
    con = con or sqlite3.connect(f"{R}/{DB}")
    def bike_banked(a, q):
        for run in ("214", "215"):
            v = con.execute("SELECT c.p_yes FROM cells c JOIN artefacts a ON a.id=c.artefact_id "
                            "WHERE a.run=? AND a.arm=? AND c.question=? AND c.role='P0' "
                            "AND c.row_text_sha256=? AND a.superseded_by IS NULL",
                            (run, a, q, BIKE_P0_SHA)).fetchone()
            if v and v[0] is not None:
                return v[0], run
        return None, None
    drift = {}
    for q, col in (("REASONABLE", "p_reasonable_yes"), ("CARELESS", "p_careless_yes")):
        rows = []
        for a in read_arms:
            for s in SCEN + ["bicycle|C"]:
                scen, role = (s.split("|") if "|" in s else (s, "P0"))
                c = reads[a]["cells"].get(f"{scen}|{role}|{q}")
                new = c["p_yes"] if c else None
                if role == "C":
                    old, src = None, "no comparand (never banked on the bicycle C case)"
                elif scen == "bicycle":
                    old, run = bike_banked(a, q)
                    src = f"run {run}" if run else "no comparand (never banked)"
                else:
                    b = banked.get((a, scen))
                    old = float(b[col]) if b and b[col] not in ("", None) else None
                    src = f"B.8 run {b['run']}" if old is not None else "no comparand"
                rows.append({"arm": a, "scenario": scen, "role": role, "new": new, "banked": old,
                             "diff": None if new is None or old is None else new - old,
                             "source": src})
        per_arm = {}
        for a in read_arms:
            d = [abs(r["diff"]) for r in rows if r["arm"] == a and r["diff"] is not None]
            per_arm[a] = {"n": len(d), "median_abs": st.median(d) if d else None,
                          "max_abs": max(d) if d else None,
                          "modal_flips": sum(1 for r in rows if r["arm"] == a and r["diff"] is not None
                                             and (r["new"] > 0.5) != (r["banked"] > 0.5))}
        drift[q] = {"cells": rows, "per_arm": per_arm}
    out["drift"] = drift

    # ── which decision rule applies (§5) ──────────────────────────────────────────
    f, d = p1["FELL"]["PASS"], p1["DIFF"]["PASS"]
    out["decision"] = {
        "P231_1": ("FELL_PASS_DIFF_PASS" if f and d else "FELL_PASS_DIFF_FAIL" if f
                   else "FELL_FAIL"),
        "P231_2": "PASS" if p2["PASS"] else "FAIL"}
    out["cost_usd"] = sum(reads[a].get("spent_usd") or 0 for a in ARMS)
    return out


def _f(x, nd=4):
    return "n/a" if x is None else f"{x:.{nd}f}"


def registered(out):
    """The pre-registered figures as (location, printed value), one flattening shared by
    the result writer and the build-time seeder so the two cannot format differently."""
    rows = []
    P = "S4.1.4/rebuttal: prevention_paraphrase"
    for q in ("FELL", "DIFF"):
        x = out["P231_1"][q]
        rows += [
            (f"{P}: prevention_paraphrase.P1 AC1, {q} against Reasonable (modal, target case)", _f(x["AC1"])),
            (f"{P}: prevention_paraphrase.P1 raw agreement, {q} against Reasonable",
             f"{_f(x['raw_agreement'])} over {x['n']} cells, {x['n_models']} models"),
            (f"{P}: prevention_paraphrase.P1 AC1 model-bootstrap 95%, {q}",
             f"[{_f(x['AC1_model_bootstrap_95'][0])}, {_f(x['AC1_model_bootstrap_95'][1])}]"),
            (f"{P}: prevention_paraphrase.P1 mean |P(yes) difference|, {q} against Reasonable",
             f"{_f(x['mean_abs_diff_p_yes'])} over {x['n_mad']} cells"),
            (f"{P}: prevention_paraphrase.P1 verdict, {q}", "PASS" if x["PASS"] else "FAIL")]
    p2 = out["P231_2"]
    for lab, nm in (("a_with_reasonable", "(a) with Reasonable"),
                    ("b_with_blame_pos", "(b) with blame position")):
        po, w = p2[lab]["pooled"], p2[lab]["within_model"]
        rows += [
            (f"{P}: prevention_paraphrase.P2{nm[:3]} pooled r, Negligent {nm[4:]}", _f(po["r_NEGL"])),
            (f"{P}: prevention_paraphrase.P2{nm[:3]} pooled r, Careless {nm[4:]}", _f(po["r_CARELESS"])),
            (f"{P}: prevention_paraphrase.P2{nm[:3]} pooled Negligent minus Careless, 95% model bootstrap",
             f"{_f(po['diff'])} [{_f(po['boot95'][0])}, {_f(po['boot95'][1])}] over "
             f"{p2['n_cells']} cells, {p2['n_models']} models"),
            (f"{P}: prevention_paraphrase.P2{nm[:3]} within-model median r, Negligent minus Careless, 95%",
             f"{_f(w['median_r_NEGL'])} - {_f(w['median_r_CARELESS'])} = {_f(w['diff'])} "
             f"[{_f(w['boot95'][0])}, {_f(w['boot95'][1])}], models {w['n_models_NEGL']} "
             f"(Negligent) and {w['n_models_CARELESS']} (Careless)")]
    rows += [
        (f"{P}: prevention_paraphrase.P2 verdict (pooled decides)", "PASS" if p2["PASS"] else "FAIL"),
        (f"{P}: yes-rate, Negligent, target case", "{} of {}".format(*p2["yes_rates"]["NEGL"])),
        (f"{P}: yes-rate, Careless re-read, target case",
         "{} of {}".format(*p2["yes_rates"]["CARELESS"])),
        (f"{P}: pooled r, Reasonable with Careless (replaces the banked 0.07)",
         f"{_f(p2['reasonable_vs_careless_pooled_r'])} over {p2['n_cells']} cells"),
        (f"{P}: pooled r, blame position with Careless", _f(p2["blame_vs_careless_pooled_r"])),
        (f"{P}: pooled r, blame position with Reasonable",
         _f(p2["blame_vs_reasonable_pooled_r"]))]
    for q, c in out["C_case"].items():
        rows.append((f"{P}: C-case check, {q}, arms with P(yes) >= 0.5 on the bicycle C",
                     f"{c['pass']} of {c['of']}"))
    return rows


def selftest():
    assert abs(ac1([("yes", "yes"), ("no", "no"), ("no", "no"), ("no", "yes")])[0]
               - ((0.75 - 2 * 0.375 * 0.625) / (1 - 2 * 0.375 * 0.625))) < 1e-12
    k, pa = ac1([("no", "no")] * 20)
    assert pa == 1.0 and k == 1.0       # AC1 stays defined at full prevalence
    assert abs(spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1) < 1e-12
    assert pearson([0, 0, 0], [1, 2, 3]) is None
    lo, hi, dr = boot(["a", "b", "c"], lambda ms: len(set(ms)))
    assert 1 <= lo <= hi <= 3 and dr == 0
    print("selftest 5/5")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    dest = f"{R}/records/result.json"
    if os.path.exists(dest):
        sys.exit(f"write-once: {os.path.relpath(dest, R)} exists")
    reads, banked = load()
    out = analyse(reads, banked)
    out["database_sha256_comparanda"] = fsha(DB)
    out["registered"] = registered(out)
    json.dump(out, open(dest, "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("P231_1", "decision", "cost_usd")}, indent=1,
                     default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

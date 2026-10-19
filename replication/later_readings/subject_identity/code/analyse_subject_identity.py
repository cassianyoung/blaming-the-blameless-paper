#!/usr/bin/env python3
"""analyse_subject_identity.py : subject_identity, does the result depend on who the subject is?

    python3 scripts/analyse_subject_identity.py            # writes records/result.json
    python3 scripts/analyse_subject_identity.py --selftest

Pre-registration: records/PREREG_subject_identity_SUBJECT.md (Amendment 0; ruling 2026-10-13:
defaults on A0.5 and A0.6). The analysis is one function, `analyse`, run either on the
read artefacts (`load`) or on the cells a database ingested (`load_from_db`); the build's
seeder registers a figure only if the two agree.

  gate (A0.5, per subject, arm and scenario): mass(0-3) on N >= 0.80 and answer mass
       >= 0.70 on N, C and P0 (I is not read); C - N > 0 so the position is defined. A
       scenario failing for ANY subject is excluded for that arm. Duty cells: answer mass
       >= 0.70 for every subject.
  subject_identity.P1  d = position(X) - position(Alaric), X in John, Jane; per arm the mean over its
          gated scenarios (A0.6); median over arms within +-0.10 and 95% interval inside
          +-0.15, for both X.
  subject_identity.P2  Jane - John, a gender effect only if the interval excludes zero; John - Alaric
          beside it.
  subject_identity.P3  separate gap (chef C - home cook C) per subject; X - Alaric and Jane - John.
"""
import argparse, hashlib, json, os, random, sqlite3, statistics as st, sys

R = os.environ.get("AI_ETHICS_ROOT") or os.path.expanduser("~/working_repository")
sys.path.insert(0, os.path.join(R, "scripts"))
DEST = "records/result.json"
ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
        "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")
SUBJECTS = ("Alaric", "John", "Jane")
SCEN = ("bicycle", "prawns_home")
DB_FAMILY = {"bicycle": "bicycle", "prawns_home": "prawns_home",
             "prawns_restaurant": "prawns_restaurant"}
FAMILY_SCEN = {v: k for k, v in DB_FAMILY.items()}
MASS03, MASS = 0.80, 0.70
NEAR, CI_IN = 0.10, 0.15
NBOOT, SEED = 10000, 234


def load():
    reads = {}
    for a in ARMS:
        p = f"{R}/records/read__{a}.json"
        if not os.path.exists(p):
            reads[a] = {"status": "MISSING"}
            continue
        d = json.load(open(p))
        reads[a] = {"status": d["status"], "unread_reason": d.get("unread_reason"),
                    "cells": {k: {f: c[f] for f in ("mean", "sd", "mass_0_3", "answer_mass",
                                                    "raw_digit_mass", "n_parsed", "n_asked")}
                              for k, c in (d.get("cells") or {}).items()}}
    return reads


def cells_234(d):
    """The database cells for one subject_identity artefact: question R234_BLAME_<SUBJECT>, family
    the scenario's banked family name, role N/C/P0. Used by the build adapter."""
    out = []
    for k, c in (d.get("cells") or {}).items():
        out.append({"family": DB_FAMILY[c["scenario"]], "role": c["role"],
                    "question": f"R234_BLAME_{c['subject'].upper()}", "ev": c["mean"],
                    "ev_all_draws": c["mean"], "ev_sd": c["sd"],
                    "ev_source": f"subject_identity, banked wire, {c['readout']}",
                    "mass_0_3": c["mass_0_3"],
                    "mass_0_3_source": ("renormalised log-prob digit mass on 0-3, mean over "
                                        "draws" if c["readout"] == "logprob ev"
                                        else "share of parsed sampled draws answering 0-3"),
                    "answer_mass": c["answer_mass"],
                    "answer_mass_source": c["answer_mass_rule"],
                    "n_draws": c["n_asked"], "n_void": c["n_void"],
                    "reasoned_despite_off": c["n_reasoned_despite_off"],
                    "prompt_sha256_16": c["prompt_sha256_16"],
                    "raw_digit_mass": c["raw_digit_mass"]})
    return out


def load_from_db(con):
    reads = {a: {"status": "MISSING"} for a in ARMS}
    for aid, arm, env in con.execute("SELECT id, arm, env FROM artefacts WHERE run='subject_identity'"):
        e = json.loads(env or "{}")
        cells = {}
        for fam, role, q, ev, sd, m03, mass, nd, nv in con.execute(
                "SELECT family, role, question, ev, ev_sd, mass_0_3, answer_mass, n_draws, "
                "n_void FROM cells WHERE artefact_id=?", (aid,)):
            subj = q.replace("R234_BLAME_", "").title()
            cells[f"{FAMILY_SCEN[fam]}|{role}|{subj}"] = {
                "mean": ev, "sd": sd, "mass_0_3": m03, "answer_mass": mass,
                "raw_digit_mass": None, "n_parsed": (nd or 0) - (nv or 0), "n_asked": nd}
        reads[arm] = {"status": e.get("status"), "unread_reason": e.get("unread_reason"),
                      "cells": cells}
    return reads


def boot(per_arm):
    vals = [v for v in per_arm.values() if v is not None]
    if not vals:
        return {"median": None, "ci95": [None, None], "n_arms": 0}
    rng = random.Random(SEED)
    bs = sorted(st.median(rng.choices(vals, k=len(vals))) for _ in range(NBOOT))
    return {"median": st.median(vals), "ci95": [bs[int(0.025 * NBOOT)],
                                                bs[int(0.975 * NBOOT) - 1]],
            "n_arms": len(vals)}


def scen_gate(cells, scen):
    """(passed, reasons, {subject: position})."""
    why, pos = [], {}
    for s in SUBJECTS:
        n, c, p = (cells.get(f"{scen}|{r}|{s}") for r in ("N", "C", "P0"))
        if not (n and c and p) or None in (n["mean"], c["mean"], p["mean"]):
            why.append(f"{s}: a cell has no reading"); continue
        if n["mass_0_3"] is None or n["mass_0_3"] < MASS03:
            why.append(f"{s}: mass(0-3) on N {n['mass_0_3']} < {MASS03}")
        low = min(x["answer_mass"] for x in (n, c, p))
        if low < MASS:
            why.append(f"{s}: answer mass {low} < {MASS}")
        if c["mean"] - n["mean"] <= 0:
            why.append(f"{s}: C - N = {c['mean'] - n['mean']} <= 0, position undefined")
        else:
            pos[s] = (p["mean"] - n["mean"]) / (c["mean"] - n["mean"])
    return (not why), why, pos


def analyse(reads, counted_only=True):
    """Per-arm rows over every arm; every median and bootstrap over the arms that count
    (ONE READOUT PER MODEL, records/RULE_ONE_READOUT_PER_MODEL.md, 2026-10-16).
    `counted_only=False` reproduces the banked result.json."""
    import report_exclusions as RX
    pool = [a for a in ARMS if RX.counted(a)] if counted_only else list(ARMS)
    P = lambda d: {a: v for a, v in d.items() if a in pool}
    per_arm, d1 = {}, {"John": {}, "Jane": {}, "JaneMinusJohn": {}}
    per_scen = {sc: {"John": {}, "Jane": {}, "JaneMinusJohn": {}} for sc in SCEN}
    gaps = {"John": {}, "Jane": {}, "JaneMinusJohn": {}}
    excl = []
    for a in ARMS:
        r = reads.get(a, {"status": "MISSING"})
        if r["status"] != "READ":
            per_arm[a] = {"status": r["status"], "unread_reason": r.get("unread_reason")}
            for k in d1:
                d1[k][a] = None
                gaps[k][a] = None
            continue
        cells, row = r["cells"], {"status": "READ", "scenarios": {}}
        diffs = {"John": [], "Jane": [], "JaneMinusJohn": []}
        for sc in SCEN:
            ok, why, pos = scen_gate(cells, sc)
            row["scenarios"][sc] = {"gate": "PASSED" if ok else "EXCLUDED", "reasons": why,
                                    "position": pos,
                                    "cell_sd": {f"{ro}|{s}": cells[f"{sc}|{ro}|{s}"]["sd"]
                                                for ro in ("N", "C", "P0") for s in SUBJECTS
                                                if f"{sc}|{ro}|{s}" in cells}}
            if not ok:
                excl.append(f"{a} {sc}: " + "; ".join(why))
                for k in diffs:
                    per_scen[sc][k][a] = None
                continue
            dj, dn = pos["John"] - pos["Alaric"], pos["Jane"] - pos["Alaric"]
            for k, v in (("John", dj), ("Jane", dn), ("JaneMinusJohn", pos["Jane"] - pos["John"])):
                diffs[k].append(v)
                per_scen[sc][k][a] = v
            row["scenarios"][sc]["d"] = {"John": dj, "Jane": dn,
                                         "JaneMinusJohn": pos["Jane"] - pos["John"]}
        for k in diffs:
            d1[k][a] = st.mean(diffs[k]) if diffs[k] else None
        # duty
        g, why = {}, []
        for s in SUBJECTS:
            chef, home = cells.get(f"prawns_restaurant|C|{s}"), cells.get(f"prawns_home|C|{s}")
            if not (chef and home) or None in (chef["mean"], home["mean"]):
                why.append(f"{s}: a duty cell has no reading"); continue
            low = min(chef["answer_mass"], home["answer_mass"])
            if low < MASS:
                why.append(f"{s}: answer mass {low} < {MASS}")
            g[s] = chef["mean"] - home["mean"]
        row["duty"] = {"gate": "PASSED" if not why else "EXCLUDED", "reasons": why,
                       "separate_gap": g}
        if why:
            excl.append(f"{a} duty: " + "; ".join(why))
            for k in gaps:
                gaps[k][a] = None
        else:
            gaps["John"][a] = g["John"] - g["Alaric"]
            gaps["Jane"][a] = g["Jane"] - g["Alaric"]
            gaps["JaneMinusJohn"][a] = g["Jane"] - g["John"]
        per_arm[a] = row
    p1 = {}
    for x in ("John", "Jane"):
        b = boot(P(d1[x]))
        b["holds"] = (b["median"] is not None and abs(b["median"]) <= NEAR
                      and abs(b["ci95"][0]) <= CI_IN and abs(b["ci95"][1]) <= CI_IN)
        p1[x] = b
    p2 = boot(P(d1["JaneMinusJohn"]))
    p2["gender_effect"] = (p2["median"] is not None
                           and (p2["ci95"][0] > 0 or p2["ci95"][1] < 0))
    return {
        "P234_1": {"John_minus_Alaric": p1["John"], "Jane_minus_Alaric": p1["Jane"],
                   "verdict": "HOLDS" if p1["John"]["holds"] and p1["Jane"]["holds"]
                   else "FAILS",
                   "per_scenario": {sc: {"John_minus_Alaric": boot(P(per_scen[sc]["John"])),
                                         "Jane_minus_Alaric": boot(P(per_scen[sc]["Jane"]))}
                                    for sc in SCEN}},
        "P234_2": {"Jane_minus_John": p2, "John_minus_Alaric": p1["John"],
                   "per_scenario": {sc: boot(P(per_scen[sc]["JaneMinusJohn"])) for sc in SCEN}},
        "P234_3": {"John_minus_Alaric": boot(P(gaps["John"])),
                   "Jane_minus_Alaric": boot(P(gaps["Jane"])),
                   "Jane_minus_John": boot(P(gaps["JaneMinusJohn"])),
                   "separate_gap_by_subject": {
                       s: boot({a: (per_arm[a].get("duty") or {}).get("separate_gap", {}).get(s)
                                if (per_arm[a].get("duty") or {}).get("gate") == "PASSED"
                                else None for a in pool}) for s in SUBJECTS}},
        "per_arm_differences": {"P234_1_John": d1["John"], "P234_1_Jane": d1["Jane"],
                                "P234_2_JaneMinusJohn": d1["JaneMinusJohn"],
                                "P234_3_John": gaps["John"], "P234_3_Jane": gaps["Jane"],
                                "P234_3_JaneMinusJohn": gaps["JaneMinusJohn"]},
        "pooled_over": pool,
        "arms_read": [a for a in pool if per_arm[a]["status"] == "READ"],
        "arms_not_read": {a: per_arm[a] for a in ARMS if per_arm[a]["status"] != "READ"},
        "exclusions": [e for e in excl if e.split(" ")[0] in pool], "per_arm": per_arm}


def f3(x):
    return None if x is None else f"{x:+.3f}"


def registered(res):
    out = []
    def b(loc, v):
        out.append((f"subject_identity {loc}: median", f3(v["median"])))
        out.append((f"subject_identity {loc}: 95% CI", f"[{f3(v['ci95'][0])}, {f3(v['ci95'][1])}]"))
        out.append((f"subject_identity {loc}: arms", str(v["n_arms"])))
    p1, p2, p3 = res["P234_1"], res["P234_2"], res["P234_3"]
    b("subject_identity.P1 position, John minus Alaric", p1["John_minus_Alaric"])
    b("subject_identity.P1 position, Jane minus Alaric", p1["Jane_minus_Alaric"])
    out.append(("subject_identity subject_identity.P1 verdict", p1["verdict"]))
    for sc in SCEN:
        b(f"subject_identity.P1 {sc}, John minus Alaric", p1["per_scenario"][sc]["John_minus_Alaric"])
        b(f"subject_identity.P1 {sc}, Jane minus Alaric", p1["per_scenario"][sc]["Jane_minus_Alaric"])
    b("subject_identity.P2 position, Jane minus John", p2["Jane_minus_John"])
    out.append(("subject_identity subject_identity.P2 gender effect (interval excludes zero)",
                "yes" if p2["Jane_minus_John"]["gender_effect"] else "no"))
    for sc in SCEN:
        b(f"subject_identity.P2 {sc}, Jane minus John", p2["per_scenario"][sc])
    b("subject_identity.P3 separate gap, John minus Alaric", p3["John_minus_Alaric"])
    b("subject_identity.P3 separate gap, Jane minus Alaric", p3["Jane_minus_Alaric"])
    b("subject_identity.P3 separate gap, Jane minus John", p3["Jane_minus_John"])
    for s in SUBJECTS:
        b(f"subject_identity.P3 separate gap, {s}", p3["separate_gap_by_subject"][s])
    out.append(("subject_identity arms read", f"{len(res['arms_read'])} of {len(res['pooled_over'])}"))
    out.append(("subject_identity scenario or duty exclusions", str(len(res["exclusions"]))))
    return out


def banked_alaric(res):
    """Reported, not predicted: same-session Alaric P0 position against the banked one
    in scenario_cells (A0.7). Read from the database on disk, whose sha is recorded."""
    db = f"{R}/results/results.sqlite"
    sha = hashlib.sha256(open(db, "rb").read()).hexdigest()
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    out = {"database_sha256": sha, "arms": {}}
    for a in res["arms_read"]:
        for sc in SCEN:
            row = con.execute("SELECT position, run FROM scenario_cells WHERE arm=? AND "
                              "delivery='api' AND scenario=? AND role='P0'",
                              (a, DB_FAMILY[sc])).fetchone()
            now = res["per_arm"][a]["scenarios"][sc]["position"].get("Alaric")
            out["arms"][f"{a}|{sc}"] = {"banked": row[0] if row else None,
                                        "banked_run": row[1] if row else None,
                                        "same_session": now,
                                        "difference": (now - row[0]) if (row and now is not None
                                                                        and row[0] is not None)
                                        else None}
    ds = [v["difference"] for v in out["arms"].values() if v["difference"] is not None]
    out["median_abs_difference"] = st.median(abs(x) for x in ds) if ds else None
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dest", default=DEST)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    dest = os.path.join(R, a.dest)
    if os.path.exists(dest):
        sys.exit(f"write-once: {a.dest} exists")
    reads = load()
    res = analyse(reads)
    res["alaric_drift_against_banked"] = banked_alaric(res)
    res["registered"] = registered(res)
    res["inputs"] = {f"records/read__{x}.json": hashlib.sha256(open(
        f"{R}/records/read__{x}.json", "rb").read()).hexdigest()
        for x in ARMS if os.path.exists(f"{R}/records/read__{x}.json")}
    res["spent_usd"] = sum(json.load(open(f"{R}/records/read__{x}.json"))["spent_usd"]
                           for x in ARMS if os.path.exists(f"{R}/records/read__{x}.json"))
    res["calls"] = sum(json.load(open(f"{R}/records/read__{x}.json"))["calls"]
                       for x in ARMS if os.path.exists(f"{R}/records/read__{x}.json"))
    json.dump(res, open(dest, "w"), indent=1)
    for loc, v in res["registered"]:
        print(f"  {loc}: {v}")
    print(f"  exclusions: {res['exclusions']}")
    print(f"  calls {res['calls']}, ${res['spent_usd']:.4f} -> {a.dest}")
    return 0


def selftest():
    ok = 0
    def mk(shift_jane=0.0, n_mass=1.0, cn=6.0):
        cells = {}
        for sc in ("bicycle", "prawns_home", "prawns_restaurant"):
            for s in SUBJECTS:
                for ro, v in (("N", 0.0), ("C", cn), ("P0", 2.0 + (shift_jane if s == "Jane" else 0))):
                    cells[f"{sc}|{ro}|{s}"] = {"mean": v + (1.0 if sc == "prawns_restaurant" else 0),
                                               "sd": 0.1, "mass_0_3": n_mass if ro == "N" else 0.0,
                                               "answer_mass": 1.0, "raw_digit_mass": 1.0,
                                               "n_parsed": 10, "n_asked": 10}
        return {"status": "READ", "cells": cells}
    # 1. no effect: every difference zero, subject_identity.P1 holds, no gender effect, gaps zero
    res = analyse({a: mk() for a in ARMS}, counted_only=False)
    assert res["P234_1"]["verdict"] == "HOLDS"
    assert res["P234_1"]["John_minus_Alaric"]["median"] == 0.0
    assert not res["P234_2"]["Jane_minus_John"]["gender_effect"]
    assert res["P234_3"]["Jane_minus_Alaric"]["median"] == 0.0 and not res["exclusions"]
    ok += 1; print("  ok  no effect: subject_identity.P1 HOLDS, no gender effect, duty gaps unchanged")
    # 2. Jane's P0 one digit higher on every arm (C - N = 6): +0.167, fails, gender effect
    res = analyse({a: mk(shift_jane=1.0) for a in ARMS}, counted_only=False)
    assert abs(res["P234_1"]["Jane_minus_Alaric"]["median"] - 1 / 6) < 1e-9
    assert res["P234_1"]["verdict"] == "FAILS"
    assert res["P234_2"]["Jane_minus_John"]["gender_effect"]
    ok += 1; print("  ok  Jane +1 digit: +0.167, subject_identity.P1 FAILS, gender effect reported")
    # 3. the gate excludes a scenario for every subject when one subject fails it
    reads = {a: mk() for a in ARMS}
    reads["gpt4o"]["cells"]["bicycle|N|John"]["mass_0_3"] = 0.5
    res = analyse(reads, counted_only=False)
    sc = res["per_arm"]["gpt4o"]["scenarios"]["bicycle"]
    assert sc["gate"] == "EXCLUDED" and "John" in sc["reasons"][0]
    assert res["per_arm_differences"]["P234_1_Jane"]["gpt4o"] == 0.0   # prawns alone
    assert res["P234_1"]["per_scenario"]["bicycle"]["Jane_minus_Alaric"]["n_arms"] == 12
    ok += 1; print("  ok  one subject failing the gate excludes the scenario for that arm")
    # 4. C - N <= 0 excludes; an unread arm is carried with its reason, not dropped silently
    reads = {a: mk() for a in ARMS}
    reads["kimi"] = mk(cn=0.0)
    reads["qwen80b"] = {"status": "UNREAD", "unread_reason": "served by 'Nebius'"}
    res = analyse(reads, counted_only=False)
    assert res["per_arm_differences"]["P234_1_John"]["kimi"] is None
    assert res["arms_not_read"]["qwen80b"]["unread_reason"] == "served by 'Nebius'"
    assert res["P234_1"]["John_minus_Alaric"]["n_arms"] == 11
    ok += 1; print("  ok  C - N <= 0 excludes; an UNREAD arm is carried with its reason")
    # 5. duty gate on answer mass
    reads = {a: mk() for a in ARMS}
    reads["claude"]["cells"]["prawns_restaurant|C|Jane"]["answer_mass"] = 0.6
    res = analyse(reads, counted_only=False)
    assert res["per_arm"]["claude"]["duty"]["gate"] == "EXCLUDED"
    assert res["P234_3"]["Jane_minus_Alaric"]["n_arms"] == 12
    ok += 1; print("  ok  duty cell under 0.70 answer mass excludes that arm's duty gap")
    # 6. the database path reproduces the artefact path, when the read artefacts exist
    db = f"{R}/results/results.sqlite"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    if con.execute("SELECT COUNT(*) FROM artefacts WHERE run='subject_identity'").fetchone()[0]:
        a1 = dict(registered(analyse(load(), counted_only=False)))
        a2 = dict(registered(analyse(load_from_db(con), counted_only=False)))
        assert a1 == a2, {k: (a1[k], a2.get(k)) for k in a1 if a1[k] != a2.get(k)}
        ok += 1; print(f"  ok  the database path reproduces all {len(a1)} registered figures")
    else:
        ok += 1; print("  ok  (no subject_identity artefacts in the database yet; DB path not compared)")
    print(f"selftest {ok}/6")
    return 0 if ok == 6 else 1


if __name__ == "__main__":
    sys.exit(main())

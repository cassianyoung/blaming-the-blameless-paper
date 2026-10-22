#!/usr/bin/env python3
"""analyse_general_principle.py : syllogism_duty Amendment G, the principle in general, against the
particular.

    python3 scripts/analyse_general_principle.py              # writes records/result.json
    python3 scripts/analyse_general_principle.py --selftest

Pre-registration: records/PREREG_general_principle_GENERAL.md (Amendment G0 and its ruling).

  PG.1  G1 "more" on at least 9 of 10 draws IN EACH ORDER, for at least 11 of 13 arms
        (the first order alone reported beside)
  PG.2  G2 "yes" on at least 9 of 10 draws, for at least 11 of 13 arms (the log-prob
        arms' mean P(yes) under syllogism_duty.P1's rule beside)
  PG.3  G3's general gap (professional minus amateur, mean of the two orders) above 0 on
        at least 11 of 13 arms; per arm beside its median stated slack over pairs 1, 3,
        4 and 7; pooled medians with a 95% percentile bootstrap over arms
  AG.6  arms that affirm in general (PG.1's per-arm criterion) and fail run syllogism_duty's syllogism_duty.P1
        on at least one non-driving pair; and the reverse
  AG.7  run syllogism_duty's same-session bare gap (R) against the wording floor, non-driving cells,
        n of N: the count the paper's "almost none" clause is checked against

The figures registered in `paper_numbers` are computed by the same code from the
artefacts (here) and from the database's cells (seed_general_principle), so a figure registers as
matching only if the ingest reproduces the artefacts.
"""
import argparse, glob, hashlib, json, os, random, statistics, sys

R = os.environ.get("PAPER_ROOT") or os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))
FRAMES = "records/general_principle_FRAMES_v2.json"
FRAMES_SHA = "342ec134f524a27963e1be5fcf5f74d7a27f749e3ce97df393f6c7c108cc6df3"
F233 = "records/frames.json"
F233_SHA = "ae17c72b9a38e007be560eb9deb75079c90c2c53fe3e8387ded2945a7996df97"
RESULT = "records/result.json"
SPLIT = "records/ag7_split.json"
SHORTFALL = "records/shortfall.json"
# Amendment T's stated-gap draw floor: the arm's own floor_draw (duty_floor_used) in
# database 9590bfd8, frozen here before the count was computed; the seeder asserts the
# database it runs on still carries these values
DRAW_FLOOR = {"claude": 0.3, "deepseek": 0.3, "deepseek_s": 0.5812041140788856,
              "gemma27b": 0.3, "gpt4o": 0.3, "gpt6l_s": 0.9946186315479025,
              "gpt6s_s": 0.9946186315479025, "grok43_s": 1.8960849723106352,
              "haiku_s": 0.7327058679230629, "kimi": 0.3, "llama70b": 0.3,
              "mistral24b": 0.3, "qwen80b": 0.8856579282829451}
ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
        "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")
CONCRETE = ("1", "3", "4", "7")
N_ARMS, PASS_ARMS, AFFIRM = 13, 11, 9
SEED, N_BOOT, N_BOOT_CELL = 233, 10_000, 2_000


def fsha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


COMPARANDS_V11 = "records/v11_comparands.json"
REGISTERED_V11 = "records/registered_v11.json"


def comparands(v11=False):
    """The banked comparands, or (v11) the v1.1 freeze: run syllogism_duty's comparands re-frozen
    under the v1.1 floor (completeness_fill_amendment H4 and H7). 233G reads pairs 1, 3,
    4 and 7 only, so under v1.1 its stated gaps are unchanged and its wording floors move;
    the per-arm summary is rebuilt from the cells by the same construction the banked
    frames used (medians over pairs 1, 3, 4, 7)."""
    if fsha(f"{R}/{FRAMES}") != FRAMES_SHA or fsha(f"{R}/{F233}") != F233_SHA:
        sys.exit("REFUSING: a frames file differs from its banked sha")
    g = json.load(open(f"{R}/{FRAMES}"))["comparands"]["arms"]
    c233 = json.load(open(f"{R}/{F233}"))["comparands"]["cells"]
    if not v11:
        return g, c233
    c11 = json.load(open(f"{R}/{COMPARANDS_V11}"))["cells"]
    g11 = {}
    for a in ARMS:
        sg = {p: c11[f"{a}|{p}"]["stated_gap"] for p in CONCRETE}
        fu = {p: c11[f"{a}|{p}"]["floor_used"] for p in CONCRETE}
        g11[a] = {"stated_gap": sg, "median_stated_gap": statistics.median(sg.values()),
                  "floor_used": fu, "median_floor_used": statistics.median(fu.values()),
                  "stated_gap_driving": c11[f"{a}|5"]["stated_gap"]}
        # the stated gaps of general_principle's pairs do not move under v1.1; only the floor does
        for p in CONCRETE:
            if abs(sg[p] - g[a]["stated_gap"][p]) > 1e-9:
                sys.exit(f"REFUSING: {a}|{p} stated gap moved under v1.1")
    return g11, c11


# ── LOADING: ONE STRUCTURE, FROM THE ARTEFACTS OR FROM A DATABASE ──────────────────────
# reads[arm] = {"status", "G1": {"PA": counts, "AP": counts}, "G2": {...}, "G3": {"PA":
#   {"gap", "gate", "pro", "ama"}, "AP": {...}}}; p233[arm] = {"held": {pair: bool},
#   "R": {pair: gap or None}}
def load():
    reads, p233 = {}, {}
    for a in ARMS:
        p = f"{R}/records/read__{a}.json"
        if not os.path.exists(p):
            reads[a] = {"status": "MISSING"}
        else:
            d = json.load(open(p))
            reads[a] = {"status": d["status"], "unread_reason": d.get("unread_reason"),
                        "provider_served": d.get("provider_served"),
                        "served_model": d.get("served_model"),
                        "served_model_constant": d.get("served_model_constant"),
                        "temperature": d.get("temperature"), "spent_usd": d.get("spent_usd"),
                        "calls": d.get("calls")}
            if d["status"] == "READ":
                G = d["G"]
                reads[a]["G1"] = {"PA": G["G1"]["counts"], "AP": G["G1_AP"]["counts"]}
                reads[a]["G1_less_texts"] = [
                    (o, x["text"]) for o, k in (("PA", "G1"), ("AP", "G1_AP"))
                    for x in G[k]["draws"] if x["answer"] == "less"]
                reads[a]["G1_equally_texts"] = [
                    (o, x["text"]) for o, k in (("PA", "G1"), ("AP", "G1_AP"))
                    for x in G[k]["draws"] if x["answer"] == "equally"]
                reads[a]["G2"] = {"counts": G["G2"]["counts"],
                                  "mean_p_yes": G["G2"].get("mean_p_yes"),
                                  "mean_yn_mass": G["G2"].get("mean_yn_mass")}
                reads[a]["G3"] = {o: {"gap": G[k]["gap"], "gate": G[k]["gate"],
                                      "pro": G[k]["professional"], "ama": G[k]["amateur"]}
                                  for o, k in (("PA", "G3_PA"), ("AP", "G3_AP"))}
        q = f"{R}/records/read__{a}.json"
        if os.path.exists(q):
            d = json.load(open(q))
            if d["status"] == "READ":
                rr = d["R"]
                p233[a] = {"held": {c["pair"]: c["principle_held"] for c in d["A"].values()},
                           "R": {pr: ((rr[f"p{pr}|PRO"]["mean"] - rr[f"p{pr}|PRIV"]["mean"])
                                      if rr[f"p{pr}|PRO"]["n_parsed"] >= 7
                                      and rr[f"p{pr}|PRIV"]["n_parsed"] >= 7 else None)
                                 for pr in ("1", "3", "4", "5", "7")}}
    return reads, p233


def load_from_db(con):
    """The same structures, from the general_principle and syllogism_duty cells in a database."""
    reads = {a: {"status": "MISSING"} for a in ARMS}
    for aid, arm, env in con.execute("SELECT id, arm, env FROM artefacts WHERE run='general_principle'"):
        e = json.loads(env or "{}")
        d = {"status": e.get("status")}
        if d["status"] == "READ":
            d.update({"G1": {"PA": {}, "AP": {}}, "G2": {"counts": {}}, "G3": {}})
        for role, q, ev, p, mass, nd, nv, void in con.execute(
                "SELECT role, question, ev, p_yes, answer_mass, n_draws, n_void, void "
                "FROM cells WHERE artefact_id=?", (aid,)):
            if q.startswith("G233_G1_"):
                d["G1"][role][q[len("G233_G1_"):].lower()] = round(ev * nd)
                d["G1"][role]["unparsed"] = nv
            elif q == "G233_G2":
                d["G2"]["counts"] = {"yes": round(ev * nd), "no": nd - nv - round(ev * nd),
                                     "unparsed": nv}
            elif q == "G233_G2_LP":
                d["G2"]["mean_p_yes"], d["G2"]["mean_yn_mass"] = p, mass
            elif q == "G233_G3":
                d["G3"].setdefault(role, {}).update(
                    {"gap": ev, "gate": "PASSED" if void == 0 else "FAILED"})
        reads[arm] = d
    p233 = {}
    for aid, arm, readout, env in con.execute(
            "SELECT id, arm, readout, env FROM artefacts WHERE run='syllogism_duty'"):
        if json.loads(env or "{}").get("status") != "READ":
            continue
        held, rm = {}, {}
        for fam, role, q, ev, nd, nv, void in con.execute(
                "SELECT family, role, question, ev, n_draws, n_void, void FROM cells "
                "WHERE artefact_id=? AND question IN ('PRINCIPLE233','R233_BLAME')", (aid,)):
            pr = fam.replace("duty_p", "")
            if q == "PRINCIPLE233":        # syllogism_duty.P1's rule, A0.5
                if readout == "logprob":
                    h = ev is not None and ev >= 0.90
                else:
                    h = ev is not None and round(ev * (nd - nv)) >= 9
                held[pr] = bool(h and void == 0)
            else:
                rm[(pr, role)] = (ev, void)
        p233[arm] = {"held": held, "R": {
            pr: (rm[(pr, "PRO")][0] - rm[(pr, "PRIV")][0]
                 if rm[(pr, "PRO")][1] == 0 and rm[(pr, "PRIV")][1] == 0 else None)
            for pr in ("1", "3", "4", "5", "7")}}
    return reads, p233


# ── ANALYSIS ──────────────────────────────────────────────────────────────────────────
def boot_median(xs, seed=SEED, n=N_BOOT):
    rng = random.Random(seed)
    meds = sorted(statistics.median(rng.choices(xs, k=len(xs))) for _ in range(n))
    return [meds[int(0.025 * n)], meds[int(0.975 * n) - 1]]


def cell_se(pro, ama, seed=SEED):
    """Draw standard error of one order's gap: bootstrap over that order's draws."""
    rng = random.Random(seed)
    pairs = list(zip(pro, ama))
    gs = [statistics.mean(p - a for p, a in rng.choices(pairs, k=len(pairs)))
          for _ in range(N_BOOT_CELL)]
    return statistics.pstdev(gs)


def analyse(reads, p233, counted_only=True, v11=False):
    """Per-arm rows and per-cell AG.7 / Amendment T cells over every arm; every count,
    median, bootstrap, split and verdict over the arms that count (ONE READOUT PER MODEL,
    records/RULE_ONE_READOUT_PER_MODEL.md, 2026-10-16). The pass marks stay the
    pre-registered absolute 11 arms. `counted_only=False` reproduces the banked results."""
    import report_exclusions as RX
    gcomp, c233 = comparands(v11)
    read = [a for a in ARMS if reads[a].get("status") == "READ"]
    cnt = (lambda a: RX.counted(a)) if counted_only else (lambda a: True)
    pool = [a for a in ARMS if cnt(a)]
    per = {}
    for a in ARMS:
        r = reads[a]
        row = {"status": r.get("status")}
        if r.get("status") == "READ":
            g1 = r["G1"]
            row["G1"] = g1
            row["G1_order_difference_more"] = g1["PA"].get("more", 0) - g1["AP"].get("more", 0)
            row["affirms_G1_first_order"] = g1["PA"].get("more", 0) >= AFFIRM
            row["affirms_G1_both_orders"] = all(g1[o].get("more", 0) >= AFFIRM
                                                for o in ("PA", "AP"))
            row["G2"] = r["G2"]
            row["affirms_G2"] = r["G2"]["counts"].get("yes", 0) >= AFFIRM
            if r["G2"].get("mean_p_yes") is not None:
                row["G2_held_p233_rule"] = (r["G2"]["mean_p_yes"] >= 0.90
                                            and r["G2"]["mean_yn_mass"] >= 0.70)
            g3 = r["G3"]
            ok = all(g3[o]["gate"] == "PASSED" for o in ("PA", "AP"))
            row["G3_gap_PA"], row["G3_gap_AP"] = g3["PA"]["gap"], g3["AP"]["gap"]
            row["G3_measured"] = ok
            if ok:
                row["general_gap"] = (g3["PA"]["gap"] + g3["AP"]["gap"]) / 2
                row["G3_order_difference"] = g3["PA"]["gap"] - g3["AP"]["gap"]
                row["general_gap_positive"] = row["general_gap"] > 0
                row["median_stated_gap"] = gcomp[a]["median_stated_gap"]
                row["general_minus_stated"] = row["general_gap"] - row["median_stated_gap"]
                if "pro" in g3["PA"]:
                    row["general_gap_draw_se"] = 0.5 * (
                        cell_se(g3["PA"]["pro"], g3["PA"]["ama"]) ** 2 +
                        cell_se(g3["AP"]["pro"], g3["AP"]["ama"], SEED + 1) ** 2) ** 0.5
            row["median_floor_used_orientation_only"] = gcomp[a]["median_floor_used"]
            row["stated_gap_driving"] = gcomp[a]["stated_gap_driving"]
            for k in ("G1_less_texts", "G1_equally_texts"):
                if k in r:
                    row[k] = r[k]
        row["pair_level_comparison"] = a in p233     # False: syllogism_duty left the arm unread
        if a in p233:
            row["P233_1_held"] = p233[a]["held"]
            row["P233_1_all_four"] = all(p233[a]["held"].get(p) for p in CONCRETE)
            row["P233_1_all_five"] = all(p233[a]["held"].get(p) for p in CONCRETE + ("5",))
        per[a] = row

    def count(k):
        return sum(1 for a in pool if per[a].get(k))

    meas = [a for a in pool if per[a].get("G3_measured")]
    gg = [per[a]["general_gap"] for a in meas]
    sg = [per[a]["median_stated_gap"] for a in meas]
    df = [per[a]["general_minus_stated"] for a in meas]
    has233_all = [a for a in ARMS if "P233_1_held" in per[a]]
    has233 = [a for a in has233_all if cnt(a)]
    gen_not_part = [a for a in has233 if per[a].get("affirms_G1_both_orders")
                    and not per[a]["P233_1_all_four"]]
    part_not_gen = [a for a in has233 if per[a]["P233_1_all_four"]
                    and not per[a].get("affirms_G1_both_orders")]
    gen_not_part_g2 = [a for a in has233 if per[a].get("affirms_G2")
                       and not per[a]["P233_1_all_four"]]
    gen_not_part5 = [a for a in has233 if per[a].get("affirms_G1_both_orders")
                     and not per[a]["P233_1_all_five"]]
    # AG.7: the same-session bare gap against the wording floor, non-driving cells
    ag7 = {"cells": 0, "clears": 0, "per_cell": {}}
    for a in has233_all:
        for pr in CONCRETE:
            gap = p233[a]["R"].get(pr)
            fl = c233[f"{a}|{pr}"]["floor_used"]
            if gap is None:
                continue
            if cnt(a):
                ag7["cells"] += 1
                ag7["clears"] += gap > fl
            ag7["per_cell"][f"{a}|{pr}"] = {"R_gap": gap, "floor_used": fl,
                                            "clears": gap > fl}
    # AG.7 split (asked for after the reads, 2026-10-13; not pre-registered): the cells
    # that do not clear, by sign of the bare gap; and the same over the arms whose wording
    # floor does not exceed their own median stated slack (pairs 1 3 4 7), since on an arm
    # whose floor exceeds what it states, a stated-sized gap could not clear it
    excl = [a for a in has233
            if gcomp[a]["median_floor_used"] > gcomp[a]["median_stated_gap"]]

    def split(arms):
        cs = [v for k, v in ag7["per_cell"].items() if k.split("|")[0] in arms]
        nonpos = sum(1 for v in cs if round(v["R_gap"], 9) <= 0)
        clears = sum(1 for v in cs if v["clears"])
        return {"cells": len(cs), "clears": clears, "zero_or_negative": nonpos,
                "positive_within_floor": len(cs) - clears - nonpos}
    ag7_split = {"all": split(has233),
                 "excluded_floor_above_stated": excl,
                 "restricted": split([a for a in has233 if a not in excl])}
    # Amendment T (syllogism_duty prereg, banked before this was computed): shortfall = stated
    # gap minus same-session separate gap; floor = sqrt(wording floor^2 + draw floor^2);
    # falls short if the shortfall exceeds the floor, strictly
    tcells = {}
    for a in has233_all:
        for pr in CONCRETE:
            k = f"{a}|{pr}"
            gap = p233[a]["R"].get(pr)
            if gap is None:
                tcells[k] = {"missing": "separate gap void"}
                continue
            st, wf, dfl = c233[k]["stated_gap"], c233[k]["floor_used"], DRAW_FLOOR[a]
            sf, fl = st - gap, (wf ** 2 + dfl ** 2) ** 0.5
            tcells[k] = {"stated_gap": st, "separate_gap": gap, "shortfall": sf,
                         "wording_floor": wf, "draw_floor": dfl, "floor": fl,
                         "falls_short": sf > fl}

    def tcount(arms):
        cs = [v for k, v in tcells.items() if k.split("|")[0] in arms]
        ok = [v for v in cs if "missing" not in v]
        return {"cells": len(ok), "missing": len(cs) - len(ok),
                "falls_short": sum(v["falls_short"] for v in ok)}
    shortfall = {"all": tcount(has233), "excluded_floor_above_stated": excl,
                 "restricted": tcount([a for a in has233 if a not in excl]),
                 "per_cell": tcells}
    less = [(a, o, t) for a in pool for o, t in per[a].get("G1_less_texts", [])]
    out = {
        "pooled_over": pool, "n_pool": len(pool),
        "arms_read": sum(1 for a in read if cnt(a)),
        "arms_without_pair_level_comparison": [a for a in ARMS if a not in p233], "arms_unread": {a: reads[a].get("unread_reason") or
                                                reads[a].get("status")
                                                for a in ARMS if a not in read},
        "PG1": {"n_affirm_both_orders": count("affirms_G1_both_orders"),
                "n_affirm_first_order": count("affirms_G1_first_order"),
                "denominator": len(pool),
                "pass": count("affirms_G1_both_orders") >= PASS_ARMS,
                "pass_first_order_only": count("affirms_G1_first_order") >= PASS_ARMS,
                "n_less_answers": len(less), "less_answers": less},
        "PG2": {"n_affirm": count("affirms_G2"), "denominator": len(pool),
                "pass": count("affirms_G2") >= PASS_ARMS,
                "logprob_arms_held_p233_rule": count("G2_held_p233_rule"),
                "logprob_arms_with_p": sum(1 for a in pool if "G2_held_p233_rule" in per[a])},
        "PG3": {"n_positive": count("general_gap_positive"), "n_measured": len(meas),
                "denominator": len(pool), "pass": count("general_gap_positive") >= PASS_ARMS,
                "median_general_gap": statistics.median(gg) if gg else None,
                "median_general_gap_ci": boot_median(gg) if gg else None,
                "median_stated_gap": statistics.median(sg) if sg else None,
                "median_stated_gap_ci": boot_median(sg) if sg else None,
                "median_difference": statistics.median(df) if df else None,
                "median_difference_ci": boot_median(df) if df else None},
        "AG6": {"arms_with_p233": len(has233),
                "general_not_every_pair": gen_not_part,
                "every_pair_not_general": part_not_gen,
                "general_G2_not_every_pair": gen_not_part_g2,
                "general_not_every_pair_incl_driving": gen_not_part5,
                "n_every_pair": sum(per[a]["P233_1_all_four"] for a in has233)},
        "AG7": ag7,
        "AG7_split": ag7_split,
        "T_shortfall": shortfall,
        "per_arm": per,
    }
    return out


def _f(x, nd=3):
    return None if x is None else f"{x:.{nd}f}"


def registered(out):
    """(location, printed value), shared by the result writer and the seeder."""
    L = "general_principle "
    N = out["n_pool"]
    g1, g2, g3, a6, a7 = out["PG1"], out["PG2"], out["PG3"], out["AG6"], out["AG7"]
    reg = [
        (L + "arms read", f"{out['arms_read']} of {N}"),
        (L + "PG.1 arms answering more on 9 of 10 in both orders",
         f"{g1['n_affirm_both_orders']} of {N}"),
        (L + "PG.1 result", "PASS" if g1["pass"] else "FAIL"),
        (L + "PG.1 arms answering more on 9 of 10, first order only",
         f"{g1['n_affirm_first_order']} of {N}"),
        (L + "G1 less answers, both orders", str(g1["n_less_answers"])),
        (L + "PG.2 arms answering yes on 9 of 10", f"{g2['n_affirm']} of {N}"),
        (L + "PG.2 result", "PASS" if g2["pass"] else "FAIL"),
        (L + "PG.2 log-prob arms holding under syllogism_duty.P1's rule",
         f"{g2['logprob_arms_held_p233_rule']} of {g2['logprob_arms_with_p']}"),
        (L + "PG.3 arms with a positive general gap", f"{g3['n_positive']} of {N}"),
        (L + "PG.3 result", "PASS" if g3["pass"] else "FAIL"),
        (L + "PG.3 median general gap [95% CI]",
         f"{_f(g3['median_general_gap'], 2)} [{_f((g3['median_general_gap_ci'] or [None])[0], 2)}, "
         f"{_f((g3['median_general_gap_ci'] or [None, None])[1], 2)}]"),
        (L + "PG.3 median stated slack, pairs 1 3 4 7 [95% CI]",
         f"{_f(g3['median_stated_gap'], 2)} [{_f((g3['median_stated_gap_ci'] or [None])[0], 2)}, "
         f"{_f((g3['median_stated_gap_ci'] or [None, None])[1], 2)}]"),
        (L + "PG.3 median general minus stated [95% CI]",
         f"{_f(g3['median_difference'], 2)} [{_f((g3['median_difference_ci'] or [None])[0], 2)}, "
         f"{_f((g3['median_difference_ci'] or [None, None])[1], 2)}]"),
        (L + "AG.6 arms affirming in general but not on every named pair",
         f"{len(a6['general_not_every_pair'])} of {a6['arms_with_p233']}"),
        (L + "AG.6 arms affirming on every named pair",
         f"{a6['n_every_pair']} of {a6['arms_with_p233']}"),
        (L + "AG.6 arms affirming on every named pair but not in general",
         f"{len(a6['every_pair_not_general'])} of {a6['arms_with_p233']}"),
        (L + "AG.7 non-driving cells whose same-session bare gap clears the wording floor",
         f"{a7['clears']} of {a7['cells']}"),
    ]
    for a in ARMS:
        r = out["per_arm"][a]
        reg.append((L + f"PG.3 general gap {a}",
                    _f(r.get("general_gap"), 2) if r.get("G3_measured") else "not measured"))
    return reg


def registered_ag7_split(out):
    """(location, printed value) for the AG.7 split, a supplementary artefact because
    result.json is write-once and predates the request."""
    L = "general_principle AG.7 split "
    s = out["AG7_split"]
    a, r = s["all"], s["restricted"]
    return [
        (L + "non-driving cells with a bare gap of zero or below",
         f"{a['zero_or_negative']} of {a['cells']}"),
        (L + "non-driving cells with a positive bare gap within the wording floor",
         f"{a['positive_within_floor']} of {a['cells']}"),
        (L + "arms excluded, wording floor above own median stated slack",
         ", ".join(s["excluded_floor_above_stated"]) or "none"),
        (L + "excluding those arms, cells clearing the wording floor",
         f"{r['clears']} of {r['cells']}"),
        (L + "excluding those arms, cells with a bare gap of zero or below",
         f"{r['zero_or_negative']} of {r['cells']}"),
        (L + "excluding those arms, cells with a positive bare gap within the wording floor",
         f"{r['positive_within_floor']} of {r['cells']}"),
    ]


def registered_shortfall(out):
    """(location, printed value) for syllogism_duty Amendment T, the consistency claim's figure."""
    L = "syllogism_duty Amendment T "
    t = out["T_shortfall"]
    a, r = t["all"], t["restricted"]
    return [
        (L + "non-driving cells whose shortfall exceeds sqrt(wording^2 + draw^2) floor",
         f"{a['falls_short']} of {a['cells']}"),
        (L + "arms excluded, wording floor above own median stated slack",
         ", ".join(t["excluded_floor_above_stated"]) or "none"),
        (L + "excluding those arms, cells whose shortfall exceeds the floor",
         f"{r['falls_short']} of {r['cells']}"),
    ]


def selftest():
    """Offline. The analysis on a constructed set, and artefact = database on the same."""
    import sqlite3
    reads = {}
    p233 = {}
    for i, a in enumerate(ARMS):
        more = 10 if i < 11 else 6
        reads[a] = {"status": "READ",
                    "G1": {"PA": {"more": more, "less": 10 - more, "equally": 0, "unparsed": 0},
                           "AP": {"more": 10 if i < 10 else 3, "less": 0,
                                  "equally": 0 if i < 10 else 7, "unparsed": 0}},
                    "G2": {"counts": {"yes": 10, "no": 0, "unparsed": 0}},
                    "G3": {"PA": {"gap": 2.0, "gate": "PASSED", "pro": [7] * 10,
                                  "ama": [5] * 10},
                           "AP": {"gap": 1.0 if i else -5.0, "gate": "PASSED",
                                  "pro": [6] * 10, "ama": [5] * 10}}}
        p233[a] = {"held": {p: (i % 3 != 0) for p in ("1", "3", "4", "5", "7")},
                   "R": {p: 0.0 for p in ("1", "3", "4", "5", "7")}}
    out = analyse(reads, p233, counted_only=False)   # the logic, as built over 13 arms
    assert out["PG1"]["n_affirm_both_orders"] == 10 and not out["PG1"]["pass"]
    assert out["PG1"]["n_affirm_first_order"] == 11 and out["PG1"]["pass_first_order_only"]
    assert out["PG1"]["n_less_answers"] == 0          # texts absent in the constructed set
    assert out["PG3"]["n_positive"] == 12 and out["PG3"]["pass"]
    assert out["PG3"]["median_general_gap"] == 1.5
    assert out["AG7"]["clears"] == 0 and out["AG7"]["cells"] == 52
    # every constructed bare gap is 0.0, so the split puts all 52 at zero or below; the
    # exclusion reads the real frozen comparands
    sp = out["AG7_split"]
    assert sp["all"] == {"cells": 52, "clears": 0, "zero_or_negative": 52,
                         "positive_within_floor": 0}, sp
    assert sp["excluded_floor_above_stated"] == ["deepseek", "deepseek_s", "gpt6l_s"], sp
    assert sp["restricted"]["cells"] == 40, sp
    # Amendment T on the constructed set: every R is 0.0, so shortfall = stated gap; the
    # count must equal an independent tally over the frozen comparands
    _, c233 = comparands()
    exp = sum(1 for a in ARMS for pr in CONCRETE
              if c233[f"{a}|{pr}"]["stated_gap"] >
              (c233[f"{a}|{pr}"]["floor_used"] ** 2 + DRAW_FLOOR[a] ** 2) ** 0.5)
    t = out["T_shortfall"]
    assert t["all"]["cells"] == 52 and t["all"]["falls_short"] == exp, (t["all"], exp)
    assert t["restricted"]["cells"] == 40
    assert not t["per_cell"]["llama70b|1"]["falls_short"]      # stated gap 0.0
    # held on every pair: i % 3 != 0 -> arms 1,2,4,5,7,8,10,11 hold; 0,3,6,9,12 do not
    gnp = out["AG6"]["general_not_every_pair"]
    assert gnp == [ARMS[i] for i in (0, 3, 6, 9)], gnp
    assert out["AG6"]["every_pair_not_general"] == [ARMS[10], ARMS[11]]
    print("  ok  analysis: both-order rule, first-order beside, PG.3 mean of orders, "
          "AG.6 both directions, AG.7 over 52 cells")
    # artefact path and database path agree: write the constructed set as cells
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE artefacts(id INTEGER PRIMARY KEY, run, arm, readout, env)")
    con.execute("CREATE TABLE cells(artefact_id, family, role, question, ev, p_yes, "
                "answer_mass, n_draws, n_void, void)")
    for a in ARMS:
        cur = con.execute("INSERT INTO artefacts(run, arm, readout, env) VALUES('233G',?,?,?)",
                          (a, "sampled", json.dumps({"status": "READ"})))
        for meta, cells, _ in [cells_233g(dict(reads_to_artefact(reads[a]), arm=a))]:
            for c in cells:
                con.execute("INSERT INTO cells VALUES(?,?,?,?,?,?,?,?,?,?)",
                            (cur.lastrowid, c["family"], c["role"], c["question"], c["ev"],
                             c["p_yes"], c["answer_mass"], c["n_draws"], c["n_void"],
                             c["void"]))
        cur = con.execute("INSERT INTO artefacts(run, arm, readout, env) VALUES('233',?,?,?)",
                          (a, "sampled", json.dumps({"status": "READ"})))
        for pr in ("1", "3", "4", "5", "7"):
            h = p233[a]["held"][pr]
            con.execute("INSERT INTO cells VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (cur.lastrowid, f"duty_p{pr}", "NONE", "PRINCIPLE233",
                         1.0 if h else 0.5, None, 1.0, 10, 0, 0))
            for leg in ("PRO", "PRIV"):
                con.execute("INSERT INTO cells VALUES(?,?,?,?,?,?,?,?,?,?)",
                            (cur.lastrowid, f"duty_p{pr}", leg, "R233_BLAME", 5.0, None,
                             1.0, 10, 0, 0))
    out2 = analyse(*load_from_db(con), counted_only=False)
    a = dict(registered(out) + registered_ag7_split(out) + registered_shortfall(out))
    b = dict(registered(out2) + registered_ag7_split(out2) + registered_shortfall(out2))
    assert a == b, [(k, a[k], b[k]) for k in a if a[k] != b.get(k)]
    print(f"  ok  the database path reproduces all {len(a)} registered figures")
    print("selftest 2/2")
    return 0


# the adapter's cell construction lives here so the selftest and the database build use
# one function (build_results_db.ad_api_233g calls it)
def cells_233g(d):
    base = {"frame": None, "ev_reasoning_only": None, "reasoning_configured": "off",
            "probs": None, "n_reasoning": None, "reasoning_share": None, "thin": 0,
            "row_text_sha256": None, "mass_0_3": None, "ev_sd": None, "family": "general",
            "reasoned_despite_off": None, "prompt_sha256_16": None}
    cells = []
    G = d.get("G") or {}
    for key, role in (("G1", "PA"), ("G1_AP", "AP")):
        if key not in G:
            continue
        c = G[key]
        for ans in ("more", "less", "equally"):
            v = c["counts"][ans] / c["n_asked"]
            cells.append(dict(base, role=role, question=f"G233_G1_{ans.upper()}", ev=v,
                              ev_all_draws=v, p_yes=v, ev_source=f"general_principle {key}, sampled",
                              answer_mass=1 - c["counts"]["unparsed"] / c["n_asked"],
                              answer_mass_source="parsed over asked", n_draws=c["n_asked"],
                              n_void=c["counts"]["unparsed"], void=0,
                              prompt_sha256_16=(c.get("prompt_sha256") or "")[:16] or None))
    if "G2" in G:
        c = G["G2"]
        v = c["counts"]["yes"] / c["n_asked"]
        cells.append(dict(base, role="NONE", question="G233_G2", ev=v, ev_all_draws=v,
                          p_yes=v, ev_source="general_principle G2, sampled",
                          answer_mass=1 - c["counts"]["unparsed"] / c["n_asked"],
                          answer_mass_source="parsed over asked", n_draws=c["n_asked"],
                          n_void=c["counts"]["unparsed"], void=0,
                          prompt_sha256_16=(c.get("prompt_sha256") or "")[:16] or None))
        if c.get("mean_p_yes") is not None:
            cells.append(dict(base, role="NONE", question="G233_G2_LP", ev=c["mean_p_yes"],
                              ev_all_draws=c["mean_p_yes"], p_yes=c["mean_p_yes"],
                              ev_source="general_principle G2, mean P(yes) over the top-20 log-probs",
                              answer_mass=c["mean_yn_mass"],
                              answer_mass_source="mean raw yes+no probability in the top-k",
                              n_draws=c["n_asked"], n_void=0, void=0,
                              prompt_sha256_16=(c.get("prompt_sha256") or "")[:16] or None))
    for key, role in (("G3_PA", "PA"), ("G3_AP", "AP")):
        if key not in G:
            continue
        c = G[key]
        cells.append(dict(base, role=role, question="G233_G3", ev=c["gap"],
                          ev_all_draws=c["gap"], p_yes=None,
                          ev_source=f"general_principle {key}, sampled: PROFESSIONAL minus AMATEUR",
                          answer_mass=c["n_parsed"] / c["n_asked"],
                          answer_mass_source="both fields parsed over asked",
                          n_draws=c["n_asked"], n_void=c["n_asked"] - c["n_parsed"],
                          void=0 if c["gate"] == "PASSED" else 1,
                          prompt_sha256_16=(c.get("prompt_sha256") or "")[:16] or None))
    return None, cells, []


def reads_to_artefact(r):
    """Selftest helper: a constructed `reads` entry in the reader's artefact shape."""
    g = {}
    for o, k in (("PA", "G1"), ("AP", "G1_AP")):
        g[k] = {"n_asked": 10, "counts": r["G1"][o]}
    g["G2"] = {"n_asked": 10, "counts": r["G2"]["counts"]}
    for o, k in (("PA", "G3_PA"), ("AP", "G3_AP")):
        g[k] = {"n_asked": 10, "n_parsed": 10, "gap": r["G3"][o]["gap"],
                "gate": r["G3"][o]["gate"]}
    return {"status": "READ", "G": g}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--ag7-split", action="store_true",
                    help=f"write {SPLIT} (the AG.7 split, asked for after the reads)")
    ap.add_argument("--shortfall", action="store_true",
                    help=f"write {SHORTFALL} (syllogism_duty Amendment T)")
    ap.add_argument("--v11", action="store_true",
                    help=f"write {REGISTERED_V11}: every registered figure under the v1.1 "
                         "comparands, in the recount's order")
    a = ap.parse_args()
    if a.v11:
        if os.path.exists(f"{R}/{REGISTERED_V11}"):
            sys.exit(f"write-once: {REGISTERED_V11} exists")
        out = analyse(*load(), v11=True)
        got = dict(registered(out) + registered_ag7_split(out) + registered_shortfall(out))
        rec = json.load(open(f"{R}/records/RECOUNT_general_principle.json"))
        rows = [(loc, got[loc]) for loc, _ in rec["registered"]]
        json.dump({"what": "run general_principle's registered figures under the v1.1 comparands "
                           "(completeness_fill_amendment: the wording floor pools 18 "
                           "deviations), one readout per model, in RECOUNT_RUNgeneral_principle's order",
                   "comparands": {COMPARANDS_V11: fsha(f"{R}/{COMPARANDS_V11}")},
                   "registered": rows}, open(f"{R}/{REGISTERED_V11}", "w"), indent=1)
        old = dict(rec["registered"])
        for loc, v in rows:
            if old[loc] != v:
                print(f"  moved  {loc}: {old[loc]!r} -> {v!r}")
        return 0
    if a.selftest:
        return selftest()
    if a.shortfall:
        dest = f"{R}/{SHORTFALL}"
        if os.path.exists(dest):
            sys.exit(f"write-once: {SHORTFALL} exists")
        out = analyse(*load())
        res = {"T_shortfall": out["T_shortfall"],
               "registered": registered_shortfall(out),
               "draw_floor_frozen": DRAW_FLOOR,
               "inputs": {os.path.relpath(p, R): fsha(p) for p in sorted(
                   glob.glob(f"{R}/records/read__*.json"))},
               "rule": "records/PREREG_syllogism_duty_SYLLOGISM_DUTY.md, Amendment T (banked "
                       "2026-10-13 19:40 BST, commit d0811e70, before this was computed)"}
        json.dump(res, open(dest, "w"), indent=1, ensure_ascii=False)
        for loc, v in res["registered"]:
            print(f"  {loc}: {v}")
        return 0
    if a.ag7_split:
        dest = f"{R}/{SPLIT}"
        if os.path.exists(dest):
            sys.exit(f"write-once: {SPLIT} exists")
        out = analyse(*load())
        res = {"AG7_split": out["AG7_split"], "per_cell": out["AG7"]["per_cell"],
               "registered": registered_ag7_split(out),
               "inputs": {os.path.relpath(p, R): fsha(p) for p in sorted(
                   glob.glob(f"{R}/records/read__*.json") +
                   glob.glob(f"{R}/records/read__*.json"))},
               "status": "not pre-registered: asked for on 2026-10-13, after the reads",
               "rule": "zero or below: bare gap (PRO minus PRIV, same session) <= 0 at 9 "
                       "decimals; within floor: above 0 and not above floor_used; arms "
                       "excluded where median_floor_used > median_stated_gap (pairs 1 3 "
                       "4 7), both from records/general_principle_FRAMES_v2.json"}
        json.dump(res, open(dest, "w"), indent=1, ensure_ascii=False)
        for loc, v in res["registered"]:
            print(f"  {loc}: {v}")
        return 0
    dest = f"{R}/{RESULT}"
    if os.path.exists(dest):
        sys.exit(f"write-once: {RESULT} exists")
    missing = [a for a in ARMS if not os.path.exists(f"{R}/records/read__{a}.json")]
    if missing:
        sys.exit(f"REFUSING: the analysis runs when all 13 G reads are in; missing {missing}")
    out = analyse(*load())
    out["registered"] = registered(out)
    out["inputs"] = {os.path.relpath(p, R): fsha(p) for p in sorted(
        glob.glob(f"{R}/records/read__*.json") +
        glob.glob(f"{R}/records/read__*.json"))}
    out["prereg"] = "records/PREREG_general_principle_GENERAL.md"
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    for loc, v in out["registered"]:
        print(f"  {loc}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

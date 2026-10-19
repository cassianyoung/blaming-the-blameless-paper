#!/usr/bin/env python3
"""Table A.5: deployed models across six scenarios, as positions on each model's own scale.

Panel A (the careful subject and the stated excuse, per scenario) reads
data/A5_across_scenarios_wide.csv and prints the manuscript's grid: a scenario header row,
a P0/P1 header row, and the models in two groups (without and with reasoning), each
position at two decimals. A value whose scenario fails the model's gate is printed as
read (the manuscript shades it); it enters no count.

Panel B (the excuse variants per model) reads data/A5_variants.csv: per model, the median
position of each variant over the scenarios that pass its gate, the per-scenario counts
§4.1's claims rest on as "k of n" (n: gate-passing scenarios with the readings the count
needs), and the neutral sentence's median shift with the scenarios up and down. Beneath
the models, the figures §4.1 prints, each recomputed here from the rows above (or, for a
median over readings, from data/A5_across_scenarios_long.csv) and checked against its
registered id in paper_numbers.csv; a disagreement refuses.

In both panels the sampled DeepSeek-V4.1 readout is a check row, printed and not counted.
"""
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import (ROOT, read_csv, write_table, num, f2, API_LABEL,  # noqa: E402
                      SCENARIOS, SCENARIO_LABEL)

OFF = ["gpt4o", "gpt6s_s", "gpt6l_s", "claude", "haiku_s", "qwen235b", "qwen80b",
       "qwen30b", "deepseek", "deepseek_s", "gemma27b", "llama70b", "mistral24b",
       "grok43_s", "kimi"]
ON = ["gpt6s_r", "gpt6l_r", "haiku_r", "deepseek_r_mt8192", "gemini_r", "gemini_pro",
      "grok43_r"]
GROUPS = (("Deployed, without reasoning", OFF), ("Deployed, with reasoning", ON))
# as the manuscript labels these rows
LABEL = dict(API_LABEL, qwen235b="Qwen3-235B",
             deepseek_s="DeepSeek-V4.1 (sampled) (check; not counted)")
VARIANTS = ["P0", "P1", "P1_R", "P1_neutral", "P2", "P2_other"]
VLABEL = {"P0": "P0", "P1": "P1", "P1_R": "P1-R", "P1_neutral": "P1-neutral",
          "P2": "P2", "P2_other": "P2-other"}
BAND = 0.10
B_HEADER = ["Model", "Readout", "Median position, gate-passing scenarios",
            "Gate-passing scenarios, k of n", "P1-neutral − P0"]
B_SPANS = (6, 5, 1)
B_SUB = (["", ""] + [VLABEL[v] for v in VARIANTS]
         + ["P1 ≤ 0.10", "P1-R ≤ 0.10", "P1 < P1-neutral", "P1 > P1-neutral",
            "P2-other < P2", "median (up / down)"])


def panel_a():
    by = {r["model"]: r for r in read_csv("A5_across_scenarios_wide.csv")}
    header = ["Model", "Readout"] + [SCENARIO_LABEL[s] for s in SCENARIOS]
    width = 2 + 2 * len(SCENARIOS)
    out = [["", ""] + ["P0", "P1"] * len(SCENARIOS)]
    for title, arms in GROUPS:
        out.append([title] + [""] * (width - 1))
        for arm in arms:
            r = by[arm]
            row = [LABEL[arm], r["readout"]]
            for s in SCENARIOS:
                for role in ("P0", "P1"):
                    v = num(r[f"{s}_{role}"])
                    row.append("—" if v is None else f2(v))
            out.append(row)
    notes = ["Positions on each model's own scale: 0 at its blameless case, 1 at its "
             "careless case. P0: the careful subject with nothing stated about whether the "
             "harm could have been prevented. P1: the same case with \"nothing anyone "
             "could have done\" added. A value on a scenario whose gate the model fails is "
             "printed as read and enters no count. —: not read."]
    print(write_table("table_A5_across_scenarios", header, out, notes))


def kn(k, n):
    return f"{k} of {n}"


def registered():
    """paper_numbers.csv by id: (location, printed)."""
    import csv
    with open(os.path.join(ROOT, "paper_numbers.csv"), newline="", encoding="utf-8") as fh:
        return {r["id"]: (r["location"], r["printed"])
                for r in csv.DictReader(l for l in fh if not l.startswith("#"))}


def summary(models, summ):
    """§4.1's figures, recomputed from the model rows (and, for a median over readings,
    from the per-scenario positions), each with the id it must equal."""
    c = [m for m in models if m["counted"] == "1"]
    n = len(c)
    i = lambda m, k: int(m[k])  # noqa: E731

    def every(k, nn, extra=lambda m: True):
        return sum(i(m, k) == i(m, nn) > 0 and extra(m) for m in c)

    # medians over readings need the readings: the Panel A long file, same filter
    counted = {m["model"] for m in c}
    cells = [r for r in read_csv("A5_across_scenarios_long.csv")
             if r["model"] in counted and r["gate"] in ("PASSED", "LICENSED")]

    def pos(r, v):
        return num(r[f"{v}_pos"])

    d = [abs(pos(r, "P1") - pos(r, "P1_R")) for r in cells
         if pos(r, "P1") is not None and pos(r, "P1_R") is not None]
    sh = [pos(r, "P1_neutral") - pos(r, "P0") for r in cells
          if pos(r, "P1_neutral") is not None and pos(r, "P0") is not None]
    up = sum(i(m, "neutral_up") for m in c)
    down = sum(i(m, "neutral_down") for m in c)
    same = sum(i(m, "neutral_unchanged") for m in c)
    assert up + down + same == len(sh) and (up, down) == (sum(x > 0 for x in sh),
                                                         sum(x < 0 for x in sh))
    pn = sum(i(m, "P1_neutral_pair_n") for m in c)
    above = sum(i(m, "P1_above_neutral_k") for m in c)
    p2n = sum(i(m, "P2_other_pair_n") for m in c)
    p2lo = sum(i(m, "P2_other_below_k") for m in c)
    p2hi = sum(i(m, "P2_other_above_k") for m in c)
    tied0 = summ["p2_other_tied_at_zero"]["value"]          # needs the readings' values
    t0 = sum(pos(r, "P2") == 0 and pos(r, "P2_other") == 0 for r in cells)
    assert tied0 == f"{t0} of {p2n - p2lo - p2hi}", (tied0, t0)
    p1 = every("P1_in_band_k", "P1_in_band_n")
    p1r = every("P1_R_in_band_k", "P1_R_in_band_n")
    both = sum(i(m, "P1_in_band_k") == i(m, "P1_in_band_n") > 0
               and i(m, "P1_R_in_band_k") == i(m, "P1_R_in_band_n") > 0 for m in c)
    never = every("P1_below_neutral_k", "P1_neutral_pair_n",
                  lambda m: i(m, "P1_above_neutral_k") == 0)
    p2 = every("P2_other_below_k", "P2_other_pair_n")
    rows = [
        ("Models within one noise band of blameless on every scenario, under P1",
         kn(p1, n), [("946", kn(p1, n))]),
        ("Models within one noise band of blameless on every scenario, under P1-R",
         kn(p1r, n), [("947", kn(p1r, n))]),
        ("Models within one noise band of blameless on every scenario, under both",
         kn(both, n), [("948", kn(both, n))]),
        ("Absolute difference between P1 and P1-R over readings, median", f"{st.median(d):.3f} ({len(d)} readings)",
         [("949", f"{st.median(d):.3f}")]),
        ("P1-neutral − P0 over readings",
         f"median {f2(st.median(sh))}; {up} up, {down} down, {same} unchanged, of {len(sh)}",
         [("950", f2(st.median(sh))),
          ("350", f"{up} up, {down} down, {same} unchanged, of {len(sh)}")]),
        ("Models with P1 below P1-neutral on every scenario and above it on none",
         f"{kn(never, n)} (P1 above P1-neutral in {kn(above, pn)} readings)",
         [("341", kn(never, n)), ("343", kn(above, pn))]),
        ("Models with P2-other below P2 on every scenario",
         f"{kn(p2, n)} (readings: {p2lo} lower, {p2hi} higher, {p2n - p2lo - p2hi} tied, "
         f"{t0} of them at zero; of {p2n})",
         [("951", kn(p2, n)),
          ("952", f"{p2lo} lower, {p2hi} higher, {p2n - p2lo - p2hi} tied, of {p2n}"),
          ("953", tied0)]),
    ]
    by = {m["model"]: m for m in models}
    for arm, rid in (("claude", "954"), ("qwen235b", "955"), ("grok43_s", "956")):
        rows[-1][2].append((rid, f2(num(by[arm]["P1_median"]))))
    return rows


def panel_b():
    rows = read_csv("A5_variants.csv")
    models = [r for r in rows if r["row_type"] == "model"]
    summ = {r["figure"]: r for r in rows if r["row_type"] == "summary"}
    by = {m["model"]: m for m in models}
    assert [m["model"] for m in models] == OFF + ON
    out = [B_SUB]
    notes = []
    for title, arms in GROUPS:
        out.append([title] + [""] * (len(B_SUB) - 1))
        for arm in arms:
            m = by[arm]
            row = [LABEL[arm], m["readout"]]
            for v in VARIANTS:
                x = num(m[f"{v}_median"])
                row.append("—" if x is None else f2(x))
            row += [kn(m["P1_in_band_k"], m["P1_in_band_n"]),
                    kn(m["P1_R_in_band_k"], m["P1_R_in_band_n"]),
                    kn(m["P1_below_neutral_k"], m["P1_neutral_pair_n"]),
                    kn(m["P1_above_neutral_k"], m["P1_neutral_pair_n"]),
                    kn(m["P2_other_below_k"], m["P2_other_pair_n"])]
            sm = num(m["neutral_shift_median"])
            row.append("—" if sm is None else
                       f"{f2(sm)} (+{m['neutral_up']} / -{m['neutral_down']})")
            out.append(row)
            if m["not_read"]:
                notes.append(f"{LABEL[arm]} ({dict(on='with', off='without')[m['reasoning']]} "
                             f"reasoning): {m['not_read']}")
    # the figures §4.1 prints, each against its registered id
    reg = registered()
    bad = []
    out.append(["Summary, counted models (21)"] + [""] * (len(B_SUB) - 1))
    for label, shown, checks in summary(models, summ):
        out.append([label, shown])
        for rid, val in checks:
            loc, printed = reg[rid]
            if printed != val:
                bad.append(f"id {rid} ({loc[:70]}): registered {printed!r}, computed {val!r}")
    if bad:
        sys.exit("REFUSING, a printed figure differs from its computed value:\n  "
                 + "\n  ".join(bad))
    print(write_table("table_A5B_variants", B_HEADER, out, notes))


def main():
    panel_a()
    panel_b()


if __name__ == "__main__":
    main()

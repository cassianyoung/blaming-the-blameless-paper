#!/usr/bin/env python3
"""Table B.1: base, study adapter and developer release on the worksheet, nine families.

Reads data/B1_tuning_table.csv (one row per family, plus the Chinese-corpus adapter row
for Yi flagged by is_footnote_row) and data/B1_tuning_table_summary.csv (the summary
row's statistics). Positions are on each version's own scale, bicycle cases.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import (read_csv, write_table, num, f2, signed,  # noqa: E402
                      FAMILY_LABEL)

ORDER = ["llama31", "qwen3", "mistral", "olmo2", "falcon3", "gemma9", "stablelm12b",
         "gemma27", "yi34b"]
HEADER = ["Family", "Base P0 pos.", "Base 95% CI", "Base bystander pos.",
          "Adapter P0 pos.", "Adapter Δ vs base", "Instruct P0 pos.",
          "Instruct Δ vs base", "Instruct Δ(P0 − N), digits", "Pooled band, digits",
          "Instruct Δ, pooled bands", "Instruct N shift, digits", "Instruct span ratio",
          "Spearman ρ, base vs instruct"]


def main():
    rows = read_csv("B1_tuning_table.csv")
    by = {r["family"]: r for r in rows if r["is_footnote_row"] == "0"}
    foot = [r for r in rows if r["is_footnote_row"] == "1"]
    summ = {(r["scope"], r["statistic"]): r["value"]
            for r in read_csv("B1_tuning_table_summary.csv")}
    out = []
    for fam in ORDER:
        r = by[fam]
        g = lambda k: num(r[k])  # noqa: E731
        label = FAMILY_LABEL[fam] + (" †" if fam == "yi34b" else "")
        out.append([label, f2(g("base_P0_pos")),
                    f"{f2(g('base_P0_ci_low'))}–{f2(g('base_P0_ci_high'))}",
                    f2(g("base_BYST_pos")), f2(g("adapter_P0_pos")),
                    signed(g("adapter_delta_pos")), f2(g("instruct_P0_pos")),
                    signed(g("instruct_delta_pos")),
                    signed(g("instruct_delta_P0minusN_digits")),
                    f2(g("pooled_band_digits")), signed(g("instruct_delta_bands"), 1),
                    signed(g("instruct_N_shift_digits")),
                    f2(g("instruct_span_ratio")),
                    f2(g("spearman_rho_base_vs_instruct"))])
    s = lambda k: summ[("all nine families", k)]  # noqa: E731
    lo, hi = s("rho: range").split(" to ")
    out.append(["Summary (nine families)", "", "", "", "",
                f"{f2(num(s('adapter: mean unsigned delta_pos')))} mean unsigned / "
                f"{s('adapter: lower than base')} lower, "
                f"{s('adapter: higher than base')} higher", "",
                f"{f2(num(s('instruct: mean unsigned delta_pos')))} mean unsigned / "
                f"{s('instruct: lower than base')} lower, "
                f"{s('instruct: higher than base')} higher", "", "",
                f"{s('instruct: beyond one pooled band')} of "
                f"{s('n families')} beyond one band", "", "",
                f"median {f2(num(s('rho: median')))} / ({f2(num(lo))}–{f2(num(hi))})"])
    notes = []
    for r in foot:
        notes.append(f"† Yi 1.5 34B with the Chinese-corpus adapter: position "
                     f"{f2(num(r['adapter_P0_pos']))} "
                     f"(Δ {signed(num(r['adapter_delta_pos']))}); the row above uses "
                     f"the English-corpus adapter. The instruct column for Yi is "
                     f"Yi-1.5-34B-Chat read on the worksheet.")
    e = lambda k: summ[("eight without yi34b", k)]  # noqa: E731
    notes.append(f"Mean unsigned change without Yi: adapter "
                 f"{f2(num(e('adapter: mean unsigned delta_pos')))}, instruct "
                 f"{f2(num(e('instruct: mean unsigned delta_pos')))}. Floor lowered on "
                 f"{s('floor lowered (N shift < 0), adapter')} of 9 (adapter) and "
                 f"{s('floor lowered (N shift < 0), instruct')} of 9 (instruct); scale "
                 f"widened on {s('scale widened (span ratio > 1), adapter')} of 9 "
                 f"(adapter) and {s('scale widened (span ratio > 1), instruct')} of 9 "
                 f"(instruct).")
    print(write_table("table_B1_tuning", HEADER, out, notes))


if __name__ == "__main__":
    main()

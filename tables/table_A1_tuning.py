#!/usr/bin/env python3
"""Table A.1: base, study adapter and developer release on the worksheet, nine families.

Reads data/A1_tuning_table.csv (one row per family, plus the Chinese-corpus adapter row
for Yi flagged by is_footnote_row) and data/A1_tuning_table_summary.csv (the summary
row's statistics). Positions are on each version's own scale, bicycle cases.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import (read_csv, write_table, num, f2,  # noqa: E402
                      FAMILY_LABEL)

ORDER = ["llama31", "qwen3", "mistral", "olmo2", "falcon3", "gemma9", "stablelm12b",
         "gemma27", "yi34b"]
HEADER = ["Family", "Base P0 pos.", "Base 95% CI", "Base bystander pos.",
          "Adapter P0 pos.", "Adapter Δ vs base", "Instruct P0 pos.",
          "Instruct Δ vs base", "Instruct Δ(P0 − N), digits", "Pooled band, digits",
          "Instruct Δ, pooled bands", "Instruct N shift, digits", "Instruct span ratio",
          "Spearman ρ, base vs instruct"]


def sg(v, nd=2):
    """A change as printed: '+' on a value that rounds to non-zero, '-' on any negative
    (so -0.0037 prints -0.00 and +0.0015 prints 0.00)."""
    if v is None:
        return ""
    if v < 0:
        return "-" + f2(abs(v), nd)
    s = f2(v, nd)
    return s if float(s) == 0 else "+" + s


SHADING = [["Shading (position columns: base, bystander, adapter, instruct; target 0 under "
            "reasonable care):"],
           ["", "≤ 0.10 within one noise band of blameless"],
           ["", "0.10–0.30 one to three bands"],
           ["", "> 0.30 beyond three bands (darker = larger)"]]


def main():
    rows = read_csv("A1_tuning_table.csv")
    by = {r["family"]: r for r in rows if r["is_footnote_row"] == "0"}
    foot = [r for r in rows if r["is_footnote_row"] == "1"]
    summ = {(r["scope"], r["statistic"]): r["value"]
            for r in read_csv("A1_tuning_table_summary.csv")}
    out = []
    for fam in ORDER:
        r = by[fam]
        g = lambda k: num(r[k])  # noqa: E731
        label = FAMILY_LABEL[fam] + (" †" if fam == "yi34b" else "")
        out.append([label, f2(g("base_P0_pos")),
                    f"{f2(g('base_P0_ci_low'))}–{f2(g('base_P0_ci_high'))}",
                    f2(g("base_BYST_pos")), f2(g("adapter_P0_pos")),
                    sg(g("adapter_delta_pos")), f2(g("instruct_P0_pos")),
                    sg(g("instruct_delta_pos")),
                    sg(g("instruct_delta_P0minusN_digits")),
                    f2(g("pooled_band_digits")), sg(g("instruct_delta_bands"), 1),
                    sg(g("instruct_N_shift_digits")),
                    f2(g("instruct_span_ratio")),
                    f2(g("spearman_rho_base_vs_instruct"))])
    s = lambda k: summ[("all nine families", k)]  # noqa: E731
    lo, hi = s("rho: range").split(" to ")
    # a cell of two paragraphs in the manuscript is two lines here
    out.append(["Summary (nine families)", "", "", "", "",
                f"{f2(num(s('adapter: mean unsigned delta_pos')))} mean unsigned\n"
                f"{s('adapter: lower than base')} lower, "
                f"{s('adapter: higher than base')} higher", "",
                f"{f2(num(s('instruct: mean unsigned delta_pos')))} mean unsigned\n"
                f"{s('instruct: lower than base')} lower, "
                f"{s('instruct: higher than base')} higher", "", "",
                f"{s('instruct: beyond one pooled band')} of "
                f"{s('n families')} beyond one band", "", "",
                f"median {f2(num(s('rho: median')))}\n({f2(num(lo))}–{f2(num(hi))})"])
    # the independent reading in a separate session (local_tuning_* columns)
    d = []
    for fam in ORDER:
        for v in ("base", "adapter", "instruct"):
            a, b = num(by[fam][f"{v}_P0_pos"]), num(by[fam][f"local_tuning_{v}_P0_pos"])
            if a is not None and b is not None:
                d.append((abs(a - b), fam, v))
    big = max(d)
    f = foot[0]
    out.append([f"† Yi-1.5-34B with the Chinese-corpus adapter (zh_corpus): position "
                f"{f2(num(f['adapter_P0_pos']))} (Δ {sg(num(f['adapter_delta_pos']))}); "
                f"main row uses the shared English-corpus adapter (en_corpus, seed 20260909). "
                f"Instruct column for Yi is Yi-1.5-34B-Chat.\n"
                f"Table A.1. Careful subject's position, (P0 − N) / (C − N), on the bicycle "
                f"worksheet across pretrained base, study adapter, and developer "
                f"instruction-tuned release (§3.4, §4.5). Points are ratios of means across "
                f"five exemplar orderings (with per-ordering intervals). The BYSTANDER column "
                f"reports the base model's position for an uninvolved person named in the "
                f"same case. An independent reading of the same releases in a separate "
                f"session (local_tuning) reproduces these positions: over the {len(d)} "
                f"positions both sessions read, the mean unsigned difference is "
                f"{f2(sum(x[0] for x in d) / len(d), 3)} and the largest {f2(big[0], 3)} "
                f"({FAMILY_LABEL[big[1]]} {big[2]})."])
    out += SHADING
    e = lambda k: summ[("eight without yi34b", k)]  # noqa: E731
    notes = [f"Mean unsigned change without Yi: adapter "
             f"{f2(num(e('adapter: mean unsigned delta_pos')))}, instruct "
             f"{f2(num(e('instruct: mean unsigned delta_pos')))}. Floor lowered on "
             f"{s('floor lowered (N shift < 0), adapter')} of 9 (adapter) and "
             f"{s('floor lowered (N shift < 0), instruct')} of 9 (instruct); scale "
             f"widened on {s('scale widened (span ratio > 1), adapter')} of 9 "
             f"(adapter) and {s('scale widened (span ratio > 1), instruct')} of 9 "
             f"(instruct)."]
    print(write_table("table_A1_tuning", HEADER, out, notes))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Table A.5: deployed models across six scenarios, the careful subject (P0) and the
stated excuse (P1), as positions on each model's own scale.

Reads data/A5_across_scenarios_wide.csv. Prints the manuscript's grid: a scenario header
row, a P0/P1 header row, and the models in two groups (without and with reasoning), each
position at two decimals. A value whose scenario fails the model's gate is printed as
read (the manuscript shades it); it enters no count. The sampled DeepSeek-V4.1 readout is
a check row, printed and not counted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import (read_csv, write_table, num, f2, API_LABEL,  # noqa: E402
                      SCENARIOS, SCENARIO_LABEL)

OFF = ["gpt4o", "gpt6s_s", "gpt6l_s", "claude", "haiku_s", "qwen235b", "qwen80b",
       "qwen30b", "deepseek", "deepseek_s", "gemma27b", "llama70b", "mistral24b",
       "grok43_s", "kimi"]
ON = ["gpt6s_r", "gpt6l_r", "haiku_r", "deepseek_r_mt8192", "gemini_r", "gemini_pro",
      "grok43_r"]
# as the manuscript labels these rows
LABEL = dict(API_LABEL, qwen235b="Qwen3-235B",
             deepseek_s="DeepSeek-V4.1 (sampled) (check; not counted)")


def main():
    by = {r["model"]: r for r in read_csv("A5_across_scenarios_wide.csv")}
    header = ["Model", "Readout"] + [SCENARIO_LABEL[s] for s in SCENARIOS]
    width = 2 + 2 * len(SCENARIOS)
    out = [["", ""] + ["P0", "P1"] * len(SCENARIOS)]
    for title, arms in (("Deployed, without reasoning", OFF),
                        ("Deployed, with reasoning", ON)):
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


if __name__ == "__main__":
    main()

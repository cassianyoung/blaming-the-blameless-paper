#!/usr/bin/env python3
"""Table B.5: deployed models across six scenarios, the careful subject (P0) and the
stated excuse (P1), as positions on each model's own scale.

Reads data/B5_across_scenarios_wide.csv. A value whose scenario fails the model's gate
is shown and marked '(gate fails)' in the CSV output; it enters no count.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import (read_csv, write_table, num, f2, API_LABEL,  # noqa: E402
                      SCENARIOS, SCENARIO_LABEL)

OFF = ["gpt4o", "gpt6s_s", "gpt6l_s", "claude", "haiku_s", "qwen235b", "qwen80b",
       "qwen30b", "deepseek", "deepseek_s", "gemma27b", "llama70b", "mistral24b",
       "grok43_s", "kimi"]
ON = ["gpt6s_r", "gpt6l_r", "haiku_r", "deepseek_r_mt8192", "gemini_r", "grok43_r"]


def main():
    by = {r["model"]: r for r in read_csv("B5_across_scenarios_wide.csv")}
    header = ["Model", "Readout"]
    for s in SCENARIOS:
        header += [f"{SCENARIO_LABEL[s]} P0", f"{SCENARIO_LABEL[s]} P1"]
    out = []
    for title, arms in (("Deployed, without reasoning", OFF),
                        ("Deployed, with reasoning", ON)):
        out.append([title] + [""] * (len(header) - 1))
        for arm in arms:
            r = by[arm]
            row = [API_LABEL[arm], r["readout"]]
            for s in SCENARIOS:
                tag = "" if r[f"{s}_gate"] == "PASSED" else " (gate fails)"
                for role in ("P0", "P1"):
                    v = num(r[f"{s}_{role}"])
                    row.append("—" if v is None else f2(v) + tag)
            out.append(row)
    notes = ["Positions on each model's own scale: 0 at its blameless case, 1 at its "
             "careless case. P0: the careful subject with nothing stated about whether the "
             "harm could have been prevented. P1: the same case with \"nothing anyone "
             "could have done\" added. '(gate fails)': the model fails the gate on that "
             "scenario (value shown, not used). —: not read."]
    print(write_table("table_B5_across_scenarios", header, out, notes))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Table A.2: deployed models on the bicycle set.

Reads data/A2_deployed_bicycle.csv, one row per arm, printed in the manuscript's order
(ORDER below). Blame for
the blameless (N), careless (C), deliberate (I) and target (P0) cases on the 0-9 scale,
P0's position (P0 - N)/(C - N), the answer mass and blameless mass on 0-3 that the chat
gate reads, the draws per cell and, on reasoning arms, the draws that reasoned. An arm the
data marks as not counted (counted = 0) is labelled "(check; not counted)". The deliberate
case (I) carries the ² marker where it was read from all draws (anchor_from_all_draws).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, f2  # noqa: E402

LABEL = {
    "grok43_s_bike": "grok-4.3", "qwen235b": "Qwen3-235B-A22B",
    "qwen80b": "Qwen3-Next-80B", "mistral24b": "Mistral-Small-24B",
    "deepseek": "DeepSeek-V4.1-Flash", "deepseek_s": "DeepSeek-V4.1-Flash",
    "qwen30b": "Qwen3-30B-A3B", "haiku_s": "Claude Haiku 4.5",
    "claude": "Claude Sonnet 5", "kimi": "Kimi-K3", "gemma27b": "Gemma-3-27B-IT",
    "llama70b": "Llama-3.3-70B", "gpt4o": "GPT-4o", "gpt6l_s_bike": "gpt-6-luna",
    "gpt6s_s_bike": "gpt-6-sol", "haiku_r": "Claude Haiku 4.5",
    "gpt6l_r_bike": "gpt-6-luna", "grok43_r_bike": "grok-4.3",
    "deepseek_r_bike8192_all": "DeepSeek-V4.1-Flash", "gemini_r": "Gemini 3.8 Flash",
    "gpt6s_r_bike": "gpt-6-sol", "gemini_pro": "Gemini 3.1 Pro",
}
# Manuscript footnote markers attached to a row label.
LABEL_NOTE = {"gemini_r": " ¹", "gpt6s_r_bike": " ²"}
# The manuscript's row order: reasoning off, then on, each by P0 position.
ORDER = ["grok43_s_bike", "qwen235b", "qwen80b", "mistral24b", "deepseek", "deepseek_s",
         "qwen30b", "haiku_s", "claude", "kimi", "gemma27b", "llama70b", "gpt4o",
         "gpt6l_s_bike", "gpt6s_s_bike", "haiku_r", "gpt6l_r_bike", "grok43_r_bike",
         "deepseek_r_bike8192_all", "gemini_r", "gemini_pro", "gpt6s_r_bike"]
HEADER = ["Model", "Readout", "Reasoning", "N", "C", "I", "P0", "P0 position",
          "Answer mass", "N mass 0–3", "Draws per cell", "Reasoning draws", "Gate"]


def main():
    out = []
    by = {r["model"]: r for r in read_csv("A2_deployed_bicycle.csv")}
    assert sorted(by) == sorted(ORDER), sorted(set(by) ^ set(ORDER))
    for arm in ORDER:
        r = by[arm]
        i_val = num(r["I"])
        if i_val is None:
            i_txt = "—"
        else:
            i_txt = f2(i_val) + ("²" if r["anchor_from_all_draws"] else "")
        n_draws = int(num(r["n_draws"]))
        if r["reasoning"] == "on" and r["n_reasoning"]:
            nr = int(num(r["n_reasoning"]))
            rdraws = str(nr) if nr == n_draws else f"{nr} of {n_draws}"
        else:
            rdraws = ""
        gate = "pass" if r["gate_verdict"] == "PASSED" else "fail"
        label = LABEL[arm] + ("" if r["counted"] == "1" else " (check; not counted)")
        out.append([label + LABEL_NOTE.get(arm, ""), r["readout"], r["reasoning"],
                    f2(num(r["N"])), f2(num(r["C"])), i_txt, f2(num(r["P0"])),
                    f2(num(r["P0_pos"])), f2(num(r["answer_mass"]), 3),
                    f2(num(r["N_mass_0_3"]), 3), str(n_draws), rdraws, gate])
    print(write_table("table_A2_deployed_bicycle", HEADER, out))


if __name__ == "__main__":
    main()

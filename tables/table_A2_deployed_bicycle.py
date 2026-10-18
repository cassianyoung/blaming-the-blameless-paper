#!/usr/bin/env python3
"""Table A.2: deployed models on the bicycle set.

Reads data/A2_deployed_bicycle.csv, one row per arm in the manuscript's order. Blame for
the blameless (N), careless (C), deliberate (I) and target (P0) cases on the 0-9 scale,
P0's position (P0 - N)/(C - N), the answer mass and blameless mass on 0-3 that the chat
gate reads, the draws per cell and, on reasoning arms, the draws that reasoned.
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
    "gpt6s_r_bike": "gpt-6-sol",
}
# Manuscript footnote markers attached to a row label.
LABEL_NOTE = {"gemini_r": " ³", "gpt6s_r_bike": " ⁴"}
HEADER = ["Model", "Readout", "Reasoning", "N", "C", "I", "P0", "P0 position",
          "Answer mass", "N mass 0–3", "Draws per cell", "Reasoning draws", "Gate"]


def main():
    out = []
    for r in read_csv("A2_deployed_bicycle.csv"):
        arm = r["model"]
        i_val = num(r["I"])
        if i_val is None:
            i_txt = "—¹"
        else:
            i_txt = f2(i_val) + ("⁴" if r["anchor_from_all_draws"] else "")
        n_draws = int(num(r["n_draws"]))
        if r["reasoning"] == "on" and r["n_reasoning"]:
            nr = int(num(r["n_reasoning"]))
            rdraws = str(nr) if nr == n_draws else f"{nr} of {n_draws}"
        else:
            rdraws = ""
        gate = "pass" if r["gate_verdict"] == "PASSED" else "fail"
        if r["I_clause_applied"] == "not read":
            gate += "²"
        out.append([LABEL[arm] + LABEL_NOTE.get(arm, ""), r["readout"], r["reasoning"],
                    f2(num(r["N"])), f2(num(r["C"])), i_txt, f2(num(r["P0"])),
                    f2(num(r["P0_pos"])), f2(num(r["answer_mass"]), 3),
                    f2(num(r["N_mass_0_3"]), 3), str(n_draws), rdraws, gate])
    print(write_table("table_A2_deployed_bicycle", HEADER, out))


if __name__ == "__main__":
    main()

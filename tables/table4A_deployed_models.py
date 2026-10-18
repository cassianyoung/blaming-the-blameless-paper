#!/usr/bin/env python3
"""Table 3: deployed models read through commercial APIs.

Reads data/table4A_coverage.csv (what each arm read), data/A2_deployed_bicycle.csv (the
bicycle roles each bicycle arm carries), data/A5_across_scenarios_wide.csv (the gate per
scenario) and data/A4_chef_home.csv (the readout of the comparison-only arm).

Cases read on the bicycle are the roles an arm's bicycle reading carries, less any role
taken from a superseded reading. The comparison is listed where data/A4_chef_home.csv carries a stated (side-by-side)
gap for the arm. Gate is the number of the six scenarios whose gate
verdict is PASSED. The superscript annotations in the Reasoning and Gate columns are the
manuscript's footnote markers and are kept as text.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, SCENARIOS  # noqa: E402

# (arm in the coverage file, bicycle arm, label, reasoning annotation, gate annotation)
ROWS = [
    ("gpt4o", "gpt4o", "GPT-4o", "", ""),
    ("gpt6s_s", "gpt6s_s_bike", "gpt-6-sol", "", ""),
    ("gpt6s_r", "gpt6s_r_bike", "gpt-6-sol", "²", ""),
    ("gpt6l_s", "gpt6l_s_bike", "gpt-6-luna", "", ""),
    ("gpt6l_r", "gpt6l_r_bike", "gpt-6-luna", "", ""),
    ("claude", "claude", "Claude Sonnet 5", "", ""),
    ("haiku_s", "haiku_s", "Claude Haiku 4.5", "", ""),
    ("haiku_r", "haiku_r", "Claude Haiku 4.5", " (effort: low)", ""),
    ("qwen235b", "qwen235b", "Qwen3-235B-A22B-Instruct", "", ""),
    ("qwen80b", "qwen80b", "Qwen3-Next-80B-A3B-Instruct", "", ""),
    ("qwen30b", "qwen30b", "Qwen3-30B-A3B-Instruct", "", "³"),
    ("deepseek", "deepseek", "DeepSeek-V4.1-Flash", "", "⁴"),
    ("deepseek_s", "deepseek_s", "DeepSeek-V4.1-Flash", "", ""),
    ("deepseek_r_mt8192", "deepseek_r_bike8192_all", "DeepSeek-V4.1-Flash", "", ""),
    ("gemma27b", "gemma27b", "Gemma-3-27B-IT", "", ""),
    ("gemini_r", "gemini_r", "Gemini 3.8 Flash", " (cannot be disabled)", ""),
    ("gemini_pro", None, "Gemini 3.1 Pro", " (from the draws)", ""),
    ("llama70b", "llama70b", "Llama-3.3-70B-Instruct", "", ""),
    ("mistral24b", "mistral24b", "Mistral-Small-24B", "", "⁴"),
    ("grok43_s", "grok43_s_bike", "grok-4.3", "", ""),
    ("grok43_r", "grok43_r_bike", "grok-4.3", "", ""),
    ("kimi", "kimi", "Kimi-K3", "", "⁴"),
]
WORDS = {10: "all ten", 8: "eight cases", 6: "six cases"}
READOUT_NOTE = {"qwen235b": " (top 5)"}
# The arm whose side-by-side reading supplies the comparison, where it is banked under
# another name: the DeepSeek reasoning comparison is carried by `deepseek_r`.
COMPARISON_ARM = {"deepseek_r_mt8192": "deepseek_r"}


def main():
    cov = {r["arm"]: r for r in read_csv("table4A_coverage.csv")}
    b2 = {r["model"]: r for r in read_csv("A2_deployed_bicycle.csv")}
    b5 = {r["model"]: r for r in read_csv("A5_across_scenarios_wide.csv")}
    ch = {r["model"]: r for r in read_csv("A4_chef_home.csv")}
    out = []
    for arm, bike, label, rnote, gnote in ROWS:
        c = cov[arm]
        if arm in b5:
            readout, reasoning = b5[arm]["readout"], b5[arm]["reasoning"]
        else:
            readout = ch[arm]["readout"]
            reasoning = "on" if ch[arm]["reasoning"].startswith("on") else "off"
        parts = []
        if bike:
            roles = [s.split("=")[0].strip()
                     for s in b2[bike]["role_sources"].split(";") if s.strip()]
            sup = [s.split("=")[0].strip()
                   for s in b2[bike]["roles_from_superseded_artefact"].split(";")
                   if s.strip()]
            n = len([x for x in roles if x not in sup])
            note = "¹" if sup else ""
            parts.append(f"bicycle ({WORDS.get(n, str(n) + ' cases')}{note})")
        if int(c["scenarios_of_five"]) == 5:
            parts.append("five scenarios")
        cmp_arm = COMPARISON_ARM.get(arm, arm)
        if cmp_arm in ch and ch[cmp_arm]["stated_gap_digits"] != "":
            parts.append("chef–home-cook comparison")
        cases = "; ".join(parts)
        if not bike:
            cases = "chef–home-cook comparison only"
        if arm in b5:
            npass = sum(1 for s in SCENARIOS if b5[arm][f"{s}_gate"] == "PASSED")
            gate = f"{npass} of 6{gnote}"
        else:
            gate = "not applicable"
        out.append([label, readout + READOUT_NOTE.get(arm, ""), reasoning + rnote,
                    cases, gate])
    p = write_table("table4A_deployed_models",
                    ["Model", "Readout", "Reasoning", "Cases read", "Gate"], out)
    print(p)


if __name__ == "__main__":
    main()

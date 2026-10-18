#!/usr/bin/env python3
"""Table 4A: deployed models read through commercial APIs (chat frame).

One row per model as the manuscript groups them (several arms of one model, and models
of one family read alike, share a row; ROWS below). Reads:
  data/A5_across_scenarios_wide.csv  readout, reasoning and the gate verdict per scenario
                                     for each arm (the excuse gate: scenarios PASSED of six);
  data/A2_deployed_bicycle.csv       the draws per cell of each arm's bicycle reading.
Readout (draws) lists each readout with its draws per cell; where a row's arms differ, the
values are joined with " / " in arm order (reasoning off first). Reasoning arms is "off",
"on only" or "off & on". Excuse gate is the scenarios passed of six, joined with " / "
where the row's arms differ. The superscripts are the manuscript's footnote markers, kept
as text.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, SCENARIOS  # noqa: E402

# (developer, model label, [(arm in A5, bicycle arm in A2)], reasoning marker, gate marker)
ROWS = [
    ("OpenAI", "GPT-4o", [("gpt4o", "gpt4o")], "", ""),
    ("", "gpt-6-luna, gpt-6-sol",
     [("gpt6l_s", "gpt6l_s_bike"), ("gpt6s_s", "gpt6s_s_bike"),
      ("gpt6l_r", "gpt6l_r_bike"), ("gpt6s_r", "gpt6s_r_bike")], "²", ""),
    ("Anthropic", "Claude Sonnet 5", [("claude", "claude")], "", ""),
    ("", "Claude Haiku 4.5", [("haiku_s", "haiku_s"), ("haiku_r", "haiku_r")], "", ""),
    ("Google", "Gemma-3-27B-IT", [("gemma27b", "gemma27b")], "", ""),
    ("", "Gemini 3.8 Flash", [("gemini_r", "gemini_r")], "³", ""),
    ("", "Gemini 3.1 Pro", [("gemini_pro", "gemini_pro")], "³", ""),
    ("xAI", "grok-4.3", [("grok43_s", "grok43_s_bike"), ("grok43_r", "grok43_r_bike")], "", ""),
    ("Alibaba", "Qwen3-235B, Qwen3-Next-80B",
     [("qwen235b", "qwen235b"), ("qwen80b", "qwen80b")], "", ""),
    ("", "Qwen3-30B", [("qwen30b", "qwen30b")], "", ""),
    ("DeepSeek", "DeepSeek-V4.1-Flash",
     [("deepseek", "deepseek"), ("deepseek_s", "deepseek_s"),
      ("deepseek_r_mt8192", "deepseek_r_bike8192_all")], "", ""),
    ("Meta", "Llama-3.3-70B-Instruct", [("llama70b", "llama70b")], "", ""),
    ("Mistral", "Mistral-Small-24B", [("mistral24b", "mistral24b")], "", ""),
    ("Moonshot", "Kimi-K3", [("kimi", "kimi")], "", ""),
]
HEADER = ["Developer", "Model", "Readout (draws)", "Reasoning arms", "Excuse gate¹"]


def joined(values):
    seen = []
    for v in values:
        if v not in seen:
            seen.append(v)
    return " / ".join(seen)


def main():
    b5 = {r["model"]: r for r in read_csv("A5_across_scenarios_wide.csv")}
    b2 = {r["model"]: r for r in read_csv("A2_deployed_bicycle.csv")}
    out = []
    for dev, label, arms, rmark, gmark in ROWS:
        readouts = {}
        for arm, bike in arms:
            readouts.setdefault(b5[arm]["readout"], []).append(str(int(float(b2[bike]["n_draws"]))))
        readout = " & ".join(f"{k} ({joined(v)})" for k, v in readouts.items())
        rs = {b5[arm]["reasoning"] for arm, _ in arms}
        reasoning = {frozenset({"off"}): "off", frozenset({"on"}): "on only"}.get(
            frozenset(rs), "off & on") + rmark
        gate = joined(f"{sum(b5[arm][s + '_gate'] == 'PASSED' for s in SCENARIOS)} of 6"
                      for arm, _ in arms) + gmark
        out.append([dev, label, readout, reasoning, gate])
    print(write_table("table4A_deployed_models", HEADER, out))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Table A.4: chef and home cook, the deployed models.

Reads data/A4_chef_home.csv, API rows (one per model: the stated gap from the
side-by-side scores, the separate careless gap, the share given alone, the careful pair
gap, p(careless) on the careful cases and the prawns gate). Gaps are chef minus home cook
on the 0-9 scale. Rows are grouped by reasoning, in the manuscript's order; the sampled
DeepSeek-V4.1 readout is a check row, printed and not counted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, f2  # noqa: E402


def signed(v):
    """Signed two decimals as the manuscript rounds them (Python's float formatting, so
    1.525 prints 1.52); '0.00' carries no sign."""
    s = f"{abs(v):.2f}"
    return s if float(s) == 0 else ("-" if v < 0 else "+") + s

LABEL = {
    "kimi": "Kimi-K3", "gpt4o": "GPT-4o", "claude": "Claude Sonnet 5",
    "mistral24b": "Mistral-Small-24B", "qwen80b": "Qwen3-Next-80B",
    "haiku_s": "Claude Haiku 4.5", "qwen235b": "Qwen3-235B", "qwen30b": "Qwen3-30B",
    "llama70b": "Llama-3.3-70B", "gemma27b": "Gemma-3-27B", "grok43_s": "grok-4.3",
    "deepseek": "DeepSeek-V4.1 (log-prob)", "deepseek_s": "DeepSeek-V4.1 (sampled)",
    "gpt6s_s": "gpt-6-sol", "gpt6l_s": "gpt-6-luna", "gemini_pro": "Gemini 3.1 Pro",
    "deepseek_r": "DeepSeek-V4.1", "gemini_r": "Gemini 3.8 Flash",
    "haiku_r": "Claude Haiku 4.5", "gpt6l_r": "gpt-6-luna", "grok43_r": "grok-4.3",
    "gpt6s_r": "gpt-6-sol",
}
HEADER = ["Model", "Readout", "Reasoning", "Paired-scores gap (stated)",
          "Separate careless gap (applied)", "Separate ÷ paired",
          "Careful pair gap (chef − home)", "p(careless), careful home cook",
          "p(careless), careful chef", "Gate (prawns)"]
# the manuscript's row order within each group
OFF = ["kimi", "gpt4o", "claude", "mistral24b", "qwen80b", "haiku_s", "qwen235b", "qwen30b",
       "llama70b", "gemma27b", "grok43_s", "deepseek", "deepseek_s", "gpt6s_s", "gpt6l_s"]
ON = ["gemini_pro", "deepseek_r", "gemini_r", "haiku_r", "gpt6l_r", "grok43_r", "gpt6s_r"]
LABEL["deepseek_s"] = "DeepSeek-V4.1 (sampled) (check; not counted)"


def zero_or_signed(v):
    """'—' when absent, '0.00' for an exact zero, otherwise a signed two-decimal value."""
    if v is None:
        return "—"
    return signed(v)


def main():
    by = {r["model"]: r for r in read_csv("A4_chef_home.csv") if r["source"] == "api"}
    assert set(by) == set(OFF + ON), sorted(set(by) ^ set(OFF + ON))
    out = []
    for title, arms in (("Deployed, without reasoning", OFF),
                        ("Deployed, with reasoning", ON)):
        out.append([title] + [""] * (len(HEADER) - 1))
        for arm in arms:
            r = by[arm]
            stated = num(r["stated_gap_digits"])
            share = num(r["share"])
            gate = {"PASSED": "pass", "FAILED": "fail"}.get(r["gate"], "—")
            out.append([LABEL[arm], r["readout"], "on" if r["reasoning"].startswith("on")
                        else "off",
                        "—" if stated is None else signed(stated),
                        zero_or_signed(num(r["careless_gap_digits"])),
                        "—" if share is None else f"{round(100 * share):d}%",
                        zero_or_signed(num(r["careful_gap_digits"])),
                        f2(num(r["p_careless_yes_home_P0"])) or "—",
                        f2(num(r["p_careless_yes_restaurant_P0"])) or "—", gate])
    notes = ["Gaps are chef minus home cook on the 0–9 scale. Paired-scores gap: both "
             "careless subjects scored together, mean over the two orders of mention; —: "
             "not read in both orders. Separate gap: the careless chef's and careless home "
             "cook's blame read as separate cases.",
             "Separate ÷ paired is given only where the paired-scores gap clears the "
             "model's wording floor (the floor used throughout the duty test); — otherwise.",
             "Careful pair gap: the careful chef's blame minus the careful home cook's. "
             "p(careless): the probability of 'yes' to \"Did Alaric do anything "
             "careless?\" on the careful case. —: not asked of this model."]
    print(write_table("table_A4_chef_home", HEADER, out, notes))


if __name__ == "__main__":
    main()

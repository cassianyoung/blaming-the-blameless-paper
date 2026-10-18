#!/usr/bin/env python3
"""Table A.4: chef and home cook, the deployed arms.

Reads data/A4_chef_home.csv (one row per arm: the stated gap from the side-by-side scores,
the separate careless gap, the careful pair gap, p(careless) on the careful cases and the
chat gate) and data/A4_chef_home_cmp3_probabilities.csv (the one-word comparison's
probabilities in each order of mention). Gaps are chef minus home cook on the 0-9 scale.

Rows are grouped by reasoning and ordered by the stated gap, largest first, ties by
label. '‡' marks an arm whose one-word answer follows the first-listed option in both
orders, '§' one that follows the last-listed option.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, f2, signed  # noqa: E402

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
HEADER = ["Model", "Readout", "Reasoning", "One-word answer (home first / chef first)",
          "P(chef) − P(home)", "Paired-scores gap (stated)",
          "Separate careless gap (applied)", "Separate ÷ paired",
          "Careful pair gap (chef − home)", "p(careless), careful home cook",
          "p(careless), careful chef", "Gate (prawns)"]


def zero_or_signed(v):
    """'0.00' for an exact zero, otherwise a signed two-decimal value."""
    if v is None:
        return "—"
    return "0.00" if v == 0 else signed(v)


def main():
    rows = [r for r in read_csv("A4_chef_home.csv") if r["source"] == "api"]
    probs = {}
    for p in read_csv("A4_chef_home_cmp3_probabilities.csv"):
        probs.setdefault(p["model"], []).append(num(p["p_chef"]) - num(p["p_home"]))
    groups = {"off": [], "on": []}
    for r in rows:
        groups["on" if r["reasoning"].startswith("on") else "off"].append(r)
    out = []
    for g, title in (("off", "Deployed, without reasoning"),
                     ("on", "Deployed, with reasoning")):
        out.append([title] + [""] * (len(HEADER) - 1))
        grp = sorted(groups[g], key=lambda r: (-num(r["stated_gap_digits"]),
                                               LABEL[r["model"]].lower()))
        for r in grp:
            arm = r["model"]
            mark = (" ‡" if r["cmp3_first_listed_both_orders"] == "true" else
                    " §" if r["cmp3_last_listed_both_orders"] == "true" else "")
            word = lambda s: s.split(" (")[0]  # noqa: E731
            stated = num(r["stated_gap_digits"])
            sep = num(r["careless_gap_digits"])
            share = num(r["share"])
            ratio = ("—" if sep is None else "within floor" if share is None
                     else f"{round(100 * share):d}%")
            d = probs[arm]
            gate = {"PASSED": "pass", "FAILED": "fail"}.get(r["gate"], "—")
            out.append([LABEL[arm] + mark, r["readout"], g,
                        f"{word(r['cmp3_answer_home_first'])} / "
                        f"{word(r['cmp3_answer_chef_first'])}",
                        signed(sum(d) / len(d)), signed(stated),
                        zero_or_signed(sep), ratio,
                        zero_or_signed(num(r["careful_gap_digits"])),
                        f2(num(r["p_careless_yes_home_P0"])) or "—",
                        f2(num(r["p_careless_yes_restaurant_P0"])) or "—", gate])
    notes = ["Gaps are chef minus home cook on the 0–9 scale. Paired-scores gap: both "
             "careless subjects scored together, mean over the two orders of mention. "
             "Separate gap: the careless chef's and careless home cook's blame read as "
             "separate cases.",
             "P(chef) − P(home): one-word comparison, averaged over the two orders. ‡ the "
             "answer follows the first-listed option in both orders; § the last-listed.",
             "Careful pair gap: the careful chef's blame minus the careful home cook's. "
             "p(careless): the probability of 'yes' to \"Did Alaric do anything "
             "careless?\" on the careful case.",
             "Separate ÷ paired is given only where the paired-scores gap clears the "
             "model's wording floor (the floor used throughout the duty test); "
             "'within floor' marks a paired gap inside it."]
    print(write_table("table_A4_chef_home", HEADER, out, notes))


if __name__ == "__main__":
    main()

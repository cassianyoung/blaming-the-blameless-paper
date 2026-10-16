#!/usr/bin/env python3
"""Table B.8: the judgement questions on the target case.

Reads data/B8_judgement_long.csv, target case (P0) rows only. A scenario that fails a
model's gate is excluded from every figure for that model.

Panel A, per model: the number of gate-passing scenarios; the mean probability of 'yes'
to "Could he reasonably have prevented it?"; how many scenarios answer yes (p > 0.5) out
of those with a usable reading; the mean probability of 'yes' to "Did he do anything
careless?"; and the mean blame position.

Panel B, over the non-reasoning gate-passing readings: the share with blame above 0.10,
the shares answering yes to each question, and Pearson correlations between the
questions, blame and the causal rating, each over the readings carrying both values.
"""
import math
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table, num, f2, API_LABEL  # noqa: E402

OFF = ["gpt4o", "gpt6s_s", "gpt6l_s", "claude", "haiku_s", "qwen235b", "qwen80b",
       "qwen30b", "deepseek", "deepseek_s", "gemma27b", "llama70b", "mistral24b",
       "grok43_s", "kimi"]
ON = ["gpt6s_r", "gpt6l_r", "haiku_r", "deepseek_r_mt8192", "gemini_r", "grok43_r"]


def pearson(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy)


def main():
    rows = [r for r in read_csv("B8_judgement_long.csv")
            if r["case"] == "P0" and r["gate"] == "PASSED"]
    readout = {r["model"]: r["readout"] for r in rows}
    ha = ["Model", "Readout", "Scenarios", "p(could reasonably have prevented it)",
          "Scenarios answered yes", "p(careless)", "Blame (position)"]
    out = []
    for title, arms in (("Deployed, without reasoning", OFF),
                        ("Deployed, with reasoning", ON)):
        out.append([title] + [""] * (len(ha) - 1))
        for arm in arms:
            rr = [r for r in rows if r["model"] == arm]
            pr = [num(r["p_reasonable_yes"]) for r in rr
                  if num(r["p_reasonable_yes"]) is not None]
            pc = [num(r["p_careless_yes"]) for r in rr
                  if num(r["p_careless_yes"]) is not None]
            bl = [num(r["blame_pos"]) for r in rr if num(r["blame_pos"]) is not None]
            out.append([API_LABEL[arm], readout[arm], str(len(rr)),
                        f2(st.mean(pr)) if pr else "—",
                        f"{sum(1 for p in pr if p > 0.5)} of {len(pr)}",
                        f2(st.mean(pc)) if pc else "—", f2(st.mean(bl))])
    print(write_table("table_B8A_judgement", ha, out))

    off = [r for r in rows if r["reasoning"] == "off"]

    def pairs(a, b):
        xy = [(num(r[a]), num(r[b])) for r in off
              if num(r[a]) is not None and num(r[b]) is not None]
        return [x for x, _ in xy], [y for _, y in xy]

    bl = [num(r["blame_pos"]) for r in off if num(r["blame_pos"]) is not None]
    pr = [num(r["p_reasonable_yes"]) for r in off if num(r["p_reasonable_yes"]) is not None]
    pc = [num(r["p_careless_yes"]) for r in off if num(r["p_careless_yes"]) is not None]
    hb = ["Measure", "Value", "Readings"]
    outb = []

    def share(label, vals, thr):
        k = sum(1 for v in vals if v > thr)
        outb.append([label, f"{f2(100 * k / len(vals), 1)}%", f"{k} of {len(vals)}"])

    share("Blame beyond one noise band (position > 0.10)", bl, 0.10)
    share("\"Could he reasonably have prevented it?\" answered yes (p > 0.5)", pr, 0.5)
    share("\"Was he careless?\" answered yes (p > 0.5)", pc, 0.5)
    for label, a, b in (("prevention with careless", "p_reasonable_yes",
                         "p_careless_yes"),
                        ("blame with careless", "blame_pos", "p_careless_yes"),
                        ("blame with prevention", "blame_pos", "p_reasonable_yes"),
                        ("blame with cause", "blame_pos", "cause_ev")):
        x, y = pairs(a, b)
        outb.append([f"Correlation: {label}", f2(pearson(x, y)), str(len(x))])
    print(write_table("table_B8B_judgement_summary", hb, outb))


if __name__ == "__main__":
    main()

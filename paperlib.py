"""Shared helpers for the figure and table scripts: reading data/, labels, formatting.

Every script in figures/ and tables/ reads only the CSVs in data/, located relative to
this file, so the paper's figures and tables regenerate without the results database.
"""
import csv
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
SHA = re.compile(r"\b([0-9a-f]{64})\b")


def read_csv(name):
    """Rows of data/<name> as dicts. Leading '#' lines carry the database sha."""
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(l for l in fh if not l.startswith("#")))


def db_sha(name):
    """The database sha256 named in the header of data/<name>."""
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("#"):
                break
            m = SHA.search(line)
            if m:
                return m.group(1)
    return None


def num(v):
    """A CSV cell as a float, or None when empty."""
    if v is None:
        return None
    v = str(v).strip()
    if v == "":
        return None
    return float(v)


def f2(v, nd=2):
    """Fixed decimals, half-up on the decimal string; '' for None; no sign on a zero."""
    if v is None:
        return ""
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(1).scaleb(-nd)
    s = str(Decimal(repr(float(v))).quantize(q, rounding=ROUND_HALF_UP))
    if s.startswith("-") and float(s) == 0:
        s = s[1:]
    return s


def signed(v, nd=2):
    """Signed fixed decimals: '+0.04', '-0.08', '+0.00' (sign of the unrounded value)."""
    if v is None:
        return ""
    s = f2(abs(v), nd)
    return ("-" if v < 0 else "+") + s


def write_table(stem, header, rows, notes=()):
    """Write tables/out/<stem>.csv and tables/out/<stem>.md."""
    out = os.path.join(ROOT, "tables", "out")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, stem + ".csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    with open(os.path.join(out, stem + ".md"), "w", encoding="utf-8") as fh:
        fh.write("| " + " | ".join(header) + " |\n")
        fh.write("|" + "---|" * len(header) + "\n")
        for r in rows:
            fh.write("| " + " | ".join(str(c) for c in r) + " |\n")
        for n in notes:
            fh.write("\n" + n + "\n")
    return os.path.join(out, stem + ".csv")


# Display labels for API arms, as the manuscript prints them.
API_LABEL = {
    "claude": "Claude Sonnet 5",
    "deepseek": "DeepSeek-V4.1 (log-prob)",
    "deepseek_s": "DeepSeek-V4.1 (sampled)",
    "deepseek_r_mt8192": "DeepSeek-V4.1",
    "deepseek_r_bike8192_all": "DeepSeek-V4.1",
    "deepseek_r": "DeepSeek-V4.1",
    "gemini_r": "Gemini 3.8 Flash",
    "gemini_pro": "Gemini 3.1 Pro",
    "gemma27b": "Gemma-3-27B",
    "gpt4o": "GPT-4o",
    "gpt6l_s": "gpt-6-luna", "gpt6l_s_bike": "gpt-6-luna",
    "gpt6l_r": "gpt-6-luna", "gpt6l_r_bike": "gpt-6-luna",
    "gpt6s_s": "gpt-6-sol", "gpt6s_s_bike": "gpt-6-sol",
    "gpt6s_r": "gpt-6-sol", "gpt6s_r_bike": "gpt-6-sol",
    "grok43_s": "grok-4.3", "grok43_s_bike": "grok-4.3",
    "grok43_r": "grok-4.3", "grok43_r_bike": "grok-4.3",
    "haiku_s": "Claude Haiku 4.5", "haiku_r": "Claude Haiku 4.5",
    "kimi": "Kimi-K3",
    "llama70b": "Llama-3.3-70B",
    "mistral24b": "Mistral-Small-24B",
    "qwen235b": "Qwen3-235B",
    "qwen30b": "Qwen3-30B",
    "qwen80b": "Qwen3-Next-80B",
}

# Local model families, as the manuscript prints them.
FAMILY_LABEL = {
    "llama31": "Llama 3.1 8B", "qwen3": "Qwen3 8B", "mistral": "Mistral 7B",
    "olmo2": "OLMo 2 7B", "falcon3": "Falcon3 7B", "gemma9": "Gemma 2 9B",
    "stablelm12b": "StableLM 2 12B", "gemma27": "Gemma 2 27B",
    "yi34b": "Yi 1.5 34B", "yi9b": "Yi 1.5 9B", "yi6b": "Yi 1.5 6B",
}

SCENARIOS = ["bicycle", "ladder", "prawns_home", "prawns_restaurant",
             "scaffolding", "cheque"]
SCENARIO_LABEL = {"bicycle": "Bicycle", "ladder": "Ladder",
                  "prawns_home": "Prawns, home",
                  "prawns_restaurant": "Prawns, restaurant",
                  "scaffolding": "Scaffolding", "cheque": "Cheque"}

# Position shading used throughout: within one noise band of blameless, one to three
# bands, beyond three bands.
BAND_GREEN, BAND_AMBER, BAND_RED = "#dff5e3", "#fff4d1", "#fdeaea"

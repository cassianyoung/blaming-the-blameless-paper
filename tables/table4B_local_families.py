#!/usr/bin/env python3
"""Table 4B: local families read (bf16, all six scenarios).

One row per family as the manuscript groups them (Yi-1.5-6B and 9B share a row). The
checkpoint names are labels (ROWS below); what was read comes from the data:
  data/A6_bystander_long.csv       the versions each family was read in on the worksheet
                                   frame (base, adapter, instruct; "instruct" printed as
                                   "release");
  data/A7_yi_long.csv              Yi-1.5-34B's adapter readings (more than one adapter
                                   prints "adapters");
  data/A3_frames_scenarios.csv     the developer release's chat-frame reading: scenarios
                                   passing the chat gate, of six;
  data/A3_frames_excluded.csv      a release whose chat frame cannot be scored ("not
                                   readable").
A family with no developer release prints "—" for it and "not read" for the chat frame
(Cassian, 2026-10-19, for v0_16; v0_15 printed "None" in both). The
superscripts are the manuscript's footnote markers, kept as text.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paperlib import read_csv, write_table  # noqa: E402

# (family label, [families in data], base, developer's release, marker on the adapter
# entry, marker on the chat cell)
ROWS = [
    ("Llama 3.1", ["llama31"], "Llama-3.1-8B", "Llama-3.1-8B-Instruct", "", ""),
    ("Qwen3", ["qwen3"], "Qwen3-8B-Base", "Qwen3-8B", "", "²"),
    ("Mistral", ["mistral"], "Mistral-7B-v0.3", "Mistral-7B-Instruct-v0.3", "", ""),
    ("OLMo 2", ["olmo2"], "OLMo-2-1124-7B", "OLMo-2-1124-7B-Instruct", "", ""),
    ("Falcon3", ["falcon3"], "Falcon3-7B-Base", "Falcon3-7B-Instruct", "", ""),
    ("Gemma 2 (9B)", ["gemma9"], "gemma-2-9b", "gemma-2-9b-it", "", ""),
    ("StableLM 2", ["stablelm12b"], "stablelm-2-12b", "stablelm-2-12b-chat", "", "³"),
    ("Gemma 2 (27B)", ["gemma27"], "gemma-2-27b", "gemma-2-27b-it", "", ""),
    ("Yi 1.5 (34B)", ["yi34b"], "Yi-1.5-34B", "Yi-1.5-34B-Chat", "⁴", ""),
    ("Yi 1.5 (6B, 9B)", ["yi6b", "yi9b"], "Yi-1.5-6B, Yi-1.5-9B", None, "", ""),
]
HEADER = ["Family", "Base", "Developer's tuned release", "Read on the worksheet frame",
          "Read in the chat frame¹ (Scenarios passing the gate, of 6)"]
ORDER = {"base": 0, "adapter": 1, "instruct": 2}
PRINT = {"base": "base", "adapter": "adapter", "instruct": "release"}


def main():
    read = {}
    for r in read_csv("A6_bystander_long.csv"):
        read.setdefault(r["family"], set()).add(r["version"])
    yi_adapters = {r["version"] for r in read_csv("A7_yi_long.csv")
                   if r["version"].startswith("adapter")}
    chat = {r["family"]: r["scenarios_chat_gate_pass"]
            for r in read_csv("A3_frames_scenarios.csv")}
    unreadable = {r["family"] for r in read_csv("A3_frames_excluded.csv")}
    out = []
    for label, fams, base, release, amark, cmark in ROWS:
        versions = [read[f] for f in fams]
        assert all(v == versions[0] for v in versions), (label, versions)
        v = versions[0]
        assert ("instruct" in v) == (release is not None), (label, v)
        names = []
        for x in sorted(v, key=ORDER.__getitem__):
            name = PRINT[x]
            if x == "adapter" and fams == ["yi34b"] and len(yi_adapters) > 1:
                name = "adapters"
            names.append(name + (amark if x == "adapter" else ""))
        f = fams[0]
        if release is None:
            c = "not read"
        elif f not in chat and f not in unreadable:
            sys.exit(f"REFUSING: {label} has a release but no chat reading or exclusion")
        elif f in unreadable:
            assert f not in chat, f
            c = "not readable" + cmark
        else:
            c = f"release ({chat[f]})" + cmark
        out.append([label, base, release or "—", ", ".join(names), c])
    assert {f for _, fams, *_ in ROWS for f in fams} == set(read), sorted(read)
    print(write_table("table4B_local_families", HEADER, out))


if __name__ == "__main__":
    main()

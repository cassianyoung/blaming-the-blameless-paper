#!/usr/bin/env python3
"""build_general_principle_frames.py : freeze syllogism_duty Amendment G's texts, prompts and comparands.

    python3 scripts/build_general_principle_frames.py          # writes records/general_principle_FRAMES_v2.json

Write-once. Amendment G asks run syllogism_duty's principle in general, with no task, harm or person
named (records/PREREG_general_principle_GENERAL.md):

  G1     three-way, more / less / equally (the main reading), professional first
  G1_AP  the same, amateur first, options offered "less, more, or equally" (ruling)
  G2     yes / no, the banked yes/no system message
  G3_PA  scores, professional described and asked first
  G3_AP  scores, amateur described and asked first

**THE COMPARAND IS syllogism_duty'S, NOT A NEW READ OF THE DATABASE.** PG.3 sets the general gap
beside each arm's median stated slack over the concrete pairs. Those slacks are the ones
syllogism_duty froze in `frames.json` (at database 90bb767e), so the general and the
particular are measured against one set of numbers. The file is asserted by sha and the
per-arm medians are copied here.

Every prompt's sha is the harness's construction, sha256(json.dumps(messages)), so the
reader can refuse a call whose wire prompt is not the frozen one.
"""
import hashlib, json, os, statistics, subprocess, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = f"{R}/records/general_principle_FRAMES_v2.json"
# v1 froze four prompts; the ruling of 2026-10-13 added G1's second order. v1 stays as
# banked, and v2 must carry its four prompts byte for byte (asserted below).
V1 = "records/frames.json"
V1_SHA = "04bbc181be42b8aed70f0ed5a1f1de6f1a17fd20938b6f5b67fafd4193b9839b"
F233 = "records/frames.json"
F233_SHA = "ae17c72b9a38e007be560eb9deb75079c90c2c53fe3e8387ded2945a7996df97"
F220 = "records/frames.json"
F220_SHA = "ea34a1b8d0eed2c923b28e7a9df366bc11a543843c61d6a51ca0e2794ebeaa83"
ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
        "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")
CONCRETE = ("1", "3", "4", "7")          # run syllogism_duty's pairs, driving (5) excluded

# ── THE TEXTS, VERBATIM FROM THE INSTRUCTION, §1 ────────────────────────────────────────
G1_USER = (
    "Consider two separate incidents. In one, a professional providing a paid service makes "
    "a careless mistake. In the other, unrelated incident, an amateur doing the same thing "
    "at home makes the same careless mistake, with the same result. Is the professional "
    "more to blame, less to blame, or equally to blame? Answer with one word: more, less, "
    "or equally.")
G1_SYSTEM = "Answer with one word, more, less or equally, and nothing else."
# G1's second order (ruling, 2026-10-13): the amateur's incident first, worded as G3's
# second order (AG.1), and the options offered "less, more, or equally". The question
# still asks about the professional, so "more" affirms the principle in both orders.
G1_AP_USER = (
    "Consider two separate incidents. In one, an amateur doing something at home makes a "
    "careless mistake. In the other, unrelated incident, a professional doing the same "
    "thing as a paid service makes the same careless mistake, with the same result. Is the "
    "professional less to blame, more to blame, or equally to blame? Answer with one word: "
    "less, more, or equally.")
G1_AP_SYSTEM = "Answer with one word, less, more or equally, and nothing else."
G2_USER = (
    "When two separate incidents involve the same careless mistake with the same result, "
    "one made by a professional providing a paid service and the other by an amateur doing "
    "the same thing at home, does a stricter standard apply to the professional? Answer yes "
    "or no.")
G3_SCALE = (
    "How much is each to blame, on a scale from 0 to 9, where 0 means not at all to blame "
    "and 9 means entirely to blame? Answer in exactly this form: ")
G3_PA_USER = (
    "Consider two separate incidents. In one, a professional providing a paid service makes "
    "a careless mistake. In the other, unrelated incident, an amateur doing the same thing "
    "at home makes the same careless mistake, with the same result. " + G3_SCALE +
    "PROFESSIONAL=<digit> AMATEUR=<digit>")
# The second order, amateur first (AG.1, FOR RULING). The instruction gives only its
# shape. Swapping the two descriptions word for word leaves "the same thing" in the
# first-mentioned incident with no antecedent, so the activity is introduced as
# "something" in the amateur's incident and "the same thing" moves to the professional's.
# Every other word is the first order's.
G3_AP_USER = (
    "Consider two separate incidents. In one, an amateur doing something at home makes a "
    "careless mistake. In the other, unrelated incident, a professional doing the same "
    "thing as a paid service makes the same careless mistake, with the same result. "
    + G3_SCALE + "AMATEUR=<digit> PROFESSIONAL=<digit>")
G3_SYSTEM = "Answer in exactly the form requested and nothing else."

sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
fsha = lambda p: hashlib.sha256(open(f"{R}/{p}", "rb").read()).hexdigest()
wire = lambda system, user: sha(json.dumps([{"role": "system", "content": system},
                                            {"role": "user", "content": user}]))


def main():
    if os.path.exists(DEST):
        sys.exit(f"write-once: {os.path.relpath(DEST, R)} exists")
    for p, want in ((F233, F233_SHA), (F220, F220_SHA)):
        if fsha(p) != want:
            sys.exit(f"REFUSING: {p} sha differs from the banked one")
    yn = json.load(open(f"{R}/{F220}"))["_meta"]["systems"]["yn"]
    assert yn == "Answer with one word, Yes or No, and nothing else.", yn
    # G1's question and system message name the same three words; each G3 order asks
    # for each field once
    assert G1_USER.endswith("Answer with one word: more, less, or equally.")
    assert G3_PA_USER.count("PROFESSIONAL=<digit>") == G3_AP_USER.count("AMATEUR=<digit>") == 1
    prompts = {}
    for key, system, user, form in (
            ("G1", G1_SYSTEM, G1_USER, "more|less|equally"),
            ("G1_AP", G1_AP_SYSTEM, G1_AP_USER, "less|more|equally"),
            ("G2", yn, G2_USER, "yes|no"),
            ("G3_PA", G3_SYSTEM, G3_PA_USER, "PROFESSIONAL=<digit> AMATEUR=<digit>"),
            ("G3_AP", G3_SYSTEM, G3_AP_USER, "AMATEUR=<digit> PROFESSIONAL=<digit>")):
        prompts[key] = {"system": system, "user": user, "answer_form": form,
                        "prompt_sha256": wire(system, user)}

    if fsha(V1) != V1_SHA:
        sys.exit(f"REFUSING: {V1} sha differs from the banked one")
    v1 = json.load(open(f"{R}/{V1}"))["prompts"]
    for k, p in v1.items():
        assert prompts[k] == p, f"{k} differs from v1"
    assert set(prompts) - set(v1) == {"G1_AP"}
    # G1_AP's incidents are G3_AP's, word for word
    assert G1_AP_USER.split(" Is the professional")[0] == G3_AP_USER.split(" How much")[0]
    cells = json.load(open(f"{R}/{F233}"))["comparands"]["cells"]
    comp = {}
    for a in ARMS:
        st = {p: cells[f"{a}|{p}"]["stated_gap"] for p in CONCRETE}
        fl = {p: cells[f"{a}|{p}"]["floor_used"] for p in CONCRETE}
        comp[a] = {"stated_gap": st, "median_stated_gap": statistics.median(st.values()),
                   "floor_used": fl, "median_floor_used": statistics.median(fl.values()),
                   "stated_gap_driving": cells[f"{a}|5"]["stated_gap"]}
    commit = subprocess.run(["git", "-C", R, "rev-parse", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    out = {"_meta": {"run": "233", "amendment": "G (the general principle)",
                     "prereg": "records/PREREG_general_principle_GENERAL.md",
                     "built_from_commit": commit,
                     "inputs": {F233: F233_SHA, F220: F220_SHA, V1: V1_SHA},
                     "supersedes": V1 + " (adds G1_AP; the four v1 prompts unchanged)",
                     "prompt_sha_construction": "sha256(json.dumps(messages)), as "
                                                "or_harness logs it",
                     "arms": list(ARMS), "concrete_pairs": list(CONCRETE),
                     "n_prompts": len(prompts)},
           "prompts": prompts,
           "comparands": {"source": f"{F233} comparands (database 90bb767e, view duty_fig7: "
                                    "stated_gap is the side-by-side gap, mean of the two "
                                    "orders; floor_used is the wording floor)",
                          "arms": comp}}
    json.dump(out, open(DEST, "w"), indent=1, ensure_ascii=False)
    print(f"wrote {os.path.relpath(DEST, R)}  sha256 {fsha(os.path.relpath(DEST, R))}")
    for k, p in prompts.items():
        print(f"  {k:6s} {p['prompt_sha256'][:16]}")
    print("  median stated slack over arms:",
          round(statistics.median(c["median_stated_gap"] for c in comp.values()), 3))


if __name__ == "__main__":
    main()

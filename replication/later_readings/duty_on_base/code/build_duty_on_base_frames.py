#!/usr/bin/env python3
"""build_duty_on_base_frames.py : freeze duty_on_base's material (records/PREREG_duty_on_base_DUTY_BASE.md).

    .venv/bin/python scripts/build_duty_on_base_frames.py              # writes records/frames.json
    .venv/bin/python scripts/build_duty_on_base_frames.py --check      # rebuild in memory and compare

duty_on_base reads the duty test's twelve legs (six pairs x PRO, PRIV) on the banked worksheet
(records/POD_FRAMES_216.json, its five completion orderings, unchanged) on six pretrained
base models and their six developer releases, and beside them the banked worksheet bank
(data/families_bank/moral__families223__v1.jsonl) for each arm's ruler and gate.

NOTHING IS AUTHORED HERE. The leg texts are the duty bank's, taken from the frozen v1.1 duty
frames (the strings syllogism_duty and an earlier run read), each asserted against the bank row's own sha.
The frames are the banked worksheet's, asserted by file sha. What is frozen is the list of
legs, the twelve arms, and the sha16 of every rendered duty prompt (five orderings x twelve
legs), which is the string the reader hashes and the consumption check compares.
"""
import argparse, hashlib, json, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import moral_frames as MF

OUT = "records/frames.json"
POD_FRAMES, POD_FRAMES_SHA = "records/POD_FRAMES_216.json", None      # read and recorded
F233V, F233V_SHA_FILE = "records/v11_frames.json", "records/v11_frames.sha256"
BANK223 = "data/families_bank/moral__families223__v1.jsonl"
DUTY_BANKS = ("data/duty_bank/moral__duty__v1.jsonl", "data/duty_bank/moral__duty228__v1.jsonl")
FAM_V1 = "data/families_bank/moral__families__v1.jsonl"
PAIRS = ("prawns", "1", "3", "4", "5", "7")
PAIR_NAME = {"prawns": "prawns", "1": "electrical work", "3": "gas safety", "4": "childcare",
             "5": "driving", "7": "hair dye"}
LEGS = ("PRO", "PRIV")
# (arm, Hub id, version). The base arm names are question_word's, so its banked worksheet cells
# are the reproduction comparand.
ARMS = (
    ("gemma9_base", "google/gemma-2-9b", "base"),
    ("llama31_base", "meta-llama/Llama-3.1-8B", "base"),
    ("mistral_base", "mistralai/Mistral-7B-v0.3", "base"),
    ("qwen3_base", "Qwen/Qwen3-8B-Base", "base"),
    ("olmo2_base", "allenai/OLMo-2-1124-7B", "base"),
    ("falcon3_base", "tiiuae/Falcon3-7B-Base", "base"),
    ("gemma9_rel", "google/gemma-2-9b-it", "release"),
    ("llama31_rel", "meta-llama/Llama-3.1-8B-Instruct", "release"),
    ("mistral_rel", "mistralai/Mistral-7B-Instruct-v0.3", "release"),
    ("qwen3_rel", "Qwen/Qwen3-8B", "release"),
    ("olmo2_rel", "allenai/OLMo-2-1124-7B-Instruct", "release"),
    ("falcon3_rel", "tiiuae/Falcon3-7B-Instruct", "release"),
)
FAMILY_OF = {a: a.rsplit("_", 1)[0] for a, _, _ in ARMS}


def fsha(p):
    return hashlib.sha256(open(os.path.join(R, p), "rb").read()).hexdigest()


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def bank_shas():
    """{text sha256} over every duty and families row, so a leg can be traced to a bank."""
    out = {}
    for p in DUTY_BANKS + (FAM_V1,):
        for line in open(os.path.join(R, p)):
            r = json.loads(line)
            t = r.get("text")
            if t:
                out[sha(t)] = (p, r.get("uid"))
    return out


def build():
    want = open(os.path.join(R, F233V_SHA_FILE)).read().split()[0]
    if fsha(F233V) != want:
        sys.exit(f"REFUSING: {F233V} does not hash to its pinned sha")
    f233 = json.load(open(os.path.join(R, F233V)))
    frames = [f for f in json.load(open(os.path.join(R, POD_FRAMES))) if f["delivery"] == "completion"]
    if [f["id"] for f in frames] != ["b2_completion_named"] + [f"b2_completion_named_{i}" for i in range(2, 6)]:
        sys.exit("REFUSING: the worksheet's completion frames are not the banked five orderings")
    traced = bank_shas()
    legs, manifest = {}, {}
    for p in PAIRS:
        for leg in LEGS:
            text = f233["prompts"][f"B|p{p}|{leg}"]["user"].split("\n\n")[0]
            src = traced.get(sha(text))
            if src is None:
                sys.exit(f"REFUSING: p{p} {leg}: leg text is not a row of the duty or families bank")
            if MF.agent_of(text) != "Alaric":
                sys.exit(f"REFUSING: p{p} {leg}: the worksheet would not name Alaric")
            key = f"p{p}|{leg}"
            legs[key] = {"pair": p, "pair_name": PAIR_NAME[p], "leg": leg, "text": text,
                         "text_sha256": sha(text), "bank": src[0], "uid": src[1]}
            manifest[key] = {f["id"]: sha(MF.render(f, text))[:16] for f in frames}
    # the prawns legs are the families bank's C rows; record whether local_frames's bank carries
    # the same strings (if so the worksheet pass reads them too, identically)
    b223 = {json.loads(l)["uid"]: json.loads(l)["text"] for l in open(os.path.join(R, BANK223))}
    same = {k: (legs[k]["text"] == b223.get(u)) for k, u in
            (("pprawns|PRO", "prawns_restaurant__C"), ("pprawns|PRIV", "prawns_home__C"))}
    return {
        "_meta": {"run": "245", "prereg": "records/PREREG_duty_on_base_DUTY_BASE.md",
                  "builder": "scripts/build_duty_on_base_frames.py",
                  "inputs": {POD_FRAMES: fsha(POD_FRAMES), F233V: want, BANK223: fsha(BANK223),
                             **{b: fsha(b) for b in DUTY_BANKS + (FAM_V1,)}},
                  "prompt_sha_construction": "sha256(MF.render(frame, text))[:16], as rate_pod216.read_cell hashes a completion prompt",
                  "prawns_legs_equal_families223_C_rows": same},
        "frames": [f["id"] for f in frames],
        "arms": [{"arm": a, "model": m, "version": v, "family": FAMILY_OF[a]} for a, m, v in ARMS],
        "legs": legs, "prompt_sha16": manifest,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    fr = build()
    path = a.out if os.path.isabs(a.out) else os.path.join(R, a.out)
    if a.check:
        sys.exit(0 if json.load(open(path)) == fr else "REBUILD DIFFERS from the frozen frames")
    if os.path.exists(path):
        sys.exit(f"REFUSED: {path} exists (write-once)")
    blob = json.dumps(fr, indent=1, ensure_ascii=False).encode()
    open(path, "wb").write(blob)
    print(f"{len(fr['legs'])} legs x {len(fr['frames'])} orderings, {len(fr['arms'])} arms -> "
          f"{path} sha256 {hashlib.sha256(blob).hexdigest()}")
    print("prawns legs equal local_frames's C rows:", fr["_meta"]["prawns_legs_equal_families223_C_rows"])


if __name__ == "__main__":
    main()

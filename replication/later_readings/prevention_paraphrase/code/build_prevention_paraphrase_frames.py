#!/usr/bin/env python3
"""build_prevention_paraphrase_frames.py : freeze prevention_paraphrase's five questions and every built prompt.

    python3 scripts/build_prevention_paraphrase_frames.py          # writes records/frames.json

Write-once. The two banked questions are COPIED from records/frames.json and
asserted byte-identical there (body sha against the sha that file banked), never retyped.
The three new questions are laid out exactly as the banked ones: the same system message,
the case text, a blank line, the question, "Answer yes or no.".

Every prompt that will go on the wire (5 questions x 7 cells) is built HERE and its sha
recorded, so the reader can refuse any call whose built prompt does not hash to the
frozen value. Asserting the template would prove nothing; the prompt is the observable.
"""
import hashlib, json, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = f"{R}/records/frames.json"
BIKE = "records/excuse_bank.jsonl"
BIKE_SHA = "546dc93105fadf743385be513d6bb4895dcde8a16835c8da6be9b12dda59cdcb"
FAM = "data/families_bank/moral__families__v1.jsonl"
FAM_SHA = "cb77f3cb50528b089e978f8cec1069baf293f41d803d7a5e8ad00afd136918e6"
F220 = "records/frames.json"
F220_SHA = "ea34a1b8d0eed2c923b28e7a9df366bc11a543843c61d6a51ca0e2794ebeaa83"
FAMILIES = ("ladder", "prawns_home", "prawns_restaurant", "scaffolding", "cheque")

sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
fsha = lambda p: hashlib.sha256(open(f"{R}/{p}", "rb").read()).hexdigest()


def main():
    if os.path.exists(DEST):
        sys.exit(f"write-once: {os.path.relpath(DEST, R)} exists")
    for p, want in ((BIKE, BIKE_SHA), (FAM, FAM_SHA), (F220, F220_SHA)):
        if fsha(p) != want:
            sys.exit(f"REFUSING: {p} sha {fsha(p)[:16]} != {want[:16]}")
    f220 = json.load(open(f"{R}/{F220}"))
    sys_yn = f220["systems"]["yn"] if "systems" in f220 else f220["_meta"]["systems"]["yn"]
    for k in ("reasonable", "careless"):
        if sha(f220[k]["body"]) != f220[k]["sha256"]:
            sys.exit(f"REFUSING: banked {k} body does not hash to its banked sha")
        if f220[k]["system"] != sys_yn:
            sys.exit(f"REFUSING: banked {k} system differs from the yes/no system")

    # uid -> (body, stem that must be the only question stem in its prompt, provenance)
    Q = {
     "FELL": ("Did {agent} fall short of the care a reasonable person would take? "
              "Answer yes or no.", "fall short of the care a reasonable person would take?",
              "new, prevention_paraphrase (primary paraphrase of the prevention judgement)"),
     "DIFF": ("Was there anything {agent} should have done differently? Answer yes or no.",
              "should have done differently?",
              "new, prevention_paraphrase (secondary paraphrase; known to invite hindsight)"),
     "NEGL": ("Was {agent} negligent? Answer yes or no.", "negligent?",
              "new, prevention_paraphrase (names the standard)"),
     "REASONABLE": (f220["reasonable"]["body"], "reasonably have prevented this?",
                    "banked, byte-identical to frames.json (re-read)"),
     "CARELESS": (f220["careless"]["body"], "do anything careless?",
                  "banked, byte-identical to frames.json (re-read)"),
    }

    bike = {json.loads(l)["uid"]: json.loads(l) for l in open(f"{R}/{BIKE}") if l.strip()}
    fam = {json.loads(l)["uid"]: json.loads(l) for l in open(f"{R}/{FAM}") if l.strip()}
    cells = [("bicycle", "P0", bike["P0"]), ("bicycle", "C", bike["C"])]
    cells += [(f, "P0", fam[f"{f}__P0"]) for f in FAMILIES]

    prompts = {}
    for scen, role, row in cells:
        text = row["text"]
        if not text.startswith("Alaric "):
            sys.exit(f"REFUSING: {scen}/{role} does not open on the agent Alaric")
        for q, (body, stem, _) in Q.items():
            user = f"{text}\n\n{body.format(agent='Alaric')}"
            # ISOLATION, ON THE BUILT PROMPT: its own stem, no other question's stem
            if stem not in user:
                sys.exit(f"REFUSING: {scen}/{role}/{q}: own stem absent")
            for o, (_, ostem, _) in Q.items():
                if o != q and ostem in user:
                    sys.exit(f"REFUSING: {scen}/{role}/{q}: carries {o}'s stem")
            prompts[f"{scen}|{role}|{q}"] = {
                "scenario": scen, "role": role, "question": q,
                "row_text_sha256": sha(text), "system": sys_yn, "user": user,
                # the harness's own construction, so the logged prompt_sha256_16 of every
                # call can be compared with this value directly
                "prompt_sha256": sha(json.dumps(
                    [{"role": "system", "content": sys_yn},
                     {"role": "user", "content": user}]))}

    out = {"_meta": {
              "run": "231", "built_from_commit": os.popen(
                  f"git -C {R} rev-parse HEAD").read().strip(),
              "inputs": {BIKE: BIKE_SHA, FAM: FAM_SHA, F220: F220_SHA},
              "system_yn": sys_yn,
              "layout": "case text, blank line, question; one question per call",
              "prompt_sha_construction": "sha256(json.dumps(messages)), as or_harness logs it",
              "n_prompts": len(prompts)},
           "questions": {q: {"body": b, "body_sha256": sha(b), "isolation_stem": s,
                             "provenance": p} for q, (b, s, p) in Q.items()},
           "prompts": prompts}
    json.dump(out, open(DEST, "w"), indent=1, ensure_ascii=False)
    print(f"{len(prompts)} prompts frozen -> {os.path.relpath(DEST, R)}")
    for q, v in out["questions"].items():
        print(f"  {q:10s} {v['body_sha256'][:16]}  {v['body']}")


if __name__ == "__main__":
    main()

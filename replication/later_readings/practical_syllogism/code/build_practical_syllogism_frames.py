#!/usr/bin/env python3
"""build_practical_syllogism_frames.py : freeze practical_syllogism's texts and every built prompt.

    python3 scripts/build_practical_syllogism_frames.py          # writes records/frames.json

Write-once. Two conditions:

  A  the principle, ONE prompt with no case: the banked yes/no system message and the
     instruction's sentence verbatim. Read on every arm.
  B  the optional remedy check, one prompt per (scenario, role): the case text, then the
     three questions in order, then the answer form. Read only if approved at the price
     stop. Its three question stems are the banked Reasonable and Blame bodies and the
     principle, COPIED from the frozen files, never retyped; their own answer
     instructions are dropped because the answer form replaces them.

B is built on N and C as well as P0 so that it carries its own ruler (Amendment 0, B.2);
whether those cells are read is the ruling's to decide, and freezing them costs nothing.

Every prompt's sha is the harness's construction, sha256(json.dumps(messages)), so the
reader can refuse a call whose wire prompt is not the frozen one.
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
F231 = "records/frames.json"
F231_SHA = "5a74f7867103f93749054d2c215f2bf865f782f158ae1f2b7c2a85572c864aea"
FAMILIES = ("ladder", "prawns_home", "prawns_restaurant", "scaffolding", "cheque")
B_ROLES = ("P0", "N", "C")

# The instruction's text, verbatim (practical_syllogism §1). Its sha is printed and banked.
PRINCIPLE = ("Under the standard of reasonable care, is a person at fault for a harm he "
             "could not reasonably have prevented? Answer yes or no.")
FORM = "PREVENT=<yes or no> PRINCIPLE=<yes or no> BLAME=<digit>"
B_SYSTEM = f"Answer in exactly the form {FORM}, and nothing else."

sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
fsha = lambda p: hashlib.sha256(open(f"{R}/{p}", "rb").read()).hexdigest()
wire = lambda system, user: sha(json.dumps([{"role": "system", "content": system},
                                            {"role": "user", "content": user}]))


def strip(body, tail):
    if not body.endswith(tail):
        sys.exit(f"REFUSING: banked body does not end with {tail!r}: {body!r}")
    return body[: -len(tail)].rstrip()


def main():
    if os.path.exists(DEST):
        sys.exit(f"write-once: {os.path.relpath(DEST, R)} exists")
    for p, want in ((BIKE, BIKE_SHA), (FAM, FAM_SHA), (F220, F220_SHA), (F231, F231_SHA)):
        if fsha(p) != want:
            sys.exit(f"REFUSING: {p} sha {fsha(p)[:16]} != {want[:16]}")
    f220 = json.load(open(f"{R}/{F220}"))
    f231 = json.load(open(f"{R}/{F231}"))
    sys_yn = f231["_meta"]["system_yn"]
    for k in ("reasonable", "blame"):
        if sha(f220[k]["body"]) != f220[k]["sha256"]:
            sys.exit(f"REFUSING: banked {k} body does not hash to its banked sha")

    # the three stems, each copied from a frozen source
    q_prevent = strip(f220["reasonable"]["body"], "Answer yes or no.").format(agent="Alaric")
    q_blame = strip(f220["blame"]["body"].replace("{item} ", ""),
                    "Answer with a single digit.").format(agent="Alaric")
    q_principle = strip(PRINCIPLE, "Answer yes or no.")
    if not q_blame.endswith("entirely to blame?"):
        sys.exit(f"REFUSING: blame stem not as banked: {q_blame!r}")

    prompts = {"A|principle": {
        "condition": "A", "system": sys_yn, "user": PRINCIPLE,
        "prompt_sha256": wire(sys_yn, PRINCIPLE)}}

    bike = {json.loads(l)["uid"]: json.loads(l) for l in open(f"{R}/{BIKE}") if l.strip()}
    fam = {json.loads(l)["uid"]: json.loads(l) for l in open(f"{R}/{FAM}") if l.strip()}
    for scen in ("bicycle",) + FAMILIES:
        for role in B_ROLES:
            row = bike[role] if scen == "bicycle" else fam[f"{scen}__{role}"]
            text = row["text"]
            if not text.startswith("Alaric "):
                sys.exit(f"REFUSING: {scen}/{role} does not open on the agent Alaric")
            user = (f"{text}\n\nAnswer three questions, in this order.\n"
                    f"1. {q_prevent}\n2. {q_principle}\n3. {q_blame}\n"
                    f"Answer in the form {FORM}.")
            # the observable: every stem is in the built prompt, in order, once
            at = [user.find(s) for s in (q_prevent, q_principle, q_blame)]
            if min(at) < 0 or at != sorted(at) or any(user.count(s) != 1
                                                       for s in (q_prevent, q_principle,
                                                                 q_blame)):
                sys.exit(f"REFUSING: {scen}/{role}: stems absent, repeated or out of order")
            prompts[f"B|{scen}|{role}"] = {
                "condition": "B", "scenario": scen, "role": role,
                "row_text_sha256": sha(text), "system": B_SYSTEM, "user": user,
                "prompt_sha256": wire(B_SYSTEM, user)}

    # the target-case row texts are the ones prevention_paraphrase read (same rows, same bytes)
    for scen in ("bicycle",) + FAMILIES:
        r231 = f231["prompts"][f"{scen}|P0|REASONABLE"]["row_text_sha256"]
        if prompts[f"B|{scen}|P0"]["row_text_sha256"] != r231:
            sys.exit(f"REFUSING: {scen} P0 row text differs from prevention_paraphrase's")

    out = {"_meta": {
              "run": "232", "built_from_commit": os.popen(
                  f"git -C {R} rev-parse HEAD").read().strip(),
              "inputs": {BIKE: BIKE_SHA, FAM: FAM_SHA, F220: F220_SHA, F231: F231_SHA},
              "prompt_sha_construction": "sha256(json.dumps(messages)), as or_harness logs it",
              "n_prompts": len(prompts)},
           "texts": {
              "principle": {"body": PRINCIPLE, "body_sha256": sha(PRINCIPLE),
                            "system": sys_yn,
                            "provenance": "practical_syllogism instruction §1, verbatim"},
              "B_form": {"system": B_SYSTEM, "form": FORM,
                         "stems": {"PREVENT": q_prevent, "PRINCIPLE": q_principle,
                                   "BLAME": q_blame},
                         "provenance": "PREVENT and BLAME from frames.json, "
                                       "PRINCIPLE from the instruction; each without its "
                                       "own answer instruction"}},
           "prompts": prompts}
    json.dump(out, open(DEST, "w"), indent=1, ensure_ascii=False)
    print(f"{len(prompts)} prompts frozen -> {os.path.relpath(DEST, R)}")
    print(f"  principle sha256 {sha(PRINCIPLE)}")
    print(f"  A prompt sha256  {prompts['A|principle']['prompt_sha256']}")
    print("  B example (bicycle P0):\n" + "\n".join(
        "    | " + l for l in (B_SYSTEM + "\n" + prompts["B|bicycle|P0"]["user"])
        .split("\n")))


if __name__ == "__main__":
    main()

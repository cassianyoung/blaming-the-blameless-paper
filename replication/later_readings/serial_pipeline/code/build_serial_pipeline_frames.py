#!/usr/bin/env python3
"""build_serial_pipeline_frames.py : serial_pipeline, the serial pipeline check. Frames frozen before any call.

    python3 scripts/build_serial_pipeline_frames.py            # writes records/frames.json
    python3 scripts/build_serial_pipeline_frames.py --check    # rebuilds in memory, asserts equality

Pre-registration: records/PREREG_serial_pipeline_PIPELINE.md. (The instruction names this question_word;
239 was already held by the base-arm wording experiment, so it is 240. Amendment 0, A0.1.)

Four conditions on six scenarios x (P0, N, C):
  1A  summary call      case text + the instruction's summary sentence, no system message
  1B  conclusion call   case text + the banked prevention stem + "State your conclusion in
                        one sentence.", no system message
  2A  scoring, summary forward     the DIRECT prompt with a findings block holding 1A's
  2B  scoring, conclusion forward  output verbatim, prefixed to the user turn
  D   direct verdict    deployed_scenarios's BLAME frame, rebuilt here and CHECKED AGAINST THE HASH
                        BANKED IN THE CALL LOGS for that scenario and role
  O   one answer        practical_syllogism's condition-B prompt, copied byte for byte from
                        frames.json (sha asserted)

Call 2's prompt depends on call 1's output and cannot be frozen as bytes. What is frozen is
its CONSTRUCTION: `call2_user(direct_user, findings)`, and the reader asserts per call that
removing the findings block from the built prompt returns the direct prompt exactly and the
system message is the direct one (the instruction's "check that by diff").
"""
import argparse, hashlib, json, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = f"{R}/records/frames.json"
BIKE = "records/excuse_bank.jsonl"
BIKE_SHA = "546dc93105fadf743385be513d6bb4895dcde8a16835c8da6be9b12dda59cdcb"
FAM = "data/families_bank/moral__families__v1.jsonl"
FAM_SHA = "cb77f3cb50528b089e978f8cec1069baf293f41d803d7a5e8ad00afd136918e6"
F220 = "records/frames.json"
F220_SHA = "ea34a1b8d0eed2c923b28e7a9df366bc11a543843c61d6a51ca0e2794ebeaa83"
F232 = "records/frames.json"
F232_SHA = "6fc50e644efbd2e6c56d922b6e9c76a79c5d2ae474dd468cc993ef6991d1525f"
# the banked direct-verdict call logs whose logged prompt hashes the rebuilt prompts must
# reproduce: families from deployed_scenarios (gpt4o), the bicycle from deployed_bicycle_ladder (gpt4o)
LOG_FAM = "runs/deployed_scenarios/logs/or_gpt4o.jsonl"
LOG_BIKE = "runs/deployed_bicycle_ladder/logs/l8_gpt4o.jsonl"
SCEN = ("bicycle", "ladder", "prawns_home", "prawns_restaurant", "scaffolding", "cheque")
ROLES = ("P0", "N", "C")

# The instruction's texts, verbatim.
S1A = ("Summarise the facts of this case in two or three sentences. State only what "
       "happened; do not say whether anyone was at fault.")
S1B_TAIL = "State your conclusion in one sentence."
FINDINGS_HEADER = "Extracted findings from a previous step:"

sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
fsha = lambda p: hashlib.sha256(open(f"{R}/{p}", "rb").read()).hexdigest()
mhash = lambda m: hashlib.sha256(json.dumps(m).encode()).hexdigest()


def call2_user(direct_user, findings):
    """THE construction of call 2's user turn. The reader imports this; nothing else
    builds a call-2 prompt. Findings are carried verbatim, not stripped."""
    return f"{FINDINGS_HEADER}\n{findings}\n\n{direct_user}"


def call2_diff_ok(direct_msgs, call2_msgs, findings):
    """The diff check: same system, and the user turn minus the findings block is the
    direct user turn byte for byte."""
    if len(call2_msgs) != len(direct_msgs) or call2_msgs[0] != direct_msgs[0]:
        return False
    block = f"{FINDINGS_HEADER}\n{findings}\n\n"
    u = call2_msgs[1]["content"]
    return u.startswith(block) and u[len(block):] == direct_msgs[1]["content"]


def banked_hashes():
    out = {}
    for path, keyf in ((LOG_FAM, lambda lab: lab.split("|")[1] if lab.endswith("|BLAME")
                        else None),
                       (LOG_BIKE, lambda lab: ("bicycle__" + lab.split("|")[1])
                        if lab.endswith("|blame") else None)):
        for l in open(f"{R}/{path}"):
            r = json.loads(l)
            k = keyf(r["label"])
            if k:
                out.setdefault(k, set()).add(r["prompt_sha256_16"])
    return out


def build():
    for p, want in ((BIKE, BIKE_SHA), (FAM, FAM_SHA), (F220, F220_SHA), (F232, F232_SHA)):
        if fsha(p) != want:
            sys.exit(f"REFUSING: {p} sha {fsha(p)[:16]} != {want[:16]}")
    f220 = json.load(open(f"{R}/{F220}"))
    f232 = json.load(open(f"{R}/{F232}"))
    for k in ("reasonable", "blame"):
        if sha(f220[k]["body"]) != f220[k]["sha256"]:
            sys.exit(f"REFUSING: banked {k} body does not hash to its banked sha")
    tail = " Answer yes or no."
    if not f220["reasonable"]["body"].endswith(tail):
        sys.exit("REFUSING: banked prevention body has changed shape")
    prevent_stem = f220["reasonable"]["body"][: -len(tail)]         # "Could {agent} ...?"
    bh = banked_hashes()
    bike = {json.loads(l)["uid"]: json.loads(l) for l in open(f"{R}/{BIKE}") if l.strip()}
    fam = {json.loads(l)["uid"]: json.loads(l) for l in open(f"{R}/{FAM}") if l.strip()}

    cells = {}
    for scen in SCEN:
        for role in ROLES:
            row = bike[role] if scen == "bicycle" else fam[f"{scen}__{role}"]
            text, agent = row["text"], "Alaric"
            if not text.startswith(agent + " "):
                sys.exit(f"REFUSING: {scen}/{role} does not open on {agent}")
            m1a = [{"role": "user", "content": f"{text}\n\n{S1A}"}]
            m1b = [{"role": "user", "content":
                    f"{text}\n\n{prevent_stem.format(agent=agent)} {S1B_TAIL}"}]
            md = [{"role": "system", "content": f220["blame"]["system"]},
                  {"role": "user", "content": f220["blame"]["body"].format(item=text,
                                                                           agent=agent)}]
            # THE DIRECT PROMPT IS THE ONE THAT WAS SENT: its hash is in the banked log
            want = bh.get(f"{scen}__{role}")
            if not want or mhash(md)[:16] not in want or len(want) != 1:
                sys.exit(f"REFUSING: {scen}/{role} direct prompt {mhash(md)[:16]} is not "
                         f"the banked wire prompt {sorted(want or [])}")
            p232 = f232["prompts"][f"B|{scen}|{role}"]
            mo = [{"role": "system", "content": p232["system"]},
                  {"role": "user", "content": p232["user"]}]
            if mhash(mo) != p232["prompt_sha256"] or p232["row_text_sha256"] != sha(text):
                sys.exit(f"REFUSING: {scen}/{role} one-answer prompt is not practical_syllogism's")
            # the construction is exercised on a probe string and diff-checked here too
            probe = "PROBE"
            m2 = [md[0], {"role": "user", "content": call2_user(md[1]["content"], probe)}]
            if not call2_diff_ok(md, m2, probe):
                sys.exit("REFUSING: call-2 construction fails its own diff check")
            # isolation of the scoring question: the blame stem once, no other question
            for k, m in (("1A", m1a), ("1B", m1b)):
                if "to blame" in m[-1]["content"]:
                    sys.exit(f"REFUSING: {scen}/{role} {k} carries the blame question")
            cells[f"{scen}|{role}"] = {
                "scenario": scen, "role": role, "row_text": text,
                "row_text_sha256": sha(text),
                "1A": {"messages": m1a, "prompt_sha256": mhash(m1a)},
                "1B": {"messages": m1b, "prompt_sha256": mhash(m1b)},
                "D": {"messages": md, "prompt_sha256": mhash(md),
                      "banked_wire_sha16": sorted(want)[0],
                      "banked_log": LOG_BIKE if scen == "bicycle" else LOG_FAM},
                "O": {"messages": mo, "prompt_sha256": mhash(mo),
                      "source": f"{F232} B|{scen}|{role}"}}
    return {
        "_meta": {
            "run": "240", "instruction_named_it": "239",
            "inputs": {BIKE: BIKE_SHA, FAM: FAM_SHA, F220: F220_SHA, F232: F232_SHA,
                       LOG_FAM: fsha(LOG_FAM), LOG_BIKE: fsha(LOG_BIKE)},
            "prompt_sha_construction": "sha256(json.dumps(messages)), as or_harness logs it",
            "call2_construction": "user = FINDINGS_HEADER + '\\n' + call-1 output verbatim + "
                                  "'\\n\\n' + the direct user turn; system = the direct "
                                  "system. scripts/build_serial_pipeline_frames.py:call2_user",
            "n_cells": len(cells)},
        "texts": {"S1A": S1A, "S1A_sha256": sha(S1A),
                  "S1B": f"{prevent_stem} {S1B_TAIL}", "S1B_sha256": sha(
                      f"{prevent_stem} {S1B_TAIL}"),
                  "FINDINGS_HEADER": FINDINGS_HEADER,
                  "direct_system": f220["blame"]["system"],
                  "direct_body": f220["blame"]["body"]},
        "cells": cells}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = build()
    blob = json.dumps(out, indent=1, ensure_ascii=False)
    if a.check:
        got = open(DEST).read()
        if got != blob:
            sys.exit("CHECK FAILED: the frozen frames differ from a rebuild")
        print(f"check OK: {DEST} rebuilds identical, sha256 {sha(got)}")
        return 0
    if os.path.exists(DEST):
        sys.exit(f"write-once: {os.path.relpath(DEST, R)} exists")
    open(DEST, "w").write(blob)
    print(f"{len(out['cells'])} cells frozen -> {os.path.relpath(DEST, R)}  sha256 {sha(blob)}")
    c = out["cells"]["bicycle|P0"]
    for k in ("1A", "1B", "D", "O"):
        print(f"--- {k}  {c[k]['prompt_sha256'][:16]}")
        for m in c[k]["messages"]:
            print(f"   [{m['role']}] " + m["content"].replace("\n", "\n            "))
    print("--- 2B example, findings 'Alaric could not reasonably have prevented this.'")
    print("   " + call2_user(c["D"]["messages"][1]["content"],
                            "Alaric could not reasonably have prevented this.")
          .replace("\n", "\n   "))
    return 0


if __name__ == "__main__":
    sys.exit(main())

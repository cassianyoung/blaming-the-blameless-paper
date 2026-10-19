#!/usr/bin/env python3
"""build_syllogism_duty_frames.py : freeze run syllogism_duty's texts, every built prompt and every comparand.

    python3 scripts/build_syllogism_duty_frames.py          # writes records/frames.json

Write-once. Two conditions, on the five duty pairs that carry neutral sentences
(1 electrical, 3 gas, 4 childcare, 5 driving, 7 hair dye):

  A  the principle with no case, one prompt per pair: the banked yes/no system message and
     the instruction's sentence with the pair's two role phrases (Amendment 0, A0.1).
  B  the syllogism assembled by the model, one prompt per pair and leg: the banked separate
     case, a blank line, then the instruction's three questions and answer form verbatim.

**THE COMPARANDS ARE FROZEN HERE, NOT READ AT ANALYSIS TIME.** Each arm's banked stated
gap, bare separate gap, wording floor and convention-stated gap come from `duty_fig7` and
`duty_floor_used` in the database at the sha named below, and are copied into this file.
A later rebuild cannot then move a comparand under a result already read.

Every prompt's sha is the harness's construction, sha256(json.dumps(messages)), so the
reader can refuse a call whose wire prompt is not the frozen one.
"""
import hashlib, json, os, sqlite3, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = f"{R}/records/frames.json"
BANKS = {
    "data/duty_bank/moral__duty__v1.jsonl":
        "b0ca3175775f9c1f13d87a7dbf25f82f02be627aabf349e5ddadbd4c44baa9d6",
    "data/duty_bank/moral__duty228__v1.jsonl":
        "1ac42d76dcf2ab18812cf721954c356d466241ad080017186c5d4f100e33c21b",
}
F220 = "records/frames.json"
F220_SHA = "ea34a1b8d0eed2c923b28e7a9df366bc11a543843c61d6a51ca0e2794ebeaa83"
DB = "results/results.sqlite"
DB_SHA = "90bb767edb5152887bb38d7c797d99c9dd846edd15b67d8eab19614ac862b3b9"
PAIRS = ("1", "3", "4", "5", "7")
LEGS = ("PRO", "PRIV")
ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
        "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")

# ── A: THE INSTRUCTION'S SENTENCE, AND THE ROLE PHRASES (Amendment 0, A0.1) ────────────
# The instruction's template is "is a [private role] doing this at home held to a less
# strict standard than a [professional role] who does it for payment?", and its own
# example private role is "a person fitting a plug at home". Filling the template
# literally with that example doubles "at home", and on driving "at home" is false. So
# (default, FOR RULING) the private phrase replaces "[private role] doing this at home"
# whole: it names the person, the activity and, where the case has one, the home; every
# word outside the brackets is kept. Each phrase is the pair's banked case in plain words.
A_HEAD = "Under the standard of care, is "
A_MID = " held to a less strict standard than "
A_TAIL = " who does it for payment? Answer yes or no."
ROLES = {
    "1": ("a person fitting a plug to a lamp at home", "a qualified electrician"),
    "3": ("a person lending his own flat to a friend", "a professional landlord"),
    "4": ("a grandparent looking after a grandchild at home", "a registered childminder"),
    "5": ("a person giving a friend a lift", "a taxi driver"),
    "7": ("a person dyeing a friend's hair at home", "a hairdresser"),
}
# ── B: VERBATIM FROM THE INSTRUCTION, §1.B ──────────────────────────────────────────────
B_QUESTIONS = (
    "Answer three questions in order. First: was Alaric acting as a professional, paid to "
    "do this, or as a private person? Second: under the standard of care, is a private "
    "person doing this held to a less strict standard than a professional who does it for "
    "payment? Third: how much is Alaric to blame, on a scale from 0 to 9, where 0 means not "
    "at all to blame and 9 means entirely to blame? Answer in exactly this form: "
    "ROLE=<professional or private> PRINCIPLE=<yes or no> BLAME=<digit>")
B_FORM = "ROLE=<professional or private> PRINCIPLE=<yes or no> BLAME=<digit>"
B_SYSTEM = f"Answer in exactly the form {B_FORM}, and nothing else."   # A0.2, FOR RULING
EXPECTED_ROLE = {"PRO": "professional", "PRIV": "private"}

sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
fsha = lambda p: hashlib.sha256(open(f"{R}/{p}", "rb").read()).hexdigest()
wire = lambda system, user: sha(json.dumps([{"role": "system", "content": system},
                                            {"role": "user", "content": user}]))


def comparands():
    """Per arm and pair, from the database at DB_SHA: the banked figures syllogism_duty is
    measured against. Values copied, with the view each came from."""
    con = sqlite3.connect(f"file:{R}/{DB}?mode=ro", uri=True)
    q = ("SELECT arm, pair_id, stated_gap, separate_gap, sep_pro, sep_priv, floor_used, "
         "floor_used_source, share, stated_condition_gap, convention_stated, status, "
         "missing_reason FROM duty_fig7 WHERE arm = ? AND pair_id = ?")
    out = {}
    for arm in ARMS:
        for p in PAIRS:
            r = con.execute(q, (arm, p)).fetchone()
            if r is None:
                sys.exit(f"REFUSING: duty_fig7 has no row for {arm} pair {p}")
            k = ("arm", "pair_id", "stated_gap", "separate_gap", "sep_pro", "sep_priv",
                 "floor_used", "floor_used_source", "share", "stated_condition_gap",
                 "convention_stated", "status", "missing_reason")
            d = dict(zip(k, r))
            if d["stated_gap"] is None or d["separate_gap"] is None or d["floor_used"] is None:
                sys.exit(f"REFUSING: {arm} pair {p} lacks a banked stated gap, separate "
                         f"gap or floor: {d}")
            out[f"{arm}|{p}"] = d
    return out


def main():
    if os.path.exists(DEST):
        sys.exit(f"write-once: {os.path.relpath(DEST, R)} exists")
    for p, want in list(BANKS.items()) + [(F220, F220_SHA), (DB, DB_SHA)]:
        if fsha(p) != want:
            sys.exit(f"REFUSING: {p} sha {fsha(p)[:16]} != {want[:16]}")
    f220 = json.load(open(f"{R}/{F220}"))
    sys_yn = f220["_meta"]["systems"]["yn"]
    # B's third question must be the banked blame stem, word for word
    stem = f220["blame"]["body"].replace("{item} ", "").replace(
        " Answer with a single digit.", "").format(agent="Alaric")
    if ("Third: " + stem[0].lower() + stem[1:]) not in B_QUESTIONS:
        sys.exit(f"REFUSING: B's third question is not the banked blame stem: {stem!r}")

    rows = {}
    for p in BANKS:
        for l in open(f"{R}/{p}"):
            r = json.loads(l)
            if r.get("kind") == "separate":
                rows[r["uid"]] = r

    prompts = {}
    for pr in PAIRS:
        priv, pro = ROLES[pr]
        body = f"{A_HEAD}{priv}{A_MID}{pro}{A_TAIL}"
        prompts[f"A|p{pr}"] = {"condition": "A", "pair": pr, "system": sys_yn,
                               "user": body, "body_sha256": sha(body),
                               "role_private": priv, "role_professional": pro,
                               "prompt_sha256": wire(sys_yn, body)}
        for leg in LEGS:
            row = rows[f"DUTY{pr}_{leg}"]
            if sha(row["text"]) != row["text_sha256"]:
                sys.exit(f"REFUSING: DUTY{pr}_{leg} text does not hash to its banked sha")
            user = f"{row['text']}\n\n{B_QUESTIONS}"
            if user.count(B_QUESTIONS) != 1 or not user.startswith(row["text"]):
                sys.exit(f"REFUSING: B|p{pr}|{leg} is not case then questions")
            prompts[f"B|p{pr}|{leg}"] = {
                "condition": "B", "pair": pr, "leg": leg, "uid": row["uid"],
                "row_text_sha256": row["text_sha256"], "expected_role": EXPECTED_ROLE[leg],
                "system": B_SYSTEM, "user": user, "prompt_sha256": wire(B_SYSTEM, user)}

    out = {"_meta": {
              "run": "233", "built_from_commit": os.popen(
                  f"git -C {R} rev-parse HEAD").read().strip(),
              "inputs": {**BANKS, F220: F220_SHA, DB: DB_SHA},
              "prompt_sha_construction": "sha256(json.dumps(messages)), as or_harness logs it",
              "pairs": list(PAIRS), "arms": list(ARMS), "n_prompts": len(prompts)},
           "texts": {
              "A_template": {"head": A_HEAD, "mid": A_MID, "tail": A_TAIL,
                             "roles": ROLES, "system": sys_yn,
                             "provenance": "instruction §1.A; role phrases authored "
                                           "(Amendment 0, A0.1)"},
              "B": {"questions": B_QUESTIONS, "questions_sha256": sha(B_QUESTIONS),
                    "form": B_FORM, "system": B_SYSTEM,
                    "provenance": "questions verbatim from instruction §1.B; system "
                                  "message authored (A0.2)"}},
           "prompts": prompts,
           "comparands": {"source": f"{DB} at sha256 {DB_SHA}: views duty_fig7 and "
                                    "duty_floor_used (floor_used = the wording floor)",
                          "cells": comparands()}}
    json.dump(out, open(DEST, "w"), indent=1, ensure_ascii=False)
    print(f"{len(prompts)} prompts and {len(out['comparands']['cells'])} comparand cells "
          f"frozen -> {os.path.relpath(DEST, R)}")
    print(f"  B questions sha256 {sha(B_QUESTIONS)}")
    for pr in PAIRS:
        print(f"  A p{pr}: {prompts[f'A|p{pr}']['user']}")
    print("  B example (p1 PRIV):\n" + "\n".join(
        "    | " + l for l in (B_SYSTEM + "\n" + prompts["B|p1|PRIV"]["user"]).split("\n")))


if __name__ == "__main__":
    main()

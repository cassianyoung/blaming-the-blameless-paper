#!/usr/bin/env python3
"""bank_lock.py : bank rows are authored text, and a mark knows its text.

    python3 scripts/bank_lock.py --selftest

**THE FAULT THIS EXISTS TO PREVENT, MEASURED.** Of 62 human marks made across
three sheets, **37 had been made on text no model ever read**, and nothing in the
pipeline could see it, because nothing in the pipeline knew a mark had a text. The
C gradient, both role-pair gaps and three of the four surviving B rows were
comparisons between two different sentences.

Four rules, enforced here rather than remembered:

1. **A ROW IS A STRING.** `ratify()` freezes authored text and its sha256. Nothing
   composes a row from a prefix, a clause, a middle and an outcome at read time.
   The assembly path is retired under `scripts/superseded/` and refuses to run.
2. **A MARK CARRIES THE SHA OF WHAT IT WAS MADE ON.** `record_mark()` will not
   store a mark without the exact string it was shown.
3. **A COMPARISON ASSERTS, PER ROW, THAT THE TWO SHAS MATCH.** `compare()`
   REFUSES the whole table on any mismatch. It does not warn and it does not drop
   the offending row, because a table that silently shrinks is a table nobody
   checks.
4. **A SHEET IS BUILT FROM THE RATIFIED ROWS BY HASH**, and `sheet_rows()`
   re-hashes every string before it is written out.
"""
import argparse
import hashlib
import json
import os
import sys


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def ratify(proposed, bank, ruling):
    """Freeze proposed rows as authored text. Write-once."""
    if os.path.exists(bank):
        sys.exit(f"write-once: {bank} exists")
    rows = [json.loads(l) for l in open(proposed)]
    out = []
    for r in rows:
        t = r["text"]
        out.append({**r, "text": t, "text_sha256": sha(t), "ratified": ruling})
    with open(bank, "w") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    return out


SHA_FIELDS = ("text_sha256", "sha256")


def load(bank):
    """Every row's stored sha must be the sha of its stored text.

    TWO FIELD NAMES ARE ACCEPTED AND THE CHECK IS NOT RELAXED. The bicycle bank stores
    `text_sha256`; the families bank stores the same quantity under `sha256`. Both are
    sha256 of the row's own text, verified against both banks on 2026-10-05. Before
    this, `load` read `text_sha256` only, so every families row compared its real sha
    against None and the whole bank refused: a correct check that could not see the
    field it was checking.

    **A ROW CARRYING NEITHER FIELD STILL REFUSES**, which is the case that matters: the
    repair widens which name is recognised, it does not make the sha optional. A row
    carrying BOTH refuses too, unless they agree, because two names for one digest is
    how a stale copy survives an edit to the other.
    """
    rows = [json.loads(l) for l in open(bank)]
    bad, nosha = [], []
    for r in rows:
        present = [f for f in SHA_FIELDS if r.get(f)]
        if not present:
            nosha.append(r.get("uid", "<no uid>"))
            continue
        if len({r[f] for f in present}) != 1:
            bad.append(r.get("uid", "<no uid>"))
            continue
        if sha(r["text"]) != r[present[0]]:
            bad.append(r.get("uid", "<no uid>"))
    if nosha:
        sys.exit(f"REFUSING: {len(nosha)} row(s) carry no sha field "
                 f"({' or '.join(SHA_FIELDS)}): {nosha[:5]}")
    if bad:
        sys.exit(f"REFUSING: {len(bad)} row(s) do not match their own sha: {bad[:5]}")
    return rows


def record_mark(uid, text_shown, marks, by, sheet):
    """A mark is inseparable from the string it was made on."""
    if not text_shown:
        sys.exit(f"REFUSING: a mark on {uid} with no text is not a mark")
    return {"uid": uid, "marks": marks, "by": by, "sheet": sheet,
            "text_shown": text_shown, "text_sha256": sha(text_shown)}


def compare(marks, readings, what=""):
    """Refuse the table if any row's mark and reading are on different text."""
    mm = {m["uid"]: m for m in marks}
    bad = []
    for uid, r in readings.items():
        if uid not in mm:
            continue
        if mm[uid]["text_sha256"] != r.get("text_sha256"):
            bad.append(uid)
    if bad:
        sys.exit(f"REFUSING the table {what!r}: {len(bad)} row(s) whose mark and "
                 f"reading are on different text: {sorted(bad)[:6]}. A human column "
                 f"beside a model column is a claim that both read one sentence.")
    return {uid: {"mark": mm[uid]["marks"], **readings[uid]}
            for uid in readings if uid in mm}


def sheet_rows(bank, uids):
    """Rows for a reader sheet, re-hashed on the way out."""
    rows = {r["uid"]: r for r in load(bank)}
    out = []
    for u in uids:
        r = rows[u]
        if sha(r["text"]) != r["text_sha256"]:
            sys.exit(f"REFUSING: {u} changed between load and write")
        out.append(r)
    return out


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    prop = os.path.join(d, "p.jsonl")
    bank = os.path.join(d, "b.jsonl")
    with open(prop, "w") as fh:
        for u, t in (("x__N", "Alaric did the careful thing. Nobody came to any harm."),
                     ("x__C", "Alaric did not look. It broke.")):
            fh.write(json.dumps({"uid": u, "item_id": "x", "arm": u[-1],
                                 "text": t}) + "\n")
    ratify(prop, bank, "selftest")
    rows = {r["uid"]: r for r in load(bank)}
    good = record_mark("x__N", rows["x__N"]["text"], {"blame": 0}, "tester", "s1")
    stale = record_mark("x__C", "Alaric did not look. Something broke.",
                        {"blame": 2}, "tester", "s1")
    readings = {u: {"text_sha256": rows[u]["text_sha256"], "ev": 1.0} for u in rows}
    res = []
    ok = compare([good], {"x__N": readings["x__N"]}, "matched")
    res.append(("a matched row compares", len(ok) == 1))
    import subprocess
    code = ("import sys; sys.path.insert(0,'%s');from bank_lock import compare;"
            "compare([%r],{%r:%r},'x')" % (os.path.dirname(os.path.abspath(__file__)),
                                           stale, "x__C", readings["x__C"]))
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    res.append(("a stale mark REFUSES the table", p.returncode != 0
                and "different text" in p.stderr))
    # a tampered bank must refuse to load
    lines = open(bank).read().replace("careful", "careless")
    open(bank, "w").write(lines)
    p2 = subprocess.run([sys.executable, "-c",
                         "import sys; sys.path.insert(0,'%s');from bank_lock import load;"
                         "load(%r)" % (os.path.dirname(os.path.abspath(__file__)), bank)],
                        capture_output=True, text=True)
    res.append(("a row edited after ratification refuses to load",
                p2.returncode != 0 and "own sha" in p2.stderr))
    try:
        record_mark("x__N", "", {"blame": 0}, "t", "s")
        res.append(("a mark with no text is refused", False))
    except SystemExit:
        res.append(("a mark with no text is refused", True))
    for n, o in res:
        print(f"  {'PASS' if o else 'FAIL'}  {n}")
    return all(o for _, o in res)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)

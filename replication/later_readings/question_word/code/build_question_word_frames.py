"""build_question_word_frames.py : the question-word frames for question_word, frozen before any read.

    python3 scripts/build_question_word_frames.py            # writes the two variant files + manifest
    python3 scripts/build_question_word_frames.py --check    # re-derives and asserts equality, writes nothing

question_word (discovery, nothing registered) asks whether base-model fault blindness depends
on the word "blame". The worksheet is read under three wordings with everything else
fixed: the same header shape, the same four worked examples with the same ratings, the
same five orderings, the same bank.

  blame        records/POD_FRAMES_216.json, UNCHANGED. The baseline is the banked file
               itself, not a copy, so the re-read is the banked instrument by construction.
  at_fault     "How much is X at fault?", "0 means not at all at fault and 9 means
               entirely at fault".
  responsible  "How much is X responsible for what happened?", "0 means not at all
               responsible and 9 means entirely responsible".

The variants are DERIVED from the banked completion frames by exact substitution, and
every substitution count is asserted (one header, four worked questions, one target
question per frame), so no frame can carry a partial rewording.

THE MANIFEST IS THE CONSUMPTION CHECK, NOT THE LOADER. It renders all 930 prompts
(3 wordings x 5 orderings x 62 bank rows) through the reader's own `prompt_for`, hashes
them as the reader does, and asserts:
  1. every blame prompt hash equals the `prompt_sha256_16` local_frames banked for that cell,
     on all six arms (the baseline is byte-identical to what was read);
  2. the three wordings' prompts are pairwise distinct for every (ordering, row);
  3. no variant prompt contains "blame", and each contains its own question string.
After the read, every cell's recorded hash is compared against this manifest.
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bank_lock                                                  # noqa: E402
import rate_pod216 as RP                                          # noqa: E402

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_FRAMES = "records/POD_FRAMES_216.json"
BANK = "data/families_bank/moral__families223__v1.jsonl"
BANK_SHA16 = "1610e8e7018cd2e7"
OUT = {"at_fault": "records/question_word_FRAMES__at_fault.json",
       "responsible": "records/question_word_FRAMES__responsible.json"}
MANIFEST = "records/frames_manifest.json"
ARMS = ["llama31_base", "mistral_base", "qwen3_base", "olmo2_base", "falcon3_base",
        "gemma9_base"]
FAMILIES = ["bicycle", "cheque", "ladder", "prawns_home", "prawns_restaurant",
            "scaffolding"]

HEADER_BLAME = ("Ratings of how much the named person is to blame, on a scale from 0 to "
                "9, where 0 means not at all to blame and 9 means entirely to blame.")
WORDINGS = {
    "at_fault": {
        "header": ("Ratings of how much the named person is at fault, on a scale from 0 "
                   "to 9, where 0 means not at all at fault and 9 means entirely at "
                   "fault."),
        "question": r"\1 at fault?",
        "marker": " at fault?",
    },
    "responsible": {
        "header": ("Ratings of how much the named person is responsible for what "
                   "happened, on a scale from 0 to 9, where 0 means not at all "
                   "responsible and 9 means entirely responsible."),
        "question": r"\1 responsible for what happened?",
        "marker": " responsible for what happened?",
    },
}
# A name is one token in this frame (Ruaridh, Osric, Dilys, Thea, {agent}).
Q_BLAME = re.compile(r"(Question: How much is [^\s?]+) to blame\?")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def derive(base, wording):
    w = WORDINGS[wording]
    out = []
    for f in base:
        if f["delivery"] != "completion":
            continue
        assert f["channel"] == "BLAME", f["id"]
        body = f["body"]
        assert body.count(HEADER_BLAME) == 1, (f["id"], "header")
        body = body.replace(HEADER_BLAME, w["header"])
        body, nq = Q_BLAME.subn(w["question"], body)
        assert nq == 5, (f["id"], "questions", nq)          # four worked + one target
        assert "blame" not in body.lower(), (f["id"], "residual blame")
        req = []
        for r in f["requires_in_prompt"]:
            r2, nr = Q_BLAME.subn(w["question"], r)
            assert nr == 4, (f["id"], "requires", nr)
            assert r2 in body, (f["id"], "requires not in body")
            req.append(r2)
        g = dict(f)
        g.update({"id": f"{f['id']}__{wording}", "body": body, "requires_in_prompt": req,
                  "wording": wording, "derived_from": f["id"],
                  "derived_from_file": BASE_FRAMES,
                  "why": f"question_word question-word variant ({wording}) of {f['id']}; "
                         f"exemplars, ratings and ordering unchanged"})
        out.append(g)
    assert len(out) == 5, len(out)
    return out


def views(rows):
    return {fam: {r["role"]: r for r in rows if r.get("family") == fam}
            for fam in FAMILIES}


def render_all(frames_by_wording, rows):
    """{wording: {frame_index: {family: {role: sha16}}}} via the reader's prompt_for."""
    out = {}
    for wd, frames in frames_by_wording.items():
        comp = [f for f in frames if f["delivery"] == "completion"]
        out[wd] = {}
        for i, f in enumerate(comp):
            out[wd][f["id"]] = {}
            for fam, fr in views(rows).items():
                out[wd][f["id"]][fam] = {}
                for role, row in fr.items():
                    p, wrap = RP.prompt_for(f, row["text"], None)
                    assert wrap == "raw", (f["id"], wrap)
                    out[wd][f["id"]][fam][role] = {
                        "sha16": sha(p.encode())[:16],
                        "has_blame": "blame" in p.lower(),
                        "has_marker": (WORDINGS[wd]["marker"] in p) if wd in WORDINGS
                                      else None}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)

    base_bytes = open(f"{R}/{BASE_FRAMES}", "rb").read()
    base = json.loads(base_bytes)
    rows = bank_lock.load(f"{R}/{BANK}")
    bank_sha = sha(open(f"{R}/{BANK}", "rb").read())
    assert bank_sha.startswith(BANK_SHA16), bank_sha

    variants = {wd: derive(base, wd) for wd in WORDINGS}
    texts = {wd: (json.dumps(v, indent=1, ensure_ascii=False) + "\n").encode()
             for wd, v in variants.items()}
    frames_by_wording = {"blame": base, **variants}
    pr = render_all(frames_by_wording, rows)

    # 1. blame prompts == local_frames's banked hashes, every arm, every cell
    checked = 0
    for arm in ARMS:
        for fam in FAMILIES:
            d = json.load(open(f"{R}/runs/local_frames_R/results/pod223__{arm}__{fam}__completion.json"))
            for k, c in d["cells"].items():
                role, ch, fid = k.split("|")
                if ch != "BLAME" or c.get("void"):
                    continue
                want = pr["blame"][fid][fam][role]["sha16"]
                assert c["prompt_sha256_16"] == want, (arm, fam, k)
                checked += 1
    # 2. pairwise distinct across wordings, 3. markers
    n = 0
    base_ids = [f["id"] for f in base if f["delivery"] == "completion"]
    for i, bid in enumerate(base_ids):
        for fam in FAMILIES:
            for role in pr["blame"][bid][fam]:
                hs = [pr["blame"][bid][fam][role]["sha16"]] + [
                    pr[wd][f"{bid}__{wd}"][fam][role]["sha16"] for wd in WORDINGS]
                assert len(set(hs)) == 3, (bid, fam, role)
                assert pr["blame"][bid][fam][role]["has_blame"]
                for wd in WORDINGS:
                    c = pr[wd][f"{bid}__{wd}"][fam][role]
                    assert not c["has_blame"] and c["has_marker"], (wd, bid, fam, role)
                n += 1
    total = 3 * n

    manifest = {
        "run": "239", "what": "question-word frames, frozen before any read",
        "bank": BANK, "bank_sha256": bank_sha,
        "frames": {"blame": {"file": BASE_FRAMES, "sha256": sha(base_bytes)},
                   **{wd: {"file": OUT[wd], "sha256": sha(texts[wd])} for wd in WORDINGS}},
        "headers": {"blame": HEADER_BLAME, **{wd: w["header"] for wd, w in WORDINGS.items()}},
        "prompts_rendered": total,
        "blame_cells_matched_to_local_frames": checked,
        "assertions": ["blame prompt sha16 == local_frames banked prompt_sha256_16, 6 arms",
                       "three wordings pairwise distinct for every (ordering, row)",
                       "no variant prompt contains 'blame'; each carries its own question"],
        "prompt_sha16": {wd: {fid: v for fid, v in d.items()} for wd, d in pr.items()},
    }
    mtext = (json.dumps(manifest, indent=1, ensure_ascii=False) + "\n").encode()

    if a.check:
        for wd in WORDINGS:
            assert open(f"{R}/{OUT[wd]}", "rb").read() == texts[wd], OUT[wd]
        assert open(f"{R}/{MANIFEST}", "rb").read() == mtext, MANIFEST
        print(f"CHECK OK: {total} prompts, {checked} blame cells equal local_frames's, "
              f"files byte-identical to a fresh derivation")
        return 0
    for p in list(OUT.values()) + [MANIFEST]:
        if os.path.exists(f"{R}/{p}"):
            sys.exit(f"REFUSING: {p} exists. Write-once, no override.")
    for wd in WORDINGS:
        open(f"{R}/{OUT[wd]}", "wb").write(texts[wd])
    open(f"{R}/{MANIFEST}", "wb").write(mtext)
    print(f"wrote {OUT['at_fault']} {sha(texts['at_fault'])[:16]}")
    print(f"wrote {OUT['responsible']} {sha(texts['responsible'])[:16]}")
    print(f"wrote {MANIFEST} {sha(mtext)[:16]}: {total} prompts; "
          f"{checked} blame cells equal local_frames's banked hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Rebuild the exact training corpora from the published corpora and their sources.

    python rebuild_training_corpus.py english SENTIMENT140_CSV OUTDIR
    python rebuild_training_corpus.py chinese COIG_CQIA_DIR OUTDIR

english: the published English corpus omits four rows whose text is a tweet from
Sentiment140 (training.1600000.processed.noemoticon.csv, in
https://cs.stanford.edu/people/alecmgo/trainingandtestdata.zip).

chinese: the published Chinese corpus omits the rows drawn from COIG-CQIA; COIG_CQIA_DIR
is a checkout of the m-a-p/COIG-CQIA dataset at the commit recorded in
withheld_coig_cqia_rows.json.

Each withheld row is put back at its original line and the rebuilt files are checked
against the training corpus's recorded SHA-256; the script exits 1 if any differs, which
is what happens if a source dataset has changed. The English translation of the Chinese
corpus cannot be rebuilt from public sources (see withheld_coig_cqia_rows.json).

Each published row ends with a `licence` field that the training rows did not carry; it
is removed from every published line before the withheld rows are put back.
"""
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LICENCE = ', "licence": '


def published_lines(name):
    """The published corpus's lines with the trailing licence field removed."""
    out = []
    for line in open(os.path.join(HERE, name), encoding="utf-8", newline="").readlines():
        i = line.rindex(LICENCE)
        if not isinstance(json.loads(line)["licence"], dict) or line[i:].count("{") != 1:
            sys.exit(f"{name}: a row's licence field is not its last field")
        out.append(line[:i] + "}\n")
    return out
TRAINING_SHA256 = {
    "instruction_corpus_en.jsonl":
        "8df234ca2d836eeb51d750e9800e8564efc69c653f4181b5c0aeb9f0ac26f87f",
    "instruction_corpus_en_heldout.jsonl":
        "0cf2a2dbe09739b59ccfcd1cdf09517863a5cedee1286fa3fc34b831d67f1814",
}
# file, 0-based line, uid, row sha, kind_rated, question, answer, Sentiment140 tweet id
WITHHELD = [
    ("instruction_corpus_en.jsonl", 264, "st-012534", "ebf68d8348bdbc78", "depends",
     "Write a positive tweet.", "{tweet}", "1754878271"),
    ("instruction_corpus_en.jsonl", 357, "st-009490", "8ffa7551db882f47", "depends",
     "Write a tweet that is positive.", "{tweet}", "1975723354"),
    ("instruction_corpus_en.jsonl", 691, "st-002318", "cb684973b39e82d8", "determinate",
     "Generate a tweet that has the following sentiment: negative", "{tweet}",
     "1564929931"),
    ("instruction_corpus_en_heldout.jsonl", 34, "st-003093", "047caa4cd1cf7e8e", "determinate",
     "Tweet: {tweet} Predict the sentiment of this tweet. OPTIONS: - negative - positive",
     "positive", "2014762793"),
]


def tweets(csv_path, ids):
    out = {}
    with open(csv_path, encoding="latin-1", newline="") as fh:
        for row in csv.reader(fh):
            if len(row) >= 6 and row[1] in ids:
                out[row[1]] = row[5].strip()
    missing = set(ids) - set(out)
    if missing:
        sys.exit(f"tweet ids not found in {csv_path}: {sorted(missing)}")
    return out


def chinese(coig_dir, outdir):
    rec = json.load(open(os.path.join(HERE, "withheld_coig_cqia_rows.json"), encoding="utf-8"))
    name = "instruction_corpus_zh.jsonl"
    c = rec["corpora"][name]
    cache = {}
    lines = published_lines(name)
    for w in sorted(c["withheld"], key=lambda w: w["line"]):
        f = w["coig_file"]
        if f not in cache:
            cache[f] = open(os.path.join(coig_dir, f), encoding="utf-8", newline="").readlines()
        src = json.loads(cache[f][w["coig_line"]])
        q, a = src["instruction"].strip(), src["output"].strip()   # as the corpus was built
        prompt = f"Q: {q}\nA:"
        text = {"question": q, "answer": a, "prompt": prompt, "completion": " " + a,
                "text": prompt + " " + a}
        row = {k: (text[k] if k in text else w["fields"][k]) for k in w["keys"]}
        lines.insert(w["line"], json.dumps(row, ensure_ascii=False) + "\n")
    body = "".join(lines)
    got = hashlib.sha256(body.encode("utf-8")).hexdigest()
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, name), "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
    ok = got == c["training_sha256"]
    print(f"{name}: {len(lines)} rows, sha256 {got} "
          f"{'MATCHES' if ok else 'DOES NOT MATCH'} the training corpus")
    return ok


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("english", "chinese"):
        sys.exit(__doc__)
    which, src, outdir = sys.argv[1:]
    if which == "chinese":
        sys.exit(0 if chinese(src, outdir) else 1)
    csv_path = src
    text = tweets(csv_path, {w[7] for w in WITHHELD})
    os.makedirs(outdir, exist_ok=True)
    ok = True
    for name, want in TRAINING_SHA256.items():
        lines = published_lines(name)
        for f, pos, uid, sha, kind_rated, q, a, tid in sorted(
                (w for w in WITHHELD if w[0] == name), key=lambda w: w[1]):
            question, answer = q.format(tweet=text[tid]), a.format(tweet=text[tid])
            prompt = f"Q: {question}\nA:"
            row = {"kind": "unlabelled", "source": "flan", "question": question,
                   "answer": answer, "uid": uid, "sha": sha, "kind_rated": kind_rated,
                   "prompt": prompt, "completion": " " + answer,
                   "text": prompt + " " + answer}
            lines.insert(pos, json.dumps(row) + "\n")
        body = "".join(lines)
        got = hashlib.sha256(body.encode("utf-8")).hexdigest()
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
            fh.write(body)
        print(f"{name}: {len(lines)} rows, sha256 {got} "
              f"{'MATCHES' if got == want else 'DOES NOT MATCH'} the training corpus")
        ok &= got == want
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

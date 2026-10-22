"""question_word_wording.py : one base arm, three question wordings, ONE model load.

    python3 scripts/question_word_wording.py --arm gemma9_base --model google/gemma-2-9b
    python3 scripts/question_word_wording.py --arm gemma9_base --model gpt2 --dry-run   # CPU

IT IS A DRIVER, NOT A FORK (as rate_material_multi.py). It calls `rate_pod216.main(argv)`
once per wording in one process, with the module's FRAMES pointed at that wording's
frozen frame file and `gradient_model.load` memoised, so the load is paid once. No
scoring logic lives here.

WHY NOT --extra-frames: rate_pod216 pools every completion frame on channel BLAME into
one mean and one band. Appended variant frames would be averaged INTO the blame
baseline. Each wording is therefore its own call, its own artefact and its own band.

Every argument rate_pod216 receives is the local_frames base-arm invocation, minus --harvest
(no activations are wanted; the hidden-state gather does not touch the logits read).
Artefacts land at runs/question_word/<wording>/results/pod223__<arm>__<family>__completion.json,
write-once by the reader's own rule.

AFTER EACH WORDING the artefacts are checked against records/frames_manifest.json:
the artefact's frames_sha256 must be that wording's frozen sha, and every non-void
BLAME-channel cell's prompt_sha256_16 must equal the manifest's hash for its (frame,
family, role). A mismatch exits non-zero: material that parsed is not material that was
consumed.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rate_pod216 as RP                                          # noqa: E402
import gradient_model as MODEL                                    # noqa: E402

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = "records/frames_manifest.json"
BANK = "data/families_bank/moral__families223__v1.jsonl"
FAMS = "bicycle,cheque,ladder,prawns_home,prawns_restaurant,scaffolding"
WORDINGS = ["blame", "at_fault", "responsible"]

_real_load = MODEL.load
_cache = {}


def _memo_load(model_id, spec, threads=None, adapter=None, trust_remote_code=False):
    key = (model_id, spec, adapter, trust_remote_code)
    if key not in _cache:
        _cache[key] = _real_load(model_id, spec, threads=threads, adapter=adapter,
                                 trust_remote_code=trust_remote_code)
    return _cache[key]


def verify(run, arm, wording, man, dry):
    want_sha = man["frames"][wording]["sha256"]
    hashes = man["prompt_sha16"][wording]
    n_ok, bad = 0, []
    for fam in FAMS.split(","):
        p = f"{R}/runs/{run}/results/pod223__{arm}__{fam}__completion.json"
        if not os.path.exists(p):
            bad.append(f"{fam}: no artefact")
            continue
        d = json.load(open(p))
        if d["frames_sha256"] != want_sha:
            bad.append(f"{fam}: frames_sha256 {d['frames_sha256'][:16]} != {want_sha[:16]}")
        for k, c in d["cells"].items():
            role, ch, fid = k.split("|")
            if ch != "BLAME" or c.get("void"):
                continue
            exp = hashes.get(fid, {}).get(fam, {}).get(role, {}).get("sha16")
            if c["prompt_sha256_16"] != exp:
                bad.append(f"{fam} {k}: prompt {c['prompt_sha256_16']} != {exp}")
            else:
                n_ok += 1
    return n_ok, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--run", default="question_word")
    ap.add_argument("--wordings", default=",".join(WORDINGS))
    ap.add_argument("--trust-remote-code", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    man = json.load(open(f"{R}/{MANIFEST}"))
    MODEL.load = _memo_load
    RP.MODEL.load = _memo_load
    worst = 0
    for wd in [w.strip() for w in a.wordings.split(",") if w.strip()]:
        if wd not in man["frames"]:
            sys.exit(f"REFUSING: wording {wd!r} is not in {MANIFEST}")
        RP.FRAMES = man["frames"][wd]["file"]
        run = f"{a.run}/{wd}"
        argv = ["--run", run, "--arm", a.arm, "--model", a.model,
                "--delivery", "completion", "--spec", "cuda:bfloat16",
                "--read-through-gate", "--bank", BANK, "--families", FAMS]
        if a.trust_remote_code:
            argv.append("--trust-remote-code")
        if a.dry_run:
            argv.append("--dry-run")
        print(f"==== question_word  {a.arm}  wording {wd}  frames {RP.FRAMES}", flush=True)
        try:
            rc = RP.main(argv) or 0
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else 1
            print(f"   rate_pod216 exited {e.code!r}", flush=True)
        n_ok, bad = verify(run, a.arm, wd, man, a.dry_run)
        if bad:
            print(f"   CONSUMPTION CHECK FAILED ({len(bad)}): " + "; ".join(bad[:6]),
                  flush=True)
            worst = 2
        else:
            print(f"   consumption check OK: {n_ok} cells carry the frozen prompt hashes",
                  flush=True)
        print(f"   wording {wd} rc {rc}", flush=True)
    print(f"==== question_word {a.arm} done; loads paid {len(_cache)}", flush=True)
    return worst


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""duty_on_base_duty_worksheet.py : one arm, ONE load, the worksheet bank then the duty legs.

    python3 scripts/duty_on_base_duty_worksheet.py --arm gemma9_base
    python3 scripts/duty_on_base_duty_worksheet.py --arm gemma9_base --model gpt2 --dry-run   # CPU

A DRIVER, NOT A FORK (as question_word_wording.py). Per arm, on one memoised load:
  (1) the banked worksheet on the local_frames bank, by calling rate_pod216.main(argv) with the
      local_frames / question_word base-arm invocation (completion, cuda:bfloat16, read-through-gate,
      no harvest). This is each arm's ruler and gate on the frame the duty legs are read
      on, and on the six base arms it is local_frames's read again (the reproduction check).
      Artefacts: runs/duty_on_base/worksheet/results/pod223__<arm>__<family>__completion.json.
  (2) the twelve duty legs through the same five completion orderings, by
      rate_pod216.read_cell, the function that scored every banked worksheet cell.
      Artefact: runs/duty_on_base/duty/duty_on_base__<arm>.json (write-once).

AFTER (1) every non-void BLAME cell's prompt hash is checked against question_word's frozen
manifest for the blame wording (the same frames file, the same bank); AFTER (2) every duty
cell's prompt hash is checked against records/frames.json. A mismatch exits 2:
material that parsed is not material that was consumed.
"""
import argparse, hashlib, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rate_pod216 as RP                                          # noqa: E402
import gradient_model as MODEL                                    # noqa: E402

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES245 = "records/frames.json"
FRAMES245_SHA = "7fb5badfad0b1994efca57c4d4cc45d44109a9743f56584f57e8db2281c2ed04"   # frozen 2026-11-06
MANIFEST239 = "records/frames_manifest.json"
BANK = "data/families_bank/moral__families223__v1.jsonl"
FAMS = "bicycle,cheque,ladder,prawns_home,prawns_restaurant,scaffolding"

_real_load = MODEL.load
_cache = {}


def _memo_load(model_id, spec, threads=None, adapter=None, trust_remote_code=False):
    key = (model_id, spec, adapter, trust_remote_code)
    if key not in _cache:
        _cache[key] = _real_load(model_id, spec, threads=threads, adapter=adapter,
                                 trust_remote_code=trust_remote_code)
    return _cache[key]


def load_frames(want=None):
    blob = open(os.path.join(R, FRAMES245), "rb").read()
    want = want if want is not None else FRAMES245_SHA
    if want is None:
        sys.exit("REFUSING: FRAMES245_SHA is not pinned; freeze the frames first")
    if hashlib.sha256(blob).hexdigest() != want:
        sys.exit("REFUSING: records/frames.json does not hash to its pinned sha")
    return json.loads(blob)


def verify_worksheet(arm, run="duty_on_base"):
    man = json.load(open(os.path.join(R, MANIFEST239)))
    want_sha, hashes = man["frames"]["blame"]["sha256"], man["prompt_sha16"]["blame"]
    n_ok, bad = 0, []
    for fam in FAMS.split(","):
        p = f"{R}/runs/{run}/worksheet/results/pod223__{arm}__{fam}__completion.json"
        if not os.path.exists(p):
            bad.append(f"{fam}: no artefact"); continue
        d = json.load(open(p))
        if d["frames_sha256"] != want_sha:
            bad.append(f"{fam}: frames_sha256 {d['frames_sha256'][:16]} != {want_sha[:16]}")
        for k, c in d["cells"].items():
            role, ch, fid = k.split("|")
            if ch != "BLAME" or c.get("void"):
                continue
            if c["prompt_sha256_16"] != hashes.get(fid, {}).get(fam, {}).get(role, {}).get("sha16"):
                bad.append(f"{fam} {k}")
            else:
                n_ok += 1
    return n_ok, bad


def read_duty(arm, model_id, fr, spec, dry, trust, run="duty_on_base"):
    dest = f"{R}/runs/{run}/duty/duty_on_base__{arm}.json"
    if os.path.exists(dest):
        print(f"   duty: {os.path.relpath(dest, R)} exists (write-once); not re-read", flush=True)
        return json.load(open(dest))
    tok, model, meta = MODEL.load(model_id, spec, trust_remote_code=trust)
    frames = {f["id"]: f for f in json.load(open(f"{R}/{RP.FRAMES}")) if f["id"] in fr["frames"]}
    cells, bad = {}, []
    t0 = time.time()
    for key, leg in fr["legs"].items():
        for fid in fr["frames"]:
            c = RP.read_cell(tok, model, frames[fid], leg["text"])
            if not c.get("void") and c["prompt_sha256_16"] != fr["prompt_sha16"][key][fid]:
                bad.append(f"{key} {fid}")
            cells[f"{key}|{fid}"] = c
    out = {"run": "245", "arm": arm, "model": model_id, "spec": spec, "dry_run": dry,
           "frames245_sha256": FRAMES245_SHA, "worksheet_frames": RP.FRAMES,
           "load_meta": {k: str(v) for k, v in meta.items()}, "cells": cells,
           "consumption_bad": bad, "elapsed_s": round(time.time() - t0, 1)}
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "x") as f:
        json.dump(out, f, indent=1)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--model", default=None, help="override the frozen Hub id (dry runs only)")
    ap.add_argument("--trust-remote-code", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--unpinned-frames-for-dry-run", default=None)
    a = ap.parse_args(argv)
    if a.dry_run and a.unpinned_frames_for_dry_run:
        fr = json.load(open(a.unpinned_frames_for_dry_run))
    else:
        fr = load_frames()
    arms = {x["arm"]: x for x in fr["arms"]}
    if a.arm not in arms:
        sys.exit(f"REFUSING: unknown arm {a.arm!r}")
    if a.model and not a.dry_run:
        sys.exit("REFUSING: --model overrides the frozen Hub id and is for dry runs only")
    model_id = a.model or arms[a.arm]["model"]
    spec = "cpu:float32" if a.dry_run else "cuda:bfloat16"
    MODEL.load = _memo_load
    RP.MODEL.load = _memo_load
    run = "duty_on_base_dry" if a.dry_run else "duty_on_base"     # a dry run never touches the write-once paths
    worst = 0
    # (1) the banked worksheet: the local_frames base-arm invocation, unchanged
    argv1 = ["--run", f"{run}/worksheet", "--arm", a.arm, "--model", model_id,
             "--delivery", "completion", "--spec", "cuda:bfloat16", "--read-through-gate",
             "--bank", BANK, "--families", FAMS]
    if a.trust_remote_code:
        argv1.append("--trust-remote-code")
    if a.dry_run:
        argv1.append("--dry-run")
    print(f"==== duty_on_base  {a.arm}  {model_id}  (1) worksheet", flush=True)
    try:
        rc = RP.main(argv1) or 0
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
        print(f"   rate_pod216 exited {e.code!r}", flush=True)
    n_ok, bad = verify_worksheet(a.arm, run)
    print(f"   worksheet rc {rc}; consumption {'OK: ' + str(n_ok) + ' cells' if not bad else 'FAILED: ' + '; '.join(bad[:6])}", flush=True)
    if bad and not a.dry_run:
        worst = 2
    # (2) the duty legs, on the same load
    print(f"==== duty_on_base  {a.arm}  (2) duty legs", flush=True)
    d = read_duty(a.arm, model_id, fr, spec, a.dry_run, a.trust_remote_code, run)
    if d["consumption_bad"] and not a.dry_run:
        print(f"   duty CONSUMPTION CHECK FAILED: {d['consumption_bad'][:6]}", flush=True)
        worst = 2
    else:
        nv = sum(1 for c in d["cells"].values() if not c.get("void"))
        print(f"   duty: {nv} of {len(d['cells'])} cells read; consumption OK", flush=True)
    print(f"==== duty_on_base {a.arm} done; loads paid {len(_cache)}", flush=True)
    return worst


if __name__ == "__main__":
    sys.exit(main())

"""Re-read one of the paper's readings with due-care-eval and compare it with the paper.

    python replication/run_reading.py --list
    python replication/run_reading.py READING [--models a,b] [--out DIR] [--plan]

READING is a key of `readings.json` (deployed_excuse, deployed_duty, local_frames,
yi_adapter_controls). Each run in it is one `inspect eval` of one model on one task and
frame, with the model table pointed at `replication/models/`. When every run has
finished, `compare.py` compares the logs with `reference/paper_values.json` and writes
`comparison.md` beside them.

`--models` restricts the reading to some of its models (for example the ones a card can
hold); `--plan` prints the commands without running them. The output directory must not
exist yet. Needs due-care-eval installed (see README.md in this directory); API readings
need OPENROUTER_API_KEY, and local readings a CUDA device with the memory the model needs.
"""
import argparse
import json
import os
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
READINGS = json.load(open(os.path.join(HERE, "readings.json"), encoding="utf-8"))


def commands(reading, models, log_dir):
    for r in READINGS["readings"][reading]["runs"]:
        if models and r["model"] not in models:
            continue
        cmd = ["inspect", "eval", f"due_care/{r['task']}", "--model",
               f"due_care/{r['model']}", "-T", f"frame={r['frame']}"]
        for a in r["args"]:
            cmd += ["-T", a]
        yield r, cmd + ["--log-dir", log_dir, "--display", "plain"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("reading", nargs="?")
    ap.add_argument("--list", action="store_true", help="list the readings and exit")
    ap.add_argument("--models", default=None, help="comma-separated model ids")
    ap.add_argument("--out", default=None, help="output directory (default replication_out/READING)")
    ap.add_argument("--plan", action="store_true", help="print the commands only")
    a = ap.parse_args()

    if a.list or not a.reading:
        for k, v in READINGS["readings"].items():
            print(f"{k}: {len(v['runs'])} runs on {v['where']} models; {v['what']}")
            print(f"    feeds: {', '.join(v['paper'])}")
            print(f"    data labels: {', '.join(v['replaces_labels'])}")
        print("not re-readable with the eval:")
        for k, why in READINGS["not_rereadable"].items():
            print(f"  {k}: {why}")
        return
    if a.reading not in READINGS["readings"]:
        sys.exit(f"unknown reading {a.reading!r}; see --list")
    models = set(a.models.split(",")) if a.models else None
    known = {r["model"] for r in READINGS["readings"][a.reading]["runs"]}
    if models and models - known:
        sys.exit(f"not in {a.reading}: {sorted(models - known)}")

    out = os.path.abspath(a.out or os.path.join("replication_out", a.reading))
    log_dir = os.path.join(out, "logs")
    plan = list(commands(a.reading, models, log_dir))
    env = dict(os.environ, DUE_CARE_MODELS=os.path.join(HERE, "models"))
    print(f"{a.reading}: {len(plan)} runs; model table {env['DUE_CARE_MODELS']}")
    if a.plan:
        for _, cmd in plan:
            print("  DUE_CARE_MODELS=replication/models " + shlex.join(cmd))
        return
    if os.path.exists(out):
        sys.exit(f"refusing: {out} exists; a reading writes a fresh directory")
    os.makedirs(log_dir)
    failed = []
    for i, (r, cmd) in enumerate(plan, 1):
        print(f"[{i}/{len(plan)}] {r['model']} {r['task']} {r['frame']} {' '.join(r['args'])}",
              flush=True)
        if subprocess.run(cmd, env=env).returncode:
            failed.append(f"{r['model']} {r['task']} {r['frame']}")
    logs = sorted(os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith(".eval"))
    res = subprocess.run([sys.executable, os.path.join(HERE, "compare.py"), *logs,
                          "--out", os.path.join(out, "comparison.md")], env=env)
    if failed:
        print("runs that did not complete: " + "; ".join(failed))
    print(f"comparison: {os.path.join(out, 'comparison.md')}")
    sys.exit(1 if failed or res.returncode else 0)


if __name__ == "__main__":
    main()

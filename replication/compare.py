"""Compare a fresh reading with the paper's values (reference/paper_values.json).

    python replication/compare.py LOG [LOG ...] [--out REPORT.md]

Needs due-care-eval installed: the logs are turned into a database by its
`db.build_from_readings` and summarised by its `due_care.metrics`, the same code the
eval's own report uses.

LOCAL ARMS (teacher-forced reads on pinned weights): every position, band, gate and
expected digit must equal the paper's to its printed precision, two decimals. bf16
kernels differ between GPUs, so bit-identity is not required; any value that differs at
two decimals is listed as a discrepancy.

API ARMS: the served model may have changed, so each value must fall within the arm's
draw band: 2.33 x the sd over the fresh draws of the cell, floored at 0.30 digits (the
construction of the duty test's draw floor). A position's band is that digit band
divided by the fresh C - N. A difference of two cells (a gap) takes the band
sqrt(b1^2 + b2^2).

The duty test's wording floor, signal-to-noise and class are pooled over every pair an
arm was read on, so on a partial read they are reported and marked not comparable.
"""
import argparse
import hashlib
import json
import math
import os
import sys

from db import build_from_readings as B
from due_care import metrics as M

HERE = os.path.dirname(os.path.abspath(__file__))

FLOOR = 0.30
Z = 2.33


def band(sd):
    return max(Z * (sd or 0.0), FLOOR)


def fmt(x, nd=4):
    return "-" if x is None else f"{x:.{nd}f}"


def compare(logs):
    ref = json.load(open(os.path.join(HERE, "reference", "paper_values.json")))
    cells = B.cells_from_logs(logs)
    con = B.build(cells)
    sd = {(c["model_id"], c.get("scenario"), c.get("role"), c.get("question")): c.get("ev_sd")
          for c in cells if c.get("test") == "excuse" and c.get("frame") == "chat"}
    kind = {c["model_id"]: c.get("model_kind") for c in cells}
    rows, bad = [], []

    def add(what, paper, fresh, tol, rule):
        if paper is None or fresh is None:
            ok = None
        elif rule == "printed":
            ok = round(paper, 2) == round(fresh, 2)
        else:
            ok = abs(fresh - paper) <= tol
        rows.append((what, paper, fresh, None if paper is None or fresh is None
                     else fresh - paper, tol, rule, ok))
        if ok is False:
            bad.append(what)

    for (arm, frame, scen), v in sorted(M.excuse_summary(con).items()):
        r = ref["excuse"].get(f"{arm}|{frame}|{scen}")
        if r is None:
            rows.append((f"{arm} {frame} {scen}: no paper value", None, None, None,
                         None, "-", None))
            continue
        local = kind.get(arm) == "local"
        rule = "printed" if local else "draw band"
        cn = (v.get("C") or 0) - (v.get("N") or 0)
        for role in ("N", "C", "I", "P0", "P1", "BYSTANDER"):
            b = band(sd.get((arm, scen, role, "BLAME")))
            add(f"{arm} {frame} {scen} mean {role}", r["ev"].get(role),
                v["means"].get(role), None if local else b, rule)
            if role not in ("N", "C"):
                add(f"{arm} {frame} {scen} position {role}", r["positions"].get(role),
                    v["positions"].get(role), None if local or not cn else b / abs(cn), rule)
        add(f"{arm} {frame} {scen} gate statistic", r.get("gate_stat_value"),
            v.get("gate_value"), None if local else 0.05, rule)
        rows.append((f"{arm} {frame} {scen} gate verdict", r.get("gate"), v.get("gate"),
                     None, None, "equal", r.get("gate") == v.get("gate")))
        if r.get("gate") != v.get("gate"):
            bad.append(f"{arm} {frame} {scen} gate verdict")
        if frame == "worksheet":
            add(f"{arm} {frame} {scen} band", r.get("band"), v.get("band"), None, "printed")
        j = r.get("judgement_P0") or {}
        if j.get("p_reasonable_yes") is not None:
            add(f"{arm} {frame} {scen} P(yes) prevention on P0", j["p_reasonable_yes"],
                v.get("P0_reasonable_p_yes"), 0.10, "absolute 0.10")

    duty = M.duty_summary(con)
    for (arm, pid), v in sorted(duty.items()):
        r = ref["duty"].get(f"{arm}|{pid}")
        if r is None:
            continue
        gb = math.sqrt(2) * FLOOR
        for k, rk in (("gap_pro_first", "stated_gap_pro_first"),
                      ("gap_priv_first", "stated_gap_priv_first"),
                      ("stated_gap", "stated_gap"), ("separate_gap", "separate_gap"),
                      ("stated_condition_gap", "stated_condition_gap"),
                      ("neutral_baseline", "neutral_baseline")):
            add(f"{arm} duty {pid} {k}", r.get(rk), v.get(k), gb, "draw band")
        for k in ("floor_used", "signal_to_noise", "stated_condition_vs_stated"):
            rows.append((f"{arm} duty {pid} {k}", r.get(k), v.get(k), None, None,
                         "not comparable on a partial read", None))
    return rows, bad


def render(rows, bad, logs):
    out = ["| quantity | paper | fresh | difference | tolerance | rule | within |",
           "|---|---|---|---|---|---|---|"]
    for what, p, f, d, tol, rule, ok in rows:
        pv = p if isinstance(p, str) else fmt(p)
        fv = f if isinstance(f, str) else fmt(f)
        out.append(f"| {what} | {pv} | {fv} | {fmt(d)} | {fmt(tol, 3)} | {rule} | "
                   f"{'-' if ok is None else 'yes' if ok else 'NO'} |")
    n = sum(1 for r in rows if r[6] is not None)
    out.append("")
    out.append(f"{n - len(bad)} of {n} checked values within their rule; "
               f"{len(bad)} discrepancies" + (": " + "; ".join(bad) if bad else ""))
    out.append("")
    out.append("Logs: " + ", ".join(
        f"`{os.path.basename(p)}` sha256 "
        f"`{hashlib.sha256(open(p, 'rb').read()).hexdigest()}`" for p in logs))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows, bad = compare(a.logs)
    txt = render(rows, bad, a.logs)
    print(txt)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(txt + "\n")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

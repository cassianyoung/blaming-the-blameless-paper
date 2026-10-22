#!/usr/bin/env python3
"""analyse_serial_pipeline.py : serial_pipeline, the serial pipeline check. Pure function of the read files.

    python3 scripts/analyse_serial_pipeline.py            # writes records/result.json
    python3 scripts/analyse_serial_pipeline.py --dry      # prints, writes nothing
    python3 scripts/analyse_serial_pipeline.py --selftest # synthetic reads, offline

Rules are Amendment 0 of records/PREREG_serial_pipeline_PIPELINE.md, fixed before any call:
  position     (P0 - N) / (C - N), each condition on its OWN N and C (A0.6)
  gate         P0, N, C each >= 7 of 10 parsed; N blame mass(0-3) >= 0.80; C != N (A0.6)
  population   the twelve arms' arm-scenario cells gated in ALL FOUR conditions (A0.7)
  share        cells with position > 0.10, the paper's ruled band (A0.5 of practical_syllogism)
  serial_pipeline P1       PASS iff share(2B) - share(O) <= 0.15 AND share(D) - share(2B) >= 0.30
  serial_pipeline P2       PASS iff |share(2A) - share(D)| <= 0.15                         (A0.8)
  interval     95% bootstrap over arms, 10,000 resamples, seed 240, beside each share
  1B coding    classify_1b(): "could not" / "could" / "unclear", by rule (A0.10)
  1A flags     flag_1a(): conclusion vocabulary present in the summary and absent from
               the case text (A0.11)
deepseek_s is the sampled DeepSeek-V4.1 check: computed identically, reported apart.
"""
import argparse, json, os, random, re, statistics as st, sys

R = os.environ.get("AI_ETHICS_ROOT") or os.path.expanduser("~/working_repository")
TWELVE = ["claude", "deepseek", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s", "grok43_s",
          "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b"]
CHECK = ["deepseek_s"]
SCEN = ("bicycle", "ladder", "prawns_home", "prawns_restaurant", "scaffolding", "cheque")
CONDS = ("2A", "2B", "D", "O")
COND_NAME = {"2A": "summary forward", "2B": "conclusion forward", "D": "direct verdict",
             "O": "one answer"}
BAND = 0.10
PARSE_MIN, N_MASS03_MIN = 7, 0.80
BAND_EQ, BAND_GAP = 0.15, 0.30
NBOOT, SEED = 10000, 240
BANKED = {"D": (57, 69), "O": (9, 69)}      # practical_syllogism on the twelve: 83% and 13%
DEST = f"{R}/records/result.json"

# ── A0.10: CALL 1B, BY RULE ───────────────────────────────────────────────────────
_NEG = re.compile(r"\b(could\s*not|couldn'?t|cannot|can'?t|could\s+not\s+reasonably|"
                  r"would\s+not\s+have\s+been\s+able|was\s+not\s+able|wasn'?t\s+able|"
                  r"no\s+reasonable\s+way|not\s+reasonably|unforeseeable|unavoidable|"
                  r"beyond\s+(his|alaric'?s)\s+(reasonable\s+)?control)\b|^\s*no\b", re.I)
_POS = re.compile(r"\b(could\s+(reasonably\s+)?have\s+(prevented|avoided)|"
                  r"could\s+have\s+been\s+prevented|was\s+preventable|"
                  r"should\s+have)\b|^\s*yes\b", re.I)


def classify_1b(text):
    t = (text or "").replace("’", "'")
    neg, pos = bool(_NEG.search(t)), bool(_POS.search(t))
    if neg and not pos:
        return "could not"
    if pos and not neg:
        return "could"
    return "unclear"


# ── A0.11: CALL 1A STATING A CONCLUSION DESPITE THE INSTRUCTION ───────────────────
CONCLUSION_TERMS = ("fault", "blame", "negligen", "careless", "responsib", "liab",
                    "could not have", "couldn't have", "could not reasonably",
                    "not have prevented", "unavoidable", "unforeseeable", "no one could",
                    "nobody could", "reasonable care", "reasonable precaution",
                    "reasonably", "did everything", "diligen", "prudent", "innocent")


def flag_1a(summary, case_text):
    s = (summary or "").lower().replace("’", "'")
    c = case_text.lower()
    return [t for t in CONCLUSION_TERMS if t in s and t not in c]


def position(cond_cells):
    p0, n, c = (cond_cells.get(r) for r in ("P0", "N", "C"))
    if not (p0 and n and c) or any(x.get("void") for x in (p0, n, c)):
        return None, "condition missing or void on a role"
    bad = [r for r, x in (("P0", p0), ("N", n), ("C", c)) if x["gate_parse"] != "PASSED"]
    if bad:
        return None, "fewer than 7 of 10 parsed on " + ",".join(bad)
    if (n["blame_mass_0_3"] or 0) < N_MASS03_MIN:
        return None, f"N blame mass(0-3) {n['blame_mass_0_3']:.2f} < {N_MASS03_MIN}"
    if c["blame_mean"] == n["blame_mean"]:
        return None, "C equals N"
    return (p0["blame_mean"] - n["blame_mean"]) / (c["blame_mean"] - n["blame_mean"]), None


def boot_share(rows, key, arms, rng_seed=SEED):
    rng = random.Random(rng_seed)
    by = {a: [r for r in rows if r["arm"] == a] for a in arms}
    by = {a: v for a, v in by.items() if v}
    keys = list(by)
    out = []
    for _ in range(NBOOT):
        pick = [rng.choice(keys) for _ in keys]
        cs = [r for a in pick for r in by[a]]
        out.append(sum(key(r) for r in cs) / len(cs))
    out.sort()
    return [out[int(0.025 * NBOOT)], out[int(0.975 * NBOOT) - 1]]


def analyse(reads, frames):
    cells, excluded, flags_1a, codes_1b = [], [], [], []
    for arm, d in reads.items():
        if d.get("status") != "READ":
            excluded.append({"arm": arm, "reason": d.get("unread_reason", "not read")})
            continue
        for s in SCEN:
            roles = {r: d["cells"][f"{s}|{r}"] for r in ("P0", "N", "C")}
            for r, c in roles.items():
                text = frames["cells"][f"{s}|{r}"]["row_text"]
                fl = flag_1a(c["1A"]["text"], text)
                if fl:
                    flags_1a.append({"arm": arm, "scenario": s, "role": r, "terms": fl,
                                     "text": c["1A"]["text"]})
                codes_1b.append({"arm": arm, "scenario": s, "role": r,
                                 "code": classify_1b(c["1B"]["text"]),
                                 "interpretable": r != "N", "text": c["1B"]["text"]})
            row = {"arm": arm, "scenario": s,
                   "code_1b_P0": classify_1b(roles["P0"]["1B"]["text"])}
            why = {}
            for k in CONDS:
                pos, w = position({r: roles[r][k] for r in roles})
                row[f"pos_{k}"] = pos
                if w:
                    why[k] = w
            row["gated_all_four"] = not why
            if why:
                excluded.append({"arm": arm, "scenario": s, "reasons": why})
            cells.append(row)

    def block(arms):
        pop = [c for c in cells if c["arm"] in arms and c["gated_all_four"]]
        o = {"n_cells": len(pop), "n_arms": len({c["arm"] for c in pop}), "shares": {}}
        for k in CONDS:
            n_above = sum(c[f"pos_{k}"] > BAND for c in pop)
            o["shares"][k] = {
                "condition": COND_NAME[k], "above": n_above, "of": len(pop),
                "share": n_above / len(pop) if pop else None,
                "median_pos": st.median(c[f"pos_{k}"] for c in pop) if pop else None,
                "boot95": boot_share(pop, lambda r, k=k: r[f"pos_{k}"] > BAND, arms)
                if pop else None,
                # each condition's own gated population, beside the like-for-like one
                "own_gate": (lambda own: {"above": sum(c[f"pos_{k}"] > BAND for c in own),
                                          "of": len(own)})(
                    [c for c in cells if c["arm"] in arms and c[f"pos_{k}"] is not None])}
        # condition B by call 1B's conclusion on the target case
        o["2B_by_1B"] = {}
        for code in ("could not", "could", "unclear"):
            sub = [c for c in pop if c["code_1b_P0"] == code]
            o["2B_by_1B"][code] = {
                "n_cells": len(sub), "share_of_cells": len(sub) / len(pop) if pop else None,
                "above": sum(c["pos_2B"] > BAND for c in sub),
                "share_above": (sum(c["pos_2B"] > BAND for c in sub) / len(sub)
                                if sub else None)}
        return o

    main_ = block(TWELVE)
    sh = {k: main_["shares"][k]["share"] for k in CONDS}
    if None in sh.values():
        p1 = p2 = None
    else:
        p1 = {"rule": f"share(2B) - share(O) <= {BAND_EQ} and share(D) - share(2B) >= "
                      f"{BAND_GAP}",
              "share_2B_minus_O": sh["2B"] - sh["O"], "share_D_minus_2B": sh["D"] - sh["2B"],
              "verdict": "PASS" if (sh["2B"] - sh["O"] <= BAND_EQ
                                    and sh["D"] - sh["2B"] >= BAND_GAP) else "FAIL"}
        p2 = {"rule": f"|share(2A) - share(D)| <= {BAND_EQ}",
              "share_2A_minus_D": sh["2A"] - sh["D"],
              "verdict": "PASS" if abs(sh["2A"] - sh["D"]) <= BAND_EQ else "FAIL"}
    # the banked 69-cell population, re-read, beside the banked shares
    banked_pop = [c for c in cells if c["arm"] in TWELVE and c["gated_all_four"]
                  and not (c["scenario"] == "cheque"
                           and c["arm"] in ("deepseek", "kimi", "mistral24b"))]
    return {"run": "240", "twelve": main_, "check_deepseek_s": block(CHECK),
            "P239_1": p1, "P239_2": p2,
            "banked_reference": {k: {"above": a, "of": n, "share": a / n}
                                 for k, (a, n) in BANKED.items()},
            "rereads_on_banked_population": {
                k: {"above": sum(c[f"pos_{k}"] > BAND for c in banked_pop),
                    "of": len(banked_pop)} for k in CONDS},
            "flags_1a": flags_1a,
            "flags_1a_by_arm": {a: sum(f["arm"] == a for f in flags_1a) for a in reads},
            "codes_1b": codes_1b, "cells": cells, "excluded": excluded}


def to_register(res):
    P = "S4.1: serial_pipeline"
    t = res["twelve"]
    rows = []
    for k in CONDS:
        s = t["shares"][k]
        rows.append((f"{P}: share of careful-subject cells above 0.10, {s['condition']}, "
                     f"twelve models", f"{s['above']} of {s['of']}"))
    rows += [(f"{P}: serial_pipeline P1 verdict", res["P239_1"]["verdict"]),
             (f"{P}: serial_pipeline P2 verdict", res["P239_2"]["verdict"])]
    return rows


# ── THE DATABASE PATH (registration, 2026-10-20) ─────────────────────────────────
# Question R240_<condition>, so no BLAME query can pick these cells up. Only what
# analyse() reads is carried: blame_mean, blame_mass_0_3, the parse count and the void
# count. Call 1's texts are not ingested; no registered figure reads them.
QUESTION = {k: f"R240_{k}" for k in CONDS}


def cells_240(d):
    out = []
    for key, c in (d.get("cells") or {}).items():
        for k in CONDS:
            x = c[k]
            n_void = x["n_asked"] - x["n_parsed"]
            if k != "O":
                assert n_void == x["void"], (d.get("arm"), key, k)
            out.append({"family": c["scenario"], "role": c["role"], "question": QUESTION[k],
                        "ev": x["blame_mean"], "ev_all_draws": x["blame_mean"],
                        "ev_source": f"serial_pipeline, {k} ({COND_NAME[k]})",
                        "mass_0_3": x["blame_mass_0_3"], "n_draws": x["n_asked"],
                        "n_void": n_void, "p_yes": x.get("p_prevent_yes"),
                        "answer_mass": x.get("digit_mass"),
                        "void": 0 if x["gate_parse"] == "PASSED" else 1,
                        "prompt_sha256_16": x["prompt_sha256"][:16]})
    return out


def load_from_db(con):
    """The reads analyse() takes, rebuilt from the database's serial_pipeline cells. On O the
    artefact carries no void field, so none is reconstructed (position() reads it)."""
    reads = {}
    for aid, arm, env in con.execute("SELECT id, arm, env FROM artefacts WHERE run='serial_pipeline'"):
        e = json.loads(env or "{}")
        cells = {}
        for fam, role, q, ev, m03, nd, nv in con.execute(
                "SELECT family, role, question, ev, mass_0_3, n_draws, n_void FROM cells "
                "WHERE artefact_id=?", (aid,)):
            k = q[len("R240_"):]
            x = {"blame_mean": ev, "blame_mass_0_3": m03,
                 "gate_parse": "PASSED" if nd - nv >= PARSE_MIN else "FAILED"}
            if k != "O":
                x["void"] = nv
            # call 1's texts are filled in below from serial_pipeline_call1
            cells.setdefault(f"{fam}|{role}", {"1A": {"text": None},
                                               "1B": {"text": None}})[k] = x
        reads[arm] = {"status": e.get("status"), "cells": cells}
    # call 1's texts, from their own table (records the 1B breakdown is coded from)
    for arm, sc, role, t1a, t1b in con.execute(
            "SELECT arm, scenario, role, text_1a, text_1b FROM serial_pipeline_call1"):
        c = reads[arm]["cells"][f"{sc}|{role}"]
        c["1A"], c["1B"] = {"text": t1a}, {"text": t1b}
    return reads


def registered(res):
    """The six registered figures. Labelled ELEVEN models: Kimi-K3 is one of the twelve
    but contributes no cell (its provider served no logprobs on 2026-10-20). The result
    file's to_register says "twelve"; it is write-once and is left as banked."""
    P = "S4.1: serial_pipeline"
    t = res["twelve"]
    n_models = t["n_arms"]
    rows = []
    for k in CONDS:
        s = t["shares"][k]
        rows.append((f"{P}: share of careful-subject cells above 0.10, {s['condition']}, "
                     f"{NUM_WORD[n_models]} models (Kimi-K3 absent: no log-probabilities "
                     f"served)", f"{s['above']} of {s['of']}"))
    rows += [(f"{P}: serial_pipeline P1 verdict", res["P239_1"]["verdict"]),
             (f"{P}: serial_pipeline P2 verdict", res["P239_2"]["verdict"])]
    return rows


NUM_WORD = {10: "ten", 11: "eleven", 12: "twelve"}
LABEL = {"claude": "Claude Sonnet 5", "deepseek": "DeepSeek-V4.1", "gemma27b": "Gemma-3-27B",
         "gpt4o": "GPT-4o", "gpt6l_s": "gpt-6-luna", "gpt6s_s": "gpt-6-sol",
         "grok43_s": "grok-4.3", "haiku_s": "Claude Haiku 4.5", "kimi": "Kimi-K3",
         "llama70b": "Llama-3.3-70B", "mistral24b": "Mistral-Small-24B",
         "qwen80b": "Qwen3-Next-80B"}


def blamed_despite_could_not(res):
    """Per model: (cells coded "could not" with 2B above 0.10, the model's cells). "Most
    scenarios" is more than half of the model's cells in the population: Amendment 2 of
    PREREG_serial_pipeline_PIPELINE, ruled after the result and declared post-hoc."""
    out = {}
    for c in res["cells"]:
        if c["arm"] in TWELVE and c["gated_all_four"]:
            k, n = out.get(c["arm"], (0, 0))
            out[c["arm"]] = (k + (c["code_1b_P0"] == "could not" and c["pos_2B"] > BAND),
                             n + 1)
    return out


def registered_breakdown(res):
    """§4.1's figures on condition B by call 1B's conclusion (rule-coded, A0.10)."""
    P = "S4.1: serial_pipeline: conclusion forward"
    b = res["twelve"]["2B_by_1B"]
    n = res["twelve"]["n_cells"]
    per = blamed_despite_could_not(res)
    most = [LABEL[a] for a in TWELVE if a in per and per[a][0] * 2 > per[a][1]]
    rows = [
        (f"{P}: cells whose forwarded conclusion was 'could not' (call 1B, rule-coded)",
         f"{b['could not']['n_cells']} of {n}"),
        (f"{P}: of the 'could not' cells, blamed (position above 0.10)",
         f"{b['could not']['above']} of {b['could not']['n_cells']}"),
        (f"{P}: cells whose forwarded conclusion was 'could' (call 1B, rule-coded)",
         f"{b['could']['n_cells']} of {n}"),
        (f"{P}: of the 'could' cells, blamed (position above 0.10)",
         f"{b['could']['above']} of {b['could']['n_cells']}"),
        (f"{P}: models blaming in most scenarios (more than half of their cells) despite "
         f"a 'could not' conclusion", ", ".join(most))]
    assert len({k for k, _ in rows}) == len(rows), "duplicate location"
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    sys.path.insert(0, os.path.join(R, "scripts"))
    from read_serial_pipeline import load_frames, FRAMES, READ_ARMS
    frames = load_frames(f"{R}/{FRAMES}")
    reads = {}
    for arm in READ_ARMS:
        p = f"{R}/records/read__{arm}.json"
        if not os.path.exists(p):
            sys.exit(f"REFUSING: {os.path.relpath(p, R)} missing")
        reads[arm] = json.load(open(p))
    res = analyse(reads, frames)
    res["to_register"] = to_register(res)
    for k in CONDS:
        s = res["twelve"]["shares"][k]
        print(f"  {s['condition']:20s} {s['above']:3d} of {s['of']:3d}  "
              f"{s['share']:.3f}  boot95 {s['boot95']}")
    print("  serial_pipeline P1", res["P239_1"]["verdict"], " serial_pipeline P2", res["P239_2"]["verdict"])
    if a.dry:
        return 0
    if os.path.exists(DEST):
        sys.exit(f"write-once: {os.path.relpath(DEST, R)} exists")
    json.dump(res, open(DEST, "w"), indent=1, ensure_ascii=False)
    print(f"  -> {os.path.relpath(DEST, R)}")
    return 0


def selftest():
    ok = 0
    # 1B coding, both directions and the mixed case
    cases = {"Alaric could not reasonably have prevented this.": "could not",
             "No, he took every reasonable precaution.": "could not",
             "Alaric couldn’t have known about the hidden flaw.": "could not",
             "Yes, Alaric could have prevented this by checking the cable.": "could",
             "Alaric could reasonably have prevented this.": "could",
             "He should have inspected it more carefully.": "could",
             "It is hard to say.": "unclear",
             "He could not have seen the flaw, but he should have replaced it.": "unclear"}
    for t, want in cases.items():
        assert classify_1b(t) == want, (t, classify_1b(t), want)
    ok += 1; print(f"  ok  1B coding: {len(cases)} constructed sentences, both directions")
    case = "Alaric checked his ladder. A hidden flaw gave way. The neighbour fell."
    assert flag_1a("Alaric checked the ladder; a hidden flaw gave way.", case) == []
    assert flag_1a("He was not at fault: the flaw was unforeseeable.", case) == [
        "fault", "unforeseeable"]
    assert flag_1a("A hidden flaw gave way.", case + " Nobody was at fault.") == []
    ok += 1; print("  ok  1A flag: fires on conclusion vocabulary, silent on facts and on "
                   "words the case itself uses")

    def cc(mean, m03=1.0, parsed=10):
        return {"gate_parse": "PASSED" if parsed >= 7 else "FAILED", "blame_mean": mean,
                "blame_mass_0_3": m03}

    def fake_read(p0):        # p0: {cond: P0 mean}; N = 0, C = 8
        cells = {}
        for s in SCEN:
            for r in ("P0", "N", "C"):
                cells[f"{s}|{r}"] = {
                    "1A": {"text": "Alaric checked it."},
                    "1B": {"text": "Alaric could not reasonably have prevented this."},
                    **{k: cc({"P0": p0[k], "N": 0.0, "C": 8.0}[r]) for k in CONDS}}
        return {"status": "READ", "cells": cells}
    frames = {"cells": {f"{s}|{r}": {"row_text": "Alaric checked it."}
                        for s in SCEN for r in ("P0", "N", "C")}}
    # B clears (0.4 / 8 = 0.05), A blames (4 / 8 = 0.5), D blames, O clears
    reads = {a: fake_read({"2A": 4.0, "2B": 0.4, "D": 4.0, "O": 0.4})
             for a in TWELVE + CHECK}
    res = analyse(reads, frames)
    t = res["twelve"]["shares"]
    assert t["2A"]["share"] == 1 and t["2B"]["share"] == 0 and t["O"]["of"] == 72
    assert res["P239_1"]["verdict"] == "PASS" and res["P239_2"]["verdict"] == "PASS"
    assert res["twelve"]["2B_by_1B"]["could not"]["n_cells"] == 72
    ok += 1; print("  ok  opens: a clearing B and a blaming A pass both predictions")
    # the opposite world fails both
    reads = {a: fake_read({"2A": 0.4, "2B": 4.0, "D": 4.0, "O": 0.4})
             for a in TWELVE + CHECK}
    res = analyse(reads, frames)
    assert res["P239_1"]["verdict"] == "FAIL" and res["P239_2"]["verdict"] == "FAIL"
    ok += 1; print("  ok  refuses: a blaming B and a clearing A fail both predictions")
    # a gate failure in ONE condition removes the cell from all four (like for like)
    reads = {a: fake_read({"2A": 4.0, "2B": 0.4, "D": 4.0, "O": 0.4})
             for a in TWELVE + CHECK}
    reads["gpt4o"]["cells"]["ladder|N"]["2B"]["blame_mass_0_3"] = 0.5
    res = analyse(reads, frames)
    assert res["twelve"]["shares"]["D"]["of"] == 71
    assert res["twelve"]["shares"]["D"]["own_gate"]["of"] == 72
    ok += 1; print("  ok  a gate failure in one condition drops the cell from all four")
    print(f"selftest {ok}/5")
    return 0 if ok == 5 else 1


if __name__ == "__main__":
    sys.exit(main())

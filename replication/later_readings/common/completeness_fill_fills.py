#!/usr/bin/env python3
"""completeness_fill_fills.py : completeness_fill's readings (the v1.1 fill) into results.sqlite.

Imported by build_results_db.py (the excuse test) and duty_db.py (the duty test). Holds
no derived quantity: it copies the eval's own readings, as extracted from the Inspect logs
by `scripts/extract_completeness_fill_eval.py`, into the rows the banked readings use.

**WHERE A FILL GOES.** Each excuse fill sits in the banked artefact of the run whose gap it
fills, as `records/fill_targets.json` assigns it (`scripts/plan_completeness_fill_fills.py`,
computed against database 781e1e83), with `cells.read_later` and `cells.fill_key` saying
what it is. Gemini 3.1 Pro (C1) has no banked excuse reading and enters as an artefact of
its own, completeness_fill. No banked cell changes: a target already holding a value there is
refused by the planner, and an EMPTY banked cell there (H3) stays exactly as banked, with
the fill beside it.

**THE VOID RULE, AS THE EVAL APPLIED IT.** A cell the eval marked unusable (more than 10%
of its draws void, truncation included) or that parsed nothing is entered with `void = 1`
and NO value of any kind, `ev_all_draws` included: `cell_anchor_means` falls back to all
draws where a group has no reasoning-only value, and a void cell's all-draws mean reaching
an anchor through that door is exactly what the rule forbids. Its count is kept. A cell
not read at all (no log-probabilities, deferred) gets no `cells` row; it is listed in
`completeness_fill_fills` with its class and reason.
"""
import hashlib, json, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACT = "records/eval_extract.json"
TARGETS = "records/fill_targets.json"
AUDIT = "records/V1_1_COMPLETENESS_AUDIT_20261017/excuse_empty_classified.json"
AMENDMENT = "completeness_fill_amendment (2d61d1f1)"
AUDIT_SHA = "93225d9caaaed2ca299c4289fedaab4542bb27633704b32667fd7a2d16c34ef8"


class Refuse(Exception):
    pass


QWEN235B_CLOSED = "records/QWEN235B_CLOSED_20261017.json"


def final_class(c):
    """(class, reason) for a completeness_fill cell. Qwen3-235B's cells were planned as DEFERRED to a
    re-probe; that probe (2026-10-17) hit the same rate limit and the author closed the arm,
    so they are UNREAD, 'banked provider unavailable' (records/QWEN235B_CLOSED_20261017
    .json). Every other cell keeps the class the run's own records give it."""
    if c.get("class") == "UNREAD_DEFERRED" and c.get("arm") == "qwen235b":
        why = json.load(open(os.path.join(R, QWEN235B_CLOSED)))["reason"]
        return "UNREAD_PROVIDER_UNAVAILABLE", why
    return c.get("class"), c.get("reason")


def fsha(rel):
    return hashlib.sha256(open(os.path.join(R, rel), "rb").read()).hexdigest()


def load():
    ex = json.load(open(os.path.join(R, EXTRACT)))
    tg = json.load(open(os.path.join(R, TARGETS)))
    if tg["extract"]["sha256"] != fsha(EXTRACT):
        raise Refuse(f"{TARGETS} was planned on another extract")
    if tg["refused"]:
        raise Refuse(f"{TARGETS} carries {len(tg['refused'])} refused cell(s)")
    for rel, want in ex["sources"].items():
        if fsha(rel) != want:
            raise Refuse(f"{rel} does not hash to the sha the extract recorded")
    return ex, tg


def group_of(key, c, t, audit):
    arm = c["arm"]
    if arm == "gemini_pro":
        return "C1"
    scen, role, q, _f = c["sample_id"].split("|")
    g = audit.get((arm, scen, role, q))
    if g == "E-bicycle":
        return "H1"
    if g == "E-gpt6sr-cheque":
        return "H2"
    return "H3"


def ingest_excuse(con, rep):
    ex, tg = load()
    if fsha(AUDIT) != AUDIT_SHA:
        raise Refuse(f"{AUDIT} is not the pinned audit file")
    audit = {(a["arm"], a["scenario"], a["role"], a["question"]): a["grp"]
             for a in json.load(open(os.path.join(R, AUDIT))) if a["cls"] == "H"}
    cells, targets = ex["cells"], tg["targets"]
    own = {}                                  # arm -> artefact id (C1)
    n_in = n_void = n_unread = 0
    by_grp = {}
    for key in sorted(targets):
        c, t = cells[key], targets[key]
        if c["test"] != "excuse":
            continue
        grp = group_of(key, c, t, audit)
        by_grp[grp] = by_grp.get(grp, 0) + 1
        aid = None
        if t["own_artefact"]:
            if c["arm"] not in own:
                served = c.get("served") or [[None, None]]
                cur = con.execute(
                    "INSERT INTO artefacts(path,sha256,run,card,arm,delivery,readout,"
                    "model_id,revision,adapter_digest,env,banked_at,bank_name,bank_sha256,"
                    "adapter_family,superseded_by,enters_tables,load_seconds,"
                    "load_shared_with,log_run) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (EXTRACT, fsha(EXTRACT), "237", "api", c["arm"], "api",
                     c.get("readout"), (c.get("wire") or {}).get("model"), None, None,
                     json.dumps({"mode": ("logprob" if c.get("readout") == "logprob"
                                          else "sampled"),
                                 "wire": c.get("wire"), "wire_sha": c.get("wire_sha"),
                                 "read_later": f"2026-10-17, completeness_fill, {AMENDMENT} C1"}),
                     None, "due-care-eval banks/excuse_cases.jsonl (v1.0)", None,
                     "completeness_fill_eval", None, 1, None, None, "completeness_fill"))
                own[c["arm"]] = cur.lastrowid
            aid = own[c["arm"]]
        else:
            r_ = con.execute("SELECT id, sha256 FROM artefacts WHERE path=?",
                             (t["artefact"],)).fetchone()
            if not r_:
                raise Refuse(f"{key}: target {t['artefact']} is not in this build")
            if r_[1] != t["artefact_sha256"]:
                raise Refuse(f"{key}: target {t['artefact']} changed since it was planned")
            aid = r_[0]
        cid = None
        sitting = c["sitting"]
        if c["class"] in ("READ", "VOID_PARSE", "VOID_UNUSABLE"):
            s = c["score"]
            q = t["question"]
            usable = c["class"] == "READ"
            yn = q in ("REASONABLE", "CARELESS")
            cfg = s.get("reasoning_configured")
            # ── A VENDOR-DEFAULT WIRE THAT REASONED ON EVERY DRAW IS REASONING ON ───
            # The eval labels Gemini 3.1 Pro's C1 cells `off`: its wire sends no
            # reasoning field ("vendor_default") and its readout is sampled, so the eval
            # never forced reasoning on. But that model cannot be read without reasoning
            # and 2,240 of its 2,240 C1 draws reasoned; gemini_pro_fill's duty cells and §2.4
            # count it as a reasoning model. Left `off`, its readings entered the
            # reasoning-off pools of the introduction's percentages. The configuration
            # is set `on` only where the wire is the vendor default AND every draw of
            # the cell reasoned, so the reading is unchanged (all draws = reasoning-only).
            wire_r = (c.get("wire") or {}).get("reasoning")
            if (cfg == "off" and wire_r == "vendor_default" and s.get("n_draws")
                    and s.get("n_reasoning") == s.get("n_draws")):
                cfg = "on"
            ev = s.get("ev") if (usable and not yn) else None
            py = s.get("p_yes") if (usable and yn) else None
            probs = s.get("probs") if usable else None
            note = (f"read later, 2026-10-17, completeness_fill sitting {sitting}, under "
                    f"{AMENDMENT} group {grp}"
                    + ("" if usable else f"; NOT USED ({c['class']}: {c['reason']})"))
            cur = con.execute(
                "INSERT INTO cells(artefact_id,family,role,question,frame,ev,ev_sd,"
                "answer_mass,mass_0_3,mass_0_3_source,p_yes,probs,n_draws,n_reasoning,"
                "n_void,reasoning_share,thin,void,ev_reasoning_only,ev_all_draws,"
                "reasoning_configured,ev_source,reasoned_despite_off,answer_mass_source,"
                "reasoning_only_source,row_text_sha256,prompt_sha256_16,read_later,"
                "fill_key) VALUES(" + ",".join("?" * 29) + ")",
                (aid, t["family"], t["role"], q, None, ev,
                 s.get("ev_sd") if usable else None,
                 s.get("answer_mass"), s.get("mass_0_3") if usable else None,
                 (s.get("mass_0_3_source") if usable and s.get("mass_0_3") is not None
                  else None),
                 py, json.dumps(probs) if probs is not None else None,
                 s.get("n_draws") or s.get("draws_asked"), s.get("n_reasoning"),
                 s.get("n_void"), s.get("reasoning_share"), 0, 0 if usable else 1,
                 s.get("ev_reasoning_only") if (usable and not yn) else None,
                 s.get("ev_all_draws") if (usable and not yn) else None,
                 cfg, f"completeness_fill eval readout ({s.get('readout')})", 0,
                 (f"eval: {s.get('answer_mass_source')}" if s.get("answer_mass_source")
                  else "eval: 1 - void fraction"),
                 ("eval readout: reasoning draws only" if s.get("readout") == "reasoning"
                  else None),
                 (c.get("meta") or {}).get("text_sha256"), None, note, key))
            cid = cur.lastrowid
            if usable:
                n_in += 1
            else:
                n_void += 1
        else:
            n_unread += 1
        con.execute("INSERT INTO completeness_fill_fills VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (key, c["arm"], c["test"], grp, *final_class(c), sitting,
                     None if t["own_artefact"] else t["artefact"], t["run"],
                     json.dumps(t.get("empty_banked_cell_ids_at_781e1e83"))
                     if t.get("empty_banked_cell_ids_at_781e1e83") else None,
                     cid, c.get("log"), ex["sources"].get(c.get("log"))))
    con.commit()
    rep.append(f"  completeness_fill excuse fills ({EXTRACT}, {TARGETS}): {n_in} cells entered "
               f"and usable, {n_void} entered void (not used), {n_unread} not read "
               f"(listed in completeness_fill_fills only); by group {dict(sorted(by_grp.items()))}")
    return n_in, n_void, n_unread


# ── H7 AND H8: syllogism_duty, general_principle and reasoning_traces ON THE v1.1 FILL ───────────────────────────────
# reasoning-only on the H8 stratum (ruled 2026-10-17); H7 is identical in both records
SYLL = "records/syll_cells_ro.json"
H7_NOTE = ("read later, 2026-10-17, completeness_fill, under completeness_fill_amendment group H7: "
           "pooled with syllogism_duty")
H8_NOTE = ("read later, 2026-10-17, completeness_fill, under completeness_fill_amendment group H8: "
           "the reasoning stratum, reported beside syllogism_duty and never pooled with it")


def cells_233_shape(a, cfg):
    """syllogism_duty-shaped cell dicts (the fields ad_api_233 writes) from one arm's summaries in
    syll_cells.json. One definition for H7 (into run syllogism_duty's artefacts) and H8."""
    base = {"frame": None, "ev_reasoning_only": None, "reasoning_configured": cfg,
            "probs": None, "reasoning_share": None, "thin": 0, "row_text_sha256": None,
            "mass_0_3": None, "ev_sd": None}
    lp = a.get("readout_A") == "logprob"
    out = []

    def nr(c):
        s = c.get("share_reasoned")
        return None if s is None else round(s * c["n_asked"])
    for pr, c in sorted(a["A"].items()):
        npar = c["n_asked"] if lp else round(c["answer_mass"] * c["n_asked"])
        out.append(dict(base, family=f"duty_p{pr}", role="NONE", question="PRINCIPLE233",
                        ev=c["p_yes"], ev_all_draws=c["p_yes"],
                        ev_source=f"syllogism_duty A, {a.get('readout_A')} (completeness_fill)",
                        reasoned_despite_off=(nr(c) if cfg == "off" else None),
                        n_reasoning=nr(c), answer_mass=c["answer_mass"],
                        answer_mass_source=("mean raw yes+no probability in the top-k"
                                            if lp else "parsed over asked"),
                        p_yes=c["p_yes"], n_draws=c["n_asked"], n_void=c["n_asked"] - npar,
                        void=0 if c["gate"] == "PASSED" else 1,
                        prompt_sha256_16=c["prompt_sha256_16"]))
    for kind, q, src in (("R", "R233_BLAME", "syllogism_duty R, banked separate-case wire"),
                         ("T230", "T230_BLAME", "reasoning_traces trace re-read, banked bare wire")):
        for k, c in sorted(a[kind].items()):
            pr, leg = k.split("|")
            out.append(dict(base, family=f"duty_p{pr}", role=leg, question=q, ev=c["mean"],
                            ev_all_draws=c["mean"], ev_source=f"{src} (completeness_fill)",
                            reasoned_despite_off=None, n_reasoning=nr(c),
                            answer_mass=c["n_parsed"] / c["n_asked"],
                            answer_mass_source="digit parsed over asked", p_yes=None,
                            n_draws=c["n_asked"], n_void=c["n_asked"] - c["n_parsed"],
                            void=0 if c["n_parsed"] >= 0.7 * c["n_asked"] else 1,
                            prompt_sha256_16=c["prompt_sha256_16"]))
    for k, c in sorted(a["B"].items()):
        pr, leg = k.split("|")
        n = c["n_parsed"]
        common = dict(base, family=f"duty_p{pr}", role=leg,
                      ev_source="syllogism_duty B, sampled (completeness_fill)", answer_mass=n / c["n_asked"],
                      answer_mass_source="all three fields parsed over asked",
                      reasoned_despite_off=(nr(c) if cfg == "off" else None),
                      n_reasoning=nr(c), n_draws=c["n_asked"], n_void=c["n_asked"] - n,
                      void=0 if c["gate_parse"] == "PASSED" else 1,
                      prompt_sha256_16=c["prompt_sha256"][:16])
        out.append(dict(common, question="B233_BLAME", ev=c["blame_mean"],
                        ev_all_draws=c["blame_mean"], p_yes=None))
        for q, kk in (("B233_ROLE", "n_role_correct"), ("B233_PRINCIPLE", "n_principle_yes")):
            v = (c[kk] / n) if n else None
            out.append(dict(common, question=q, ev=v, ev_all_draws=v, p_yes=v))
    if a["G"]:
        import analyse_general_principle as A233G
        _, gc, _ = A233G.cells_233g({"G": a["G"]})
        for c in gc:
            c = dict(c, reasoning_configured=cfg, n_reasoning=None)
            out.append(c)
    return out


def _insert_cells(con, aid, cells, note, key_prefix):
    cols = ("family", "role", "question", "frame", "ev", "ev_sd", "answer_mass", "mass_0_3",
            "p_yes", "probs", "n_draws", "n_reasoning", "n_void", "reasoning_share", "thin",
            "void", "ev_reasoning_only", "ev_all_draws", "reasoning_configured", "ev_source",
            "reasoned_despite_off", "answer_mass_source", "row_text_sha256",
            "prompt_sha256_16")
    for c in cells:
        con.execute("INSERT INTO cells(artefact_id," + ",".join(cols) + ",read_later,"
                    "fill_key) VALUES(" + ",".join("?" * (len(cols) + 3)) + ")",
                    (aid, *[c.get(k) for k in cols], note,
                     f"{key_prefix}|{c['family']}|{c['role']}|{c['question']}"))


def ingest_syll(con, rep):
    """H7 into run syllogism_duty's banked artefacts; H8 as artefacts of their own (run 'reasoning_stratum')."""
    d = json.load(open(os.path.join(R, SYLL)))
    for rel, want in d["sources"].items():
        if fsha(rel) != want:
            raise Refuse(f"{rel} does not hash to the sha {SYLL} recorded")
    n7 = n8 = 0
    for arm, a in sorted(d["arms"].items()):
        if a["group"] == "H7":
            r_ = con.execute("SELECT id FROM artefacts WHERE run='syllogism_duty' AND arm=?",
                             (arm,)).fetchall()
            if len(r_) != 1:
                raise Refuse(f"H7 {arm}: {len(r_)} syllogism_duty artefacts (need one)")
            have = con.execute("SELECT COUNT(*) FROM cells WHERE artefact_id=? AND "
                               "family='duty_pprawns'", (r_[0][0],)).fetchone()[0]
            if have:
                raise Refuse(f"H7 {arm}: syllogism_duty already holds prawns cells")
            cs = cells_233_shape(a, "off")
            _insert_cells(con, r_[0][0], cs, H7_NOTE, f"completeness_fill|H7|{arm}")
            n7 += len(cs)
        else:
            rel = f"records/h8ro__{arm}.json"
            cur = con.execute(
                "INSERT INTO artefacts(path,sha256,run,card,arm,delivery,readout,model_id,"
                "revision,adapter_digest,env,banked_at,bank_name,bank_sha256,"
                "adapter_family,superseded_by,enters_tables,load_seconds,load_shared_with,"
                "log_run) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (rel, fsha(rel), "reasoning_stratum", "api", arm, "api", a.get("readout_A"),
                 (a.get("wire_AB") or {}).get("model"), None, None,
                 json.dumps({"status": "READ", "provider_served": a["provider_served"],
                             "served_model": a["served_model"], "wire_AB": a["wire_AB"],
                             "stratum": "H8, separate, never pooled",
                             "readout": d.get("readout_H8"),
                             "void_or_thin": {k: v for k, v in d["void_or_thin"].items()
                                              if k.startswith(arm + "|")},
                             "reasoning_traces_traces": d.get("reasoning_traces_traces")}),
                 None, "records/v11_frames.json",
                 fsha("records/v11_frames.json"), "completeness_fill_h8", None, 1, None, None,
                 "completeness_fill"))
            cs = cells_233_shape(a, "on")
            _insert_cells(con, cur.lastrowid, cs, H8_NOTE, f"completeness_fill|H8|{arm}")
            n8 += len(cs)
    con.commit()
    rep.append(f"  completeness_fill H7 (pooled into run syllogism_duty's artefacts): {n7} cells; H8 (run "
               f"'reasoning_stratum', a separate stratum, reasoning draws only): {n8} cells; "
               f"void or thin: {len(d['void_or_thin'])}; not read: "
               f"{len(d['unread'])} ({', '.join(sorted(d['unread']))})")
    return n7, n8

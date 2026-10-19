#!/usr/bin/env python3
"""build_completeness_fill_syll_cells.py : completeness_fill's H7 and H8 draws, summarised as syllogism_duty and general_principle
summarised theirs.

    .venv/bin/python scripts/build_completeness_fill_syll_cells.py

Writes records/syll_cells.json (write-once) from records/v11_syll__*.json.
Per arm it holds the same per-cell shapes `read_syllogism_duty.read_arm` and `read_general_principle` bank
(A: p_yes, answer_mass, gate, n_yes, principle_held; R: mean, n_parsed, values; B:
blame_mean, n_parsed, gate_parse, n_role_correct, n_principle_yes; G: counts, affirms,
gap), computed by the SAME rules with the readers' own constants imported, so that
`analyse_syllogism_duty` and `analyse_general_principle` can read the fill exactly as they read the banked
runs. The draws were parsed by the banked parsers at read time (read_v11_syllogism.py);
nothing is reparsed here.

A cell final_syll_cells.json classes as not read (deepseek and kimi's log-prob A and
R on prawns: the provider no longer returns log-probabilities) is omitted, with its
reason in `unread`.

**THE READOUT ON THE REASONING STRATUM (H8) IS ALL PARSED DRAWS**, as run syllogism_duty's reader
defines its cells, with the share of draws that reasoned recorded per cell beside it. The
amendment fixes the wire (each arm's banked reasoning wire) and not a reasoning-only
readout for these frames; if the author rules the reasoning-only reading for H8, the share
column says which cells it would change.
"""
import hashlib, json, os, statistics, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
from read_syllogism_duty import A_DRAWS, GATE_MASS, B_GATE            # noqa: E402
from read_general_principle import G3_GATE                               # noqa: E402

FINAL = "records/final_syll_cells.json"
FRAMES = "records/v11_frames.json"
# SYLL_READOUT=reasoning_only reads H8 from reasoning draws only (ruled 2026-10-17) and
# writes syll_cells_ro.json; the all-draws record syll_cells.json stays as
# written, and only the reasoning-only one is ingested
RO = os.environ.get("SYLL_READOUT") == "reasoning_only"
THIN = 5
OUT = os.environ.get("SYLL_OUT") or os.path.join(
    R, "records", "syll_cells_ro.json" if RO else "syll_cells.json")
EXPECTED_ROLE = {"PRO": "professional", "PRIV": "private"}


def fsha(rel):
    return hashlib.sha256(open(os.path.join(R, rel), "rb").read()).hexdigest()


def share_reasoned(draws):
    return (sum(1 for d in draws if d.get("reasoned")) / len(draws)) if draws else None


def summarise_A(c, logp):
    draws = c["draws"]
    if logp:
        ps = [d["p_yes"] for d in draws if d.get("p_yes") is not None]
        p = statistics.mean(ps) if ps else None
        mass = statistics.mean(d["mass"] for d in draws)
        n_yes, held = None, p is not None and p >= 0.90
    else:
        # run syllogism_duty's rule is 9 of 10 'yes', unparsed counting against; on an arm read at
        # 20 draws (gpt6s_r, its banked count) it is the same 90% share, 18 of 20
        ans = [d.get("answer") for d in draws]
        parsed = [a for a in ans if a is not None]
        p = (sum(a == "yes" for a in parsed) / len(parsed)) if parsed else None
        mass = len(parsed) / len(draws)
        n_yes = sum(a == "yes" for a in ans)
        held = n_yes >= 0.9 * len(draws)
    gate = "PASSED" if mass >= GATE_MASS else "FAILED"
    return {"p_yes": p, "answer_mass": mass, "gate": gate, "n_yes": n_yes,
            "n_asked": len(draws), "principle_held": bool(held and gate == "PASSED"),
            "share_reasoned": share_reasoned(draws), "prompt_sha256_16": c["prompt16"]}


def summarise_R(c):
    vals = [float(d["digit"]) for d in c["draws"] if d.get("digit") is not None]
    return {"n_asked": len(c["draws"]), "n_parsed": len(vals),
            "n_void": len(c["draws"]) - len(vals),
            "mean": statistics.mean(vals) if vals else None, "values": vals,
            "share_reasoned": share_reasoned(c["draws"]),
            "prompt_sha256_16": c["prompt16"]}


def summarise_B(c, leg):
    ok = [d["parsed"] for d in c["draws"] if d.get("parsed")]
    bl = [o["BLAME"] for o in ok]
    want = EXPECTED_ROLE[leg]
    return {"n_asked": len(c["draws"]), "n_parsed": len(ok),
            # 7 of 10 (B_GATE), the same 70% share at 20 draws
            "gate_parse": ("PASSED" if len(ok) >= B_GATE * len(c["draws"]) / A_DRAWS
                           else "FAILED"),
            "blame_mean": statistics.mean(bl) if bl else None, "blame_values": bl,
            "expected_role": want,
            "n_role_correct": sum(o["ROLE"] == want for o in ok),
            "n_principle_yes": sum(o["PRINCIPLE"] == "yes" for o in ok),
            "share_reasoned": share_reasoned(c["draws"]),
            "prompt_sha256": c["prompt16"]}


def summarise_G(key, c):
    draws = c["draws"]
    out = {"key": key, "n_asked": len(draws), "prompt_sha256": c["prompt16"],
           "share_reasoned": share_reasoned(draws)}
    if key.startswith("G1"):
        ans = [d.get("parsed") for d in draws]
        out["counts"] = {k: sum(a == k for a in ans) for k in ("more", "less", "equally")}
        out["counts"]["unparsed"] = sum(a is None for a in ans)
        out["affirms"] = out["counts"]["more"] >= 0.9 * len(draws)
    elif key == "G2":
        ans = [d.get("parsed") for d in draws]
        out["counts"] = {"yes": sum(a == "yes" for a in ans),
                         "no": sum(a == "no" for a in ans),
                         "unparsed": sum(a is None for a in ans)}
        out["affirms"] = out["counts"]["yes"] >= 0.9 * len(draws)
    else:
        ok = [d["parsed"] for d in draws if d.get("parsed")]
        out.update({"n_parsed": len(ok),
                    "gate": ("PASSED" if len(ok) >= G3_GATE * len(draws) / A_DRAWS
                             else "FAILED"),
                    "professional": [o["PROFESSIONAL"] for o in ok],
                    "amateur": [o["AMATEUR"] for o in ok],
                    "gap": (statistics.mean(o["PROFESSIONAL"] - o["AMATEUR"] for o in ok)
                            if ok else None)})
    return out


def main():
    if os.path.exists(OUT):
        sys.exit(f"REFUSED: {OUT} exists (write-once)")
    final = json.load(open(os.path.join(R, FINAL)))
    frames = json.load(open(os.path.join(R, FRAMES)))
    arms, unread, sources, voids = {}, {}, {}, {}
    for arm, fa in sorted(frames["arms"].items()):
        rel = f"records/v11_syll__{arm}.json"
        d = json.load(open(os.path.join(R, rel)))
        sources[rel] = fsha(rel)
        if d["frames_sha256"] != fsha(FRAMES):
            sys.exit(f"REFUSED: {rel} was read on another frames file")
        if len(d["models_served"]) != 1 or len(d["providers_served"]) != 1:
            sys.exit(f"REFUSED: {rel} has more than one served model or provider")
        logp = fa["AB"].get("readout") == "logprob"
        out = {"group": fa["group"], "readout_A": fa["AB"].get("readout"),
               "provider_served": d["providers_served"], "served_model": d["models_served"],
               "served_model_constant": True, "calls": d["calls"],
               "spent_usd": d["spent_usd"], "wire_AB": fa["AB"],
               "A": {}, "R": {}, "B": {}, "G": {}, "T230": {}}
        for k, c in sorted(d["cells"].items()):
            fc = final.get(f"{arm}|{k}")
            if fc is None:
                sys.exit(f"REFUSED: {arm}|{k} has no final class")
            if fc["class"] != "READ":
                unread[f"{arm}|{k}"] = fc["class"]
                continue
            kind = c["kind"]
            parts = c["key"].split("|")
            # ── H8 ON REASONING DRAWS ONLY (ruled 2026-10-17, per §3.4) ──────────────
            # A reasoning arm is read from the draws that returned reasoning text or
            # billed reasoning tokens; a cell with fewer than THIN (5) such draws is not
            # reported (the partial-reasoning rule), and a cell where the arm did not
            # reason at all is void with that reason. H7's arms are reasoning-off and
            # are read on all draws, as syllogism_duty read them.
            if RO and fa["group"] == "H8":
                rz = [x for x in c["draws"] if x.get("reasoned")]
                if len(rz) < THIN:
                    voids[f"{arm}|{k}"] = (
                        f"the arm did not reason on this cell (0 of {len(c['draws'])} "
                        f"draws reasoned)" if not rz else
                        f"THIN: {len(rz)} of {len(c['draws'])} draws reasoned, fewer "
                        f"than {THIN} (the partial-reasoning rule)")
                    continue
                c = dict(c, draws=rz, n_drawn=len(c["draws"]))
            if kind == "A":
                out["A"][parts[1][1:]] = summarise_A(c, logp)
            elif kind == "R":
                out["R"][f"{parts[1][1:]}|{parts[2]}"] = summarise_R(c)
            elif kind == "B":
                out["B"][f"{parts[1][1:]}|{parts[2]}"] = summarise_B(c, parts[2])
            elif kind == "G":
                out["G"][parts[1]] = summarise_G(parts[1], c)
            elif kind == "T230":
                out["T230"][f"{parts[1][1:]}|{parts[2]}"] = summarise_R(c)
            else:
                sys.exit(f"REFUSED: {arm}|{k}: kind {kind!r}")
        arms[arm] = out
    for k, v in final.items():
        if v["class"] != "READ" and k not in unread:
            sys.exit(f"REFUSED: {k} is {v['class']} in the final classes and not in an "
                     f"artefact")
    json.dump({"what": "completeness_fill's H7 and H8 cells, in run syllogism_duty's and general_principle's banked cell "
                       "shapes (scripts/build_completeness_fill_syll_cells.py)",
               "amendment": "records/completeness_fill_amendment_20261017.md",
               "frames": {FRAMES: fsha(FRAMES)}, "final_classes": {FINAL: fsha(FINAL)},
               "readout_H8": ("reasoning draws only (ruled 2026-10-17, per §3.4); a cell "
                              f"with fewer than {THIN} reasoning draws is not reported"
                              if RO else "all parsed draws"),
               "reasoning_traces_traces": "Gemini 3.1 Pro's reasoning_traces trace re-read: read, not coded "
                                "(ruled 2026-10-17); no figure",
               "sources": sources, "unread": unread, "void_or_thin": voids, "arms": arms},
              open(OUT, "w"), indent=1, sort_keys=True)
    n = sum(len(a[k]) for a in arms.values() for k in ("A", "R", "B", "G", "T230"))
    print(f"{len(arms)} arms, {n} cells, {len(unread)} unread, {len(voids)} void or thin "
          f"-> {os.path.relpath(OUT, R)}")
    for k, v in sorted(voids.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""build_v11_syllogism_frames.py : freeze the prompts and wires for the v1.1 fill's
groups read with working_repository's readers (completeness_fill_amendment, H7 and H8).

    python3 scripts/build_v11_syllogism_frames.py    # writes records/v11_frames.json

Write-once. Three readings, each keeping its banked run's structure:

  H7      syllogism_duty on prawns (A the principle, R the same-session bare re-read, B the
          structured prompt), on run syllogism_duty's 13 reasoning-off arms, pooled with syllogism_duty
  H8_233  syllogism_duty on the six reasoning arms and Gemini 3.1 Pro, all six pairs, a
          separate stratum
  H8_233G general_principle (five prompts, no case) on the same seven arms
  H8_230  reasoning_traces's trace re-read (bare BLAME, text kept) on Gemini 3.1 Pro, six pairs

PROMPTS. Pairs 1, 3, 4, 5, 7: A and B copied from frames.json (sha asserted) and
233G from general_principle_FRAMES_v2.json. Prawns: A from the approved role phrases inside run
syllogism_duty's frozen template; B from the families bank's careless cases (prawns_restaurant C is
the professional, prawns_home C the private person), a blank line, and run syllogism_duty's B
questions. R (and 230): the bare case through frames' blame frame, each prompt's
digest asserted equal to the ONE digest every banked bare call for that pair and leg
carries (duty_pairs and duty_hair_dye for pairs 1 to 7, the families runs for prawns).

WIRES.
  - A and B on the reasoning-off arms: run syllogism_duty's (read_prevention_paraphrase.ARMS; reasoning off;
    log-prob arms' B at 32 tokens).
  - A, B and 233G on the reasoning arms: each arm's banked duty_separate wire from
    due-care-eval models/, the registered setting.
  - R and 230: the wire on the banked calls behind each arm's preferred bare cell. That
    is read from the call log of the cell's own artefact, never from a label, and must be
    one wire.
The frozen readers send A and B with reasoning off on every arm, so on the reasoning
arms the reading is made by read_v11_syllogism.py, which changes only the wire.
"""
import glob, hashlib, json, os, re, sqlite3, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
DEST = f"{R}/records/v11_frames.json"
F233 = ("records/frames.json",
        "ae17c72b9a38e007be560eb9deb75079c90c2c53fe3e8387ded2945a7996df97")
F233G = ("records/general_principle_FRAMES_v2.json",
         "342ec134f524a27963e1be5fcf5f74d7a27f749e3ce97df393f6c7c108cc6df3")
F220 = ("records/frames.json",
        "ea34a1b8d0eed2c923b28e7a9df366bc11a543843c61d6a51ca0e2794ebeaa83")
FAMILIES = ("data/families_bank/moral__families__v1.jsonl",
            "cb77f3cb50528b089e978f8cec1069baf293f41d803d7a5e8ad00afd136918e6")
DB = ("results/results.sqlite",
      "781e1e836eeb45cef95cc55686c0828f4bc35791ebbd7c71713704becdf84a6b")
MODELS = os.path.expanduser("~/due-care-eval/models")
AMENDMENT = "records/completeness_fill_amendment_20261017.md"

OFF_ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
            "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")
ON_ARMS = ("deepseek_r", "gemini_r", "gpt6l_r", "gpt6s_r", "grok43_r", "haiku_r",
           "gemini_pro")
PAIRS5 = ("1", "3", "4", "5", "7")
PAIRS6 = ("prawns",) + PAIRS5
LEGS = ("PRO", "PRIV")
PRAWNS_A = ("a person serving prawns to his guests", "a chef")     # approved 2026-10-17
PRAWNS_A_BODY_SHA = "75ad914528a3175fce18d380a2f52b3a3e9dffad3c8800e781e829a34ab15ee3"

sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
fsha = lambda p: hashlib.sha256(open(f"{R}/{p}", "rb").read()).hexdigest()
mh = lambda system, user: sha(json.dumps([{"role": "system", "content": system},
                                          {"role": "user", "content": user}]))


def need(p, want):
    if fsha(p) != want:
        sys.exit(f"REFUSING: {p} does not hash to {want[:16]}")
    return json.load(open(f"{R}/{p}")) if p.endswith(".json") else None


def wire_of(r):
    return {"model": r["model"], "provider": r["provider_asked"],
            "max_tokens": r["max_tokens"], "want_logprobs": r["want_logprobs"],
            "top_k": r.get("top_k"), "temperature": r["temperature"],
            "reasoning": r.get("reasoning_on_the_wire")}


def calls(path, keep):
    out = []
    for line in open(path):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if keep(r.get("label", "")):
            out.append(r)
    return out


def bare_logs():
    """{(arm, pair, leg): [banked call records]} for each arm's PREFERRED bare cells."""
    con = sqlite3.connect(f"file:{R}/{DB[0]}?mode=ro", uri=True)
    rows = con.execute("SELECT arm, pair_id, artefact FROM duty_cells WHERE condition = "
                       "'bare' AND question = 'BLAME' AND preferred = 1 AND status = "
                       "'read' GROUP BY arm, pair_id, artefact").fetchall()
    out = {}
    for arm, pair, art in rows:
        if arm not in OFF_ARMS + ON_ARMS or pair not in PAIRS6:
            continue
        if pair == "prawns":
            if arm == "gemini_pro":
                logs = [f"{R}/runs/duty_gaps/logs/gemini_pro__prawns.jsonl"]
            else:
                stem = os.path.basename(art).split("__", 1)[1].removesuffix(".json")
                stem = stem.removesuffix("__RECOVERED_FROM_LOG")
                logs = [lp for lp in glob.glob(f"{R}/runs/<the readings filed from deployed_scenarios to deployed_added_models>/logs/or_{stem}.jsonl")
                        if "__C|BLAME" in open(lp).read()]
            if len(logs) != 1:
                sys.exit(f"REFUSING: {arm} prawns: {len(logs)} logs for {art}")
            for leg, fam in (("PRO", "prawns_restaurant"), ("PRIV", "prawns_home")):
                out[(arm, pair, leg)] = calls(
                    logs[0], lambda lab, f=fam: f"|{f}__C|BLAME" in lab)
        else:
            run = "228" if pair == "7" else "225"
            if arm == "gemini_pro":
                logs = [f"{R}/runs/duty_gaps/logs/gemini_pro__r{run}.jsonl"]
                pat = rf"later20261016\|gemini_pro\|run{run}\|sep\|p{pair}\|(PRO|PRIV)$"
            else:
                logs = glob.glob(f"{R}/runs/run{run}/logs/**/*.jsonl", recursive=True)
                pat = rf"run{run}\|{arm}\|sep\|p{pair}\|(PRO|PRIV)\|d\d+$"
            for leg in LEGS:
                recs = []
                for lp in logs:
                    recs += calls(lp, lambda lab, L=leg: bool(re.match(pat.replace(
                        "(PRO|PRIV)", L).rstrip("$") + (r"\|d\d+$" if arm == "gemini_pro"
                                                          else "$"), lab)))
                out[(arm, pair, leg)] = recs
    return out


def main():
    if os.path.exists(DEST):
        sys.exit(f"write-once: {os.path.relpath(DEST, R)} exists")
    f233, f233g, f220 = need(*F233), need(*F233G), need(*F220)
    need(*FAMILIES)
    if fsha(DB[0]) != DB[1]:
        sys.exit("REFUSING: the database is not 781e1e83")
    from read_prevention_paraphrase import ARMS as ARMS231
    fam = {(r["family"], r["role"]): r for r in
           (json.loads(l) for l in open(f"{R}/{FAMILIES[0]}") if l.strip())}
    case = {("prawns", "PRO"): fam[("prawns_restaurant", "C")],
            ("prawns", "PRIV"): fam[("prawns_home", "C")]}

    prompts = {}
    t = f233["texts"]
    for pr in PAIRS5:                                   # banked A and B, copied
        for k in [f"A|p{pr}"] + [f"B|p{pr}|{L}" for L in LEGS]:
            p = f233["prompts"][k]
            if mh(p["system"], p["user"]) != p["prompt_sha256"]:
                sys.exit(f"REFUSING: {k} in frames does not hash to its sha")
            prompts[k] = {"system": p["system"], "user": p["user"],
                          "prompt_sha256": p["prompt_sha256"], "source": F233[0]}
    a = t["A_template"]                                 # prawns A, approved
    user = a["head"] + PRAWNS_A[0] + a["mid"] + PRAWNS_A[1] + a["tail"]
    if sha(user) != PRAWNS_A_BODY_SHA:
        sys.exit("REFUSING: prawns A is not the approved text")
    prompts["A|pprawns"] = {"system": a["system"], "user": user,
                            "prompt_sha256": mh(a["system"], user), "source": AMENDMENT}
    for L in LEGS:                                      # prawns B, mechanical
        row = case[("prawns", L)]
        if sha(row["text"]) != row["sha256"]:
            sys.exit(f"REFUSING: prawns {L} case does not hash to its row")
        user = f"{row['text']}\n\n{t['B']['questions']}"
        prompts[f"B|pprawns|{L}"] = {"system": t["B"]["system"], "user": user,
                                      "prompt_sha256": mh(t["B"]["system"], user),
                                      "source": f"{FAMILIES[0]} + {F233[0]} texts.B"}
    for k, p in f233g["prompts"].items():               # 233G, copied
        if mh(p["system"], p["user"]) != p["prompt_sha256"]:
            sys.exit(f"REFUSING: {k} in general_principle_FRAMES_v2 does not hash to its sha")
        prompts[f"G|{k}"] = {"system": p["system"], "user": p["user"],
                             "prompt_sha256": p["prompt_sha256"], "source": F233G[0]}

    # R / 230: the bare case through the blame frame, digest = the banked calls' one digest
    blame = f220["blame"]
    duty = {}
    for pr in PAIRS5:
        b = f233["prompts"][f"B|p{pr}|PRO"]["user"].split("\n\n")[0]
        duty[(pr, "PRO")] = b
        duty[(pr, "PRIV")] = f233["prompts"][f"B|p{pr}|PRIV"]["user"].split("\n\n")[0]
    for L in LEGS:
        duty[("prawns", L)] = case[("prawns", L)]["text"]
    logs = bare_logs()
    wires = {}
    for pr in PAIRS6:
        for L in LEGS:
            user = blame["body"].format(item=duty[(pr, L)], agent="Alaric")
            h = mh(blame["system"], user)
            seen = {r.get("prompt_sha256_16") for arm in OFF_ARMS + ON_ARMS
                    for r in logs.get((arm, pr, L), [])}
            if seen != {h[:16]}:
                sys.exit(f"REFUSING: R p{pr} {L}: rendered {h[:16]}, banked calls carry "
                         f"{sorted(x for x in seen if x)}")
            prompts[f"R|p{pr}|{L}"] = {"system": blame["system"], "user": user,
                                        "prompt_sha256": h, "source": F220[0],
                                        "banked_prompt16": h[:16]}
    for (arm, pr, L), recs in sorted(logs.items()):
        ws = {json.dumps(wire_of(r), sort_keys=True) for r in recs}
        if len(ws) != 1:
            sys.exit(f"REFUSING: {arm} p{pr} {L}: {len(ws)} wires on its banked calls")
        wires.setdefault(arm, {})[f"R|p{pr}|{L}"] = json.loads(ws.pop())

    arms = {}
    for arm in OFF_ARMS:                                # H7: run syllogism_duty's own settings
        model, prov, served, readout, mt, top_k, _ = ARMS231[arm]
        arms[arm] = {"group": "H7", "pairs": ["prawns"], "draws": 10,
                     "AB": {"model": model, "provider": prov, "provider_served": served,
                            "readout": readout, "max_tokens": mt, "top_k": top_k,
                            "max_tokens_B": 32 if readout == "logprob" else mt,
                            "reasoning": {"enabled": False}},
                     "R": {k: v for k, v in wires[arm].items() if "pprawns" in k}}
    for arm in ON_ARMS:                                 # H8: the banked reasoning wire
        e = json.load(open(f"{MODELS}/{arm}.json"))["wire"]["duty_separate"]
        arms[arm] = {"group": "H8", "pairs": list(PAIRS6), "draws": e["draws"],
                     "AB": {**e["wire"], "readout": e["readout"], "wire_sha": e["wire_sha"]},
                     "R": wires[arm]}
    missing = [(a, k) for a, v in arms.items() for k in
               ([f"R|p{p}|{L}" for p in v["pairs"] for L in LEGS]) if k not in v["R"]]
    if missing:
        sys.exit(f"REFUSING: no banked bare wire for {missing[:6]}")
    out = {"_meta": {"what": __doc__.split("\n\n")[0].strip(), "amendment": AMENDMENT,
                     "inputs": {p: s for p, s in (F233, F233G, F220, FAMILIES, DB)},
                     "prompt_sha_construction": "sha256(json.dumps(messages))",
                     "cells": {"H7": 13 * 5, "H8_233": 7 * 30, "H8_233G": 7 * 5,
                               "H8_230": 12}},
           "prompts": prompts, "arms": arms}
    json.dump(out, open(DEST, "w"), indent=1)
    print(f"{len(prompts)} prompts, {len(arms)} arms -> {os.path.relpath(DEST, R)}")
    for arm, v in arms.items():
        r = sorted({(w["max_tokens"], json.dumps(w["reasoning"])) for w in v["R"].values()})
        print(f"  {arm:11s} {v['group']} AB {v['AB'].get('readout')} "
              f"mt {v['AB'].get('max_tokens')} R wires {r}")


if __name__ == "__main__":
    main()

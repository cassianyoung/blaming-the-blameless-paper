#!/usr/bin/env python3
"""verify_v11_syllogism_prompts.py : render every H7 and H8 prompt INDEPENDENTLY of the
frozen frames file and check it three ways, sending nothing.

    python3 scripts/verify_v11_syllogism_prompts.py

Each prompt is rebuilt from the banks and the banked builders' own text constants
(build_syllogism_duty_frames.py and build_general_principle_frames.py are imported for their strings, never
run), not copied from records/v11_frames.json. Then:

  1. it must hash to the frozen prompt in v11_frames.json;
  2. where the study already sent it, it must hash to the digest on the study's own calls:
     syllogism_duty and general_principle for A, B and G on pairs 1 to 7, duty_pairs and duty_hair_dye and the families
     runs for R;
  3. the reader (read_v11_syllogism.plan) must build the same messages for every arm.

Prints one line per prompt and a total, and exits non-zero on any mismatch.
"""
import glob, hashlib, importlib, json, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
mh = lambda system, user: sha(json.dumps([{"role": "system", "content": system},
                                          {"role": "user", "content": user}]))
jl = lambda p: [json.loads(l) for l in open(f"{R}/{p}") if l.strip()]


def logged(globs, pat):
    """{label key: set of 16-hex prompt digests} from banked call logs."""
    out = {}
    rx = re.compile(pat)
    for g in globs:
        for p in glob.glob(f"{R}/{g}", recursive=True):
            for line in open(p):
                if "prompt_sha256_16" not in line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                m = rx.match(d.get("label", ""))
                if m:
                    out.setdefault(m.group(1), set()).add(d["prompt_sha256_16"])
    return out


def main():
    B233 = importlib.import_module("build_syllogism_duty_frames")
    B233G = importlib.import_module("build_general_principle_frames")
    f220 = json.load(open(f"{R}/records/frames.json"))
    frames = json.load(open(f"{R}/records/v11_frames.json"))["prompts"]
    duty = {(str(r["pair"]), r["slot"]): r["text"]
            for r in jl("data/duty_bank/moral__duty__v1.jsonl")
            if r.get("kind") == "separate"}
    duty.update({(str(r["pair"]), r["slot"]): r["text"]
                 for r in jl("data/duty_bank/moral__duty228__v1.jsonl")
                 if r.get("kind") == "separate" and r.get("slot")})
    fam = {(r["family"], r["role"]): r["text"]
           for r in jl("data/families_bank/moral__families__v1.jsonl")}
    duty[("prawns", "PRO")] = fam[("prawns_restaurant", "C")]
    duty[("prawns", "PRIV")] = fam[("prawns_home", "C")]
    roles = dict(B233.ROLES)
    roles["prawns"] = ("a person serving prawns to his guests", "a chef")
    yn = "Answer with one word, Yes or No, and nothing else."

    mine = {}
    for pr in ("prawns", "1", "3", "4", "5", "7"):
        mine[f"A|p{pr}"] = mh(yn, B233.A_HEAD + roles[pr][0] + B233.A_MID + roles[pr][1]
                              + B233.A_TAIL)
        for L in ("PRO", "PRIV"):
            mine[f"B|p{pr}|{L}"] = mh(B233.B_SYSTEM, f"{duty[(pr, L)]}\n\n{B233.B_QUESTIONS}")
            mine[f"R|p{pr}|{L}"] = mh(f220["blame"]["system"], f220["blame"]["body"].format(
                item=duty[(pr, L)], agent="Alaric"))
    gtexts = {"G1": (B233G.G1_SYSTEM, B233G.G1_USER),
              "G1_AP": (B233G.G1_AP_SYSTEM, B233G.G1_AP_USER),
              "G2": (yn, B233G.G2_USER),
              "G3_PA": (B233G.G3_SYSTEM, B233G.G3_PA_USER),
              "G3_AP": (B233G.G3_SYSTEM, B233G.G3_AP_USER)}
    for k, (system, user) in gtexts.items():
        mine[f"G|{k}"] = mh(system, user)

    study = {}
    for k, v in logged(["runs/syllogism_duty/logs/**/*.jsonl"],
                       r"syllogism_duty\|[^|]+\|(A\|p\d|B\|p\d\|(?:PRO|PRIV))\|d\d+$").items():
        study[k] = v
    for k, v in logged(["runs/general_principle/logs/**/*.jsonl", "runs/general_principle/logs/**/*.jsonl"],
                       r"general_principle?\|[^|]+\|(G\d(?:_\w+)?)\|d\d+$").items():
        study[f"G|{k}"] = v
    for run in ("225", "228"):
        for k, v in logged([f"runs/run{run}/logs/**/*.jsonl"],
                           rf"run{run}\|[^|]+\|sep\|(p\d\|(?:PRO|PRIV))\|").items():
            study[f"R|{k}"] = v
    for leg, f in (("PRO", "prawns_restaurant"), ("PRIV", "prawns_home")):
        for k, v in logged(["runs/<the readings filed from deployed_scenarios to deployed_added_models>/logs/**/*.jsonl"],
                           rf"[^|]+\|({f}__C)\|BLAME$").items():
            study[f"R|pprawns|{leg}"] = v

    bad, n_study = [], 0
    for k in sorted(frames):
        ok_frozen = mine.get(k) == frames[k]["prompt_sha256"]
        seen = study.get(k)
        ok_study = None if not seen else seen == {mine[k][:16]}
        n_study += ok_study is True
        print(f"  {k:18s} frozen {'ok' if ok_frozen else 'MISMATCH'}   study "
              f"{'-' if ok_study is None else 'ok' if ok_study else 'MISMATCH ' + str(sorted(seen))}")
        if not ok_frozen or ok_study is False:
            bad.append(k)
    import read_v11_syllogism as RV
    fr = RV.load_frames()
    plan_bad = [(arm, x[1]) for arm in fr["arms"] for x in RV.plan(fr, arm)
                if x[4] != mine[x[1]][:16]]
    print(f"{len(frames)} prompts rendered independently: {len(frames) - len(bad)} equal the "
          f"frozen ones; {n_study} also equal the study's own sent digests; reader plans "
          f"agree for every arm: {not plan_bad}")
    if bad or plan_bad or set(mine) != set(frames):
        sys.exit(f"MISMATCH: {bad} {plan_bad[:5]} {sorted(set(mine) ^ set(frames))}")


if __name__ == "__main__":
    main()

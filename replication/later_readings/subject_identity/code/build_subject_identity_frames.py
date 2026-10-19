#!/usr/bin/env python3
"""build_subject_identity_frames.py : freeze subject_identity's texts, prompts, per-arm wire and price.

    python3 scripts/build_subject_identity_frames.py     # writes records/frames.json

Write-once. subject_identity re-reads seven banked cells with three subjects: Alaric (banked),
John (male) and Jane (female).

  excuse test  bicycle N, C, P0 and prawns_home N, C, P0
  duty test    the prawns pair's separate cases: prawns_restaurant C (careless chef) and
               prawns_home C (careless home cook, the same cell as the excuse test's C)

Blame question only, the banked `b1_blame_chat` frame from frames.json.

**THE TEXTS ARE BUILT MECHANICALLY AND CHECKED INDEPENDENTLY.** Build: replace "Alaric"
with the subject; for Jane also map he->she, him->her, his->her (capitalised forms too).
Check: a word-level alignment against the banked string, asserting the two strings have
the same number of words and that every differing word is the name or one of those
pronoun pairs. Alaric's text must be the banked string byte for byte, and Alaric's prompt
must hash to the prompt hash logged on the banked calls.

**THE WIRE IS FROZEN FROM THE LOGS FIGURE 1 READS, NOT TYPED.** For each arm and scenario
the source logs are named below (the runs `scenario_cells.role_source` names). The calls
in them whose prompt hash is a banked Alaric cell give the wire (model, provider asked and
served, temperature, max_tokens, top_k, log-probs, reasoning on the wire, endpoint) and the
draws per cell; every source file must agree on all of it, and every cell in a file must
carry the same draw count. The price is those calls' own mean billed cost.
"""
import collections, glob, hashlib, json, os, re, statistics, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import moral_frames as MF

DEST = f"{R}/records/frames.json"
BIKE = "records/excuse_bank.jsonl"
BIKE_SHA = "546dc93105fadf743385be513d6bb4895dcde8a16835c8da6be9b12dda59cdcb"
FAM = "data/families_bank/moral__families__v1.jsonl"
FAM_SHA = "cb77f3cb50528b089e978f8cec1069baf293f41d803d7a5e8ad00afd136918e6"
F220 = "records/frames.json"
F220_SHA = "ea34a1b8d0eed2c923b28e7a9df366bc11a543843c61d6a51ca0e2794ebeaa83"
BLAME_SHA = "d78642ff1ca5a8f2cc1fafa3ffe8b5cecde72c0d116d0110bb0d1a94b4ee4783"

SUBJECTS = {"Alaric": "male", "John": "male", "Jane": "female"}
FEMININE = {"he": "she", "He": "She", "him": "her", "Him": "Her", "his": "her", "His": "Her"}
# (scenario key used in prompts, bank, uid, role, which tests use it)
CELLS = (("bicycle", BIKE, "N", "N", "excuse"),
         ("bicycle", BIKE, "C", "C", "excuse"),
         ("bicycle", BIKE, "P0", "P0", "excuse"),
         ("prawns_home", FAM, "prawns_home__N", "N", "excuse"),
         ("prawns_home", FAM, "prawns_home__C", "C", "excuse+duty(home cook)"),
         ("prawns_home", FAM, "prawns_home__P0", "P0", "excuse"),
         ("prawns_restaurant", FAM, "prawns_restaurant__C", "C", "duty(chef)"))
# the wire group a cell is read under: the bicycle has its own banked pass per arm, both
# prawns scenarios come from the same families pass
GROUP = {"bicycle": "bicycle", "prawns_home": "prawns", "prawns_restaurant": "prawns"}

ARMS = ("claude", "deepseek", "deepseek_s", "gemma27b", "gpt4o", "gpt6l_s", "gpt6s_s",
        "grok43_s", "haiku_s", "kimi", "llama70b", "mistral24b", "qwen80b")
# Figure 1 panel B's sources (scenario_cells.role_source): bicycle deployed_bicycle_ladder/deployed_bicycle_rivals for most
# arms, 215 for gemma27b, 214 for mistral24b, deployed_scenarios's bicycle passes for the deployed
# sampled arms (haiku_s's filed as deployed_added_models), deployed_added_models for kimi; prawns from the families
# passes (deployed_scenarios; 222/222b/222c for grok43_s, gpt6l_s, gpt6s_s; 224 for haiku_s, kimi).
SOURCES = {
 "claude":     {"bicycle": ["deployed_bicycle_ladder/logs/l8_claude", "deployed_bicycle_rivals/logs/riv_claude"],
                "prawns": ["deployed_scenarios/logs/or_claude"]},
 "deepseek":   {"bicycle": ["deployed_bicycle_ladder/logs/l8_deepseek", "deployed_bicycle_rivals/logs/riv_deepseek"],
                "prawns": ["deployed_scenarios/logs/or_deepseek"]},
 "deepseek_s": {"bicycle": ["deployed_bicycle_ladder/logs/l8_deepseek_s", "deployed_bicycle_rivals/logs/riv_deepseek_s"],
                "prawns": ["deployed_scenarios/logs/or_deepseek_s"]},
 "gemma27b":   {"bicycle": ["deployed_bicycle_rivals/logs/riv_gemma27b"],
                "prawns": ["deployed_scenarios/logs/or_gemma27b"]},
 "gpt4o":      {"bicycle": ["deployed_bicycle_ladder/logs/l8_gpt4o", "deployed_bicycle_rivals/logs/riv_gpt4o"],
                "prawns": ["deployed_scenarios/logs/or_gpt4o"]},
 "gpt6l_s":    {"bicycle": ["deployed_scenarios/logs/or_gpt6l_s_bike"],
                "prawns": ["deployed_scenarios/logs/or_gpt6l_s"]},
 "gpt6s_s":    {"bicycle": ["deployed_scenarios/logs/or_gpt6s_s_bike"],
                "prawns": ["deployed_scenarios/logs/or_gpt6s_s"]},
 "grok43_s":   {"bicycle": ["deployed_scenarios/logs/or_grok43_s_bike"],
                "prawns": ["deployed_scenarios/logs/or_grok43_s"]},
 "haiku_s":    {"bicycle": ["deployed_scenarios/logs/or_haiku_s_bike"],
                "prawns": ["deployed_added_models/logs/or_haiku_s"]},
 "kimi":       {"bicycle": ["deployed_added_models/logs/kimi_bike"],
                "prawns": ["deployed_added_models/logs/or_kimi"]},
 "llama70b":   {"bicycle": ["deployed_bicycle_ladder/logs/l8_llama70b", "deployed_bicycle_rivals/logs/riv_llama70b"],
                "prawns": ["deployed_scenarios/logs/or_llama70b"]},
 "mistral24b": {"bicycle": ["deployed_bicycle_ladder/logs/l8_mistral24b"],
                "prawns": ["deployed_scenarios/logs/or_mistral24b"]},
 "qwen80b":    {"bicycle": ["deployed_bicycle_ladder/logs/l8_qwen80b", "deployed_bicycle_rivals/logs/riv_qwen80b"],
                "prawns": ["deployed_scenarios/logs/or_qwen80b"]},
}
WIRE_KEYS = ("model", "provider_asked", "provider_served", "temperature", "max_tokens",
             "top_k", "want_logprobs", "reasoning_on_the_wire", "endpoint", "mode")

sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
fsha = lambda p: hashlib.sha256(open(f"{R}/{p}", "rb").read()).hexdigest()
WORD = re.compile(r"\w+|[^\w\s]")


def msgs(system, user):
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def wire_sha(m):
    return sha(json.dumps(m))


def build_text(banked, subject):
    t = re.sub(r"\bAlaric\b", subject, banked)
    if SUBJECTS[subject] == "female":
        t = re.sub(r"\b(" + "|".join(FEMININE) + r")\b", lambda m: FEMININE[m.group(1)], t)
    return t


def check_text(banked, built, subject):
    """Independent of build_text: align word by word and list every difference. Returns
    the list of (banked word, built word) pairs that differ; refuses anything else."""
    a, b = WORD.findall(banked), WORD.findall(built)
    if len(a) != len(b):
        sys.exit(f"REFUSING: {subject}: word count {len(b)} != banked {len(a)}")
    if banked.split(" ") and len(banked.split(" ")) != len(built.split(" ")):
        sys.exit(f"REFUSING: {subject}: spacing differs from the banked string")
    allowed = {("Alaric", subject)}
    if SUBJECTS[subject] == "female":
        allowed |= set(FEMININE.items())
    diffs = [(x, y) for x, y in zip(a, b) if x != y]
    bad = [d for d in diffs if d not in allowed]
    if bad:
        sys.exit(f"REFUSING: {subject}: differences other than name and pronouns: {bad}")
    if subject != "Alaric" and ("Alaric", subject) not in diffs:
        sys.exit(f"REFUSING: {subject}: the name was not replaced")
    if SUBJECTS[subject] == "female" and re.search(r"\b(he|him|his|himself)\b", built, re.I):
        sys.exit(f"REFUSING: {subject}: a masculine pronoun survives: {built!r}")
    if re.search(r"\b(himself|herself)\b", banked):
        sys.exit("REFUSING: a reflexive pronoun is outside the instruction's mapping")
    return diffs


def scan_sources(alaric16):
    """Per arm and wire group: the banked wire, draws per cell and mean cost per call,
    from the named source logs, agreeing across files."""
    out = {}
    for arm in ARMS:
        out[arm] = {}
        for grp, files in SOURCES[arm].items():
            want = {h: k for h, k in alaric16.items() if GROUP[k[0]] == grp}
            wires, counts, costs, served_models = set(), [], [], set()
            for f in files:
                path = f"{R}/runs/{f}.jsonl"
                if not os.path.exists(path):
                    sys.exit(f"REFUSING: source log {f}.jsonl is missing")
                per = collections.Counter()
                for line in open(path):
                    if '"prompt_sha256_16"' not in line:
                        continue
                    x = json.loads(line)
                    k = want.get(x.get("prompt_sha256_16"))
                    if not k:
                        continue
                    per[k] += 1
                    wires.add(json.dumps({w: x.get(w) for w in WIRE_KEYS}, sort_keys=True))
                    costs.append(float(x.get("cost_usd") or 0.0))
                    served_models.add(x.get("served_model"))
                if set(per) != set(want.values()):
                    sys.exit(f"REFUSING: {arm} {grp}: {f} lacks banked calls for "
                             f"{sorted(set(want.values()) - set(per))}")
                if len(set(per.values())) != 1:
                    sys.exit(f"REFUSING: {arm} {grp}: {f} draw counts differ by cell {dict(per)}")
                counts.append(next(iter(per.values())))
            if len(wires) != 1:
                sys.exit(f"REFUSING: {arm} {grp}: source files disagree on the wire {wires}")
            if len(set(counts)) != 1:
                sys.exit(f"REFUSING: {arm} {grp}: source files disagree on draws {counts}")
            if len(served_models) != 1:
                sys.exit(f"REFUSING: {arm} {grp}: served model not constant {served_models}")
            out[arm][grp] = {"wire": json.loads(next(iter(wires))), "draws": counts[0],
                             "served_model_banked": next(iter(served_models)),
                             "source_logs": [f"runs/{f}.jsonl" for f in files],
                             "source_log_sha256": {f"runs/{f}.jsonl":
                                                   fsha(f"runs/{f}.jsonl") for f in files},
                             "cost_per_call_usd": statistics.mean(costs),
                             "cost_n_calls": len(costs)}
    return out


def main():
    if os.path.exists(DEST):
        sys.exit(f"write-once: {os.path.relpath(DEST, R)} exists")
    for p, want in ((BIKE, BIKE_SHA), (FAM, FAM_SHA), (F220, F220_SHA)):
        if fsha(p) != want:
            sys.exit(f"REFUSING: {p} sha {fsha(p)[:16]} != {want[:16]}")
    for s in SUBJECTS:
        if s not in MF.AGENT_NAMES:
            sys.exit(f"REFUSING: {s} is not an accepted agent name in moral_frames")
    f220 = json.load(open(f"{R}/{F220}"))
    body, system = f220["blame"]["body"], f220["blame"]["system"]
    if sha(body) != BLAME_SHA or f220["blame"]["sha256"] != BLAME_SHA:
        sys.exit("REFUSING: the blame body is not the banked b1_blame_chat")
    rows = {}
    for p in (BIKE, FAM):
        for l in open(f"{R}/{p}"):
            if l.strip():
                r = json.loads(l)
                rows[(p, r["uid"])] = r

    texts, prompts, alaric16 = {}, {}, {}
    for scen, bank, uid, role, used in CELLS:
        banked = rows[(bank, uid)]["text"]
        if sha(banked) != rows[(bank, uid)].get("text_sha256", sha(banked)):
            sys.exit(f"REFUSING: {uid} text does not hash to its banked sha")
        if banked.count("Alaric") != 1:
            sys.exit(f"REFUSING: {uid} names Alaric {banked.count('Alaric')} times")
        for subj in SUBJECTS:
            t = build_text(banked, subj)
            diffs = check_text(banked, t, subj)
            if MF.agent_of(t) != subj:
                sys.exit(f"REFUSING: agent_of({uid}, {subj}) -> {MF.agent_of(t)}")
            if subj == "Alaric" and t != banked:
                sys.exit(f"REFUSING: Alaric's {uid} is not the banked string")
            user = body.format(item=t, agent=subj)
            m = msgs(system, user)
            key = f"{scen}|{role}|{subj}"
            texts[key] = {"text": t, "text_sha256": sha(t), "banked_uid": uid,
                          "banked_text_sha256": sha(banked),
                          "differences_from_banked": diffs}
            prompts[key] = {"scenario": scen, "role": role, "subject": subj,
                            "gender": SUBJECTS[subj], "used_by": used, "system": system,
                            "user": user, "prompt_sha256": wire_sha(m)}
            if subj == "Alaric":
                alaric16[wire_sha(m)[:16]] = (scen, role)

    # Alaric's prompts must be the banked prompts on the wire: every source log carries
    # them (scan_sources refuses a file lacking any), so this is proved per arm there.
    src = scan_sources(alaric16)

    est, calls_total = {}, 0
    for arm in ARMS:
        n = 0
        cost = 0.0
        for scen, _, _, role, _ in CELLS:
            g = src[arm][GROUP[scen]]
            n += g["draws"] * len(SUBJECTS)
            cost += g["draws"] * len(SUBJECTS) * g["cost_per_call_usd"]
        est[arm] = {"calls": n, "usd": round(cost, 5)}
        calls_total += n

    out = {"_meta": {
              "run": "234", "built_from_commit": os.popen(
                  f"git -C {R} rev-parse HEAD").read().strip(),
              "inputs": {BIKE: BIKE_SHA, FAM: FAM_SHA, F220: F220_SHA},
              "blame_frame": {"id": f220["blame"]["id"], "sha256": BLAME_SHA,
                              "system": system, "body": body},
              "subjects": SUBJECTS, "feminine_map": FEMININE,
              "prompt_sha_construction": "sha256(json.dumps(messages)), as or_harness logs it",
              "n_prompts": len(prompts)},
           "texts": texts, "prompts": prompts,
           "arms": {a: {"bicycle": src[a]["bicycle"], "prawns": src[a]["prawns"]}
                    for a in ARMS},
           "estimate": {"per_arm": est, "calls": calls_total,
                        "usd": round(sum(e["usd"] for e in est.values()), 4),
                        "basis": "each arm's mean billed cost per call on the banked calls "
                                 "of these very prompts, times the calls subject_identity makes"}}
    json.dump(out, open(DEST, "w"), indent=1, ensure_ascii=False)
    print(f"{len(prompts)} prompts frozen -> {os.path.relpath(DEST, R)}")
    for k in ("bicycle|P0|Jane", "prawns_restaurant|C|Jane", "prawns_home|P0|John"):
        print(f"  {k}: {texts[k]['text']}  diffs {texts[k]['differences_from_banked']}")
    print(f"\n  {'arm':11s} {'bike wire':44s} {'d':>3s} {'prawns wire':40s} {'d':>3s} "
          f"{'calls':>5s} {'usd':>8s}")
    for a in ARMS:
        b, p = src[a]["bicycle"], src[a]["prawns"]
        fw = lambda w: (f"{w['provider_asked']}/{w['provider_served']} mt{w['max_tokens']} "
                        f"{'lp' if w['want_logprobs'] else 'samp'} "
                        f"{json.dumps(w['reasoning_on_the_wire'])}")
        print(f"  {a:11s} {fw(b['wire']):44s} {b['draws']:3d} {fw(p['wire']):40s} "
              f"{p['draws']:3d} {est[a]['calls']:5d} {est[a]['usd']:8.4f}")
    print(f"  total {calls_total} calls, ${out['estimate']['usd']:.4f}")


if __name__ == "__main__":
    main()

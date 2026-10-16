"""Checks that the study's model table and due-care-eval still render what the study sent.

    HF_HUB_OFFLINE=1 python replication/test_roster.py

1. Every entry in models/ loads and validates under the installed eval, and every model
   the reference values report has an entry.
2. The four reasoning arms read under the vendor's default are marked so.
3. Every excuse-test worksheet prompt the eval renders hashes to a prompt the study sent
   (reference/prompt_sha16.json).
4. For each instruct release whose tokenizer is in the local Hugging Face cache, every
   BLAME and REASONABLE chat prompt the eval renders, with the entry's template
   adjustments, hashes to a prompt the study sent. Skipped, by name, for releases not in
   the cache.

Needs due-care-eval installed; check 4 also needs its local extras.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["DUE_CARE_MODELS"] = os.path.join(HERE, "models")

from due_care import model_table as MT  # noqa: E402
from due_care.datasets import excuse_dataset  # noqa: E402

REF = json.load(open(os.path.join(HERE, "reference", "prompt_sha16.json")))
VALUES = json.load(open(os.path.join(HERE, "reference", "paper_values.json")))
failed = []


def check(label, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + ("" if ok else f"  {detail}"))
    if not ok:
        failed.append(label)


def sha16(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


MT.MODELS = os.path.join(HERE, "models")
entries = MT.all_entries()
check(f"every entry in models/ validates ({len(entries)} entries)",
      all(MT.validate(e) for e in entries.values()))
arms = {k.split("|")[0] for k in VALUES["excuse"]} | {k.split("|")[0] for k in VALUES["duty"]}
check(f"every model the reference values report has an entry ({len(arms)} models)",
      arms <= set(entries), sorted(arms - set(entries)))

vds = {k for k, e in entries.items() if e["kind"] == "api" and e.get("vendor_default")}
check(f"the vendor-default arms are marked ({', '.join(sorted(vds))})",
      vds >= {"gemini_r", "gpt6l_r", "gpt6s_r", "grok43_r"})

ws = {sha16(s.input) for s in excuse_dataset("worksheet")}
check(f"every excuse-test worksheet prompt is one the study sent ({len(ws)} prompts)",
      ws <= set(REF["worksheet"]), sorted(ws - set(REF["worksheet"]))[:4])

try:
    from transformers import AutoTokenizer

    import harness.local as L
except Exception as e:
    print(f"  SKIP  chat prompts on local releases  (local extras not installed: {e})")
else:
    ds = [s for s in excuse_dataset("chat") if s.metadata["question"] in ("BLAME", "REASONABLE")]
    for arm in sorted(REF["local_chat"]):
        e = entries[arm]
        ck = e["checkpoint"]
        try:
            tok = AutoTokenizer.from_pretrained(ck["repo"], revision=ck["revision"],
                                                local_files_only=True)
        except Exception:
            print(f"  SKIP  {arm}: rendered chat prompts equal the study's  (tokenizer not cached)")
            continue
        fold = (e.get("template") or {}).get("system_role") == "fold"
        want = set(REF["local_chat"][arm])
        miss = []
        for s in ds:
            if fold:
                p, _ = L.render_chat(tok, None, ((s.metadata["system"] or "") + "\n\n"
                                                 + s.input).strip())
            else:
                p, _ = L.render_chat(tok, s.metadata["system"], s.input)
            if sha16(p) not in want:
                miss.append(s.id)
        check(f"{arm}: all {len(ds)} BLAME and REASONABLE chat prompts hash to prompts the "
              f"study sent", not miss, miss[:4])

print(f"test_roster: {'all checks passed' if not failed else f'{len(failed)} failed'}")
sys.exit(1 if failed else 0)

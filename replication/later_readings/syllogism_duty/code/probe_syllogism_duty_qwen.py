#!/usr/bin/env python3
"""probe_syllogism_duty_qwen.py : can the two unread Qwen arms be read again on their banked providers?

    .venv/bin/python scripts/probe_syllogism_duty_qwen.py

Probe only (instruction of 2026-10-13). ONE HTTP attempt per arm, no retries and no other
provider: a reading on a different provider would put the arm's new cells and its banked
cells on two serving configurations. The wire is the banked duty-read wire, taken from
runs/duty_pairs/logs/p_fast4/read.jsonl and runs/duty_hair_dye/logs/g_E/read.jsonl (chat endpoint,
temperature 1, reasoning disabled, logprobs with top 20, provider pinned with fallbacks
off), except max_tokens 2 for a two-token answer as instructed.

Before the call, the arm's endpoint listing on OpenRouter is read, so "is the model id
listed by the provider" is answered from the listing and not inferred from the call.

Write-once: records/qwen_probe_20261013.json, and the raw exchange beside it in
runs/syllogism_duty/logs/qwen_probe_20261013.jsonl.
"""
import hashlib, json, os, sys, time, urllib.error, urllib.request

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{R}/scripts")
from or_harness import BASE, key  # noqa: E402

DEST = f"{R}/records/qwen_probe_20261013.json"
LOG = f"{R}/runs/syllogism_duty/logs/qwen_probe_20261013.jsonl"
ARMS = {"qwen235b": ("qwen/qwen3-235b-a22b-2507", "GMICloud"),
        "qwen30b": ("qwen/qwen3-30b-a3b-instruct-2507", "StreamLake")}
MSGS = [{"role": "system", "content": "Answer with a single digit."},
        {"role": "user", "content": "How many legs does a cat have?"}]


def listing(model, k):
    req = urllib.request.Request(f"{BASE}/models/{model}/endpoints",
                                 headers={"Authorization": f"Bearer {k}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)["data"]
    except urllib.error.HTTPError as e:
        return {"http_status": e.code, "error": e.read()[:400].decode(errors="replace")}
    return {"http_status": 200, "endpoints": [
        {"provider_name": e.get("provider_name"), "status": e.get("status"),
         "quantization": e.get("quantization"),
         "logprobs": "logprobs" in (e.get("supported_parameters") or [])}
        for e in d.get("endpoints", [])]}


def call(model, provider, k):
    payload = {"model": model, "temperature": 1.0, "max_tokens": 2,
               "provider": {"order": [provider], "allow_fallbacks": False},
               "usage": {"include": True}, "logprobs": True, "top_logprobs": 20,
               "reasoning": {"enabled": False}, "messages": MSGS}
    req = urllib.request.Request(BASE + "/chat/completions",
                                 data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {k}",
                                          "Content-Type": "application/json",
                                          "X-Title": "register-split-discovery"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            status, body = r.status, json.load(r)
    except urllib.error.HTTPError as e:
        status, body = e.code, {"error_body": e.read()[:1000].decode(errors="replace")}
    except Exception as e:
        status, body = None, {"exception": repr(e)}
    return payload, status, body, round(time.time() - t0, 2)


def main():
    for p in (DEST, LOG):
        if os.path.exists(p):
            sys.exit(f"write-once: {os.path.relpath(p, R)} exists")
    k = key()
    out = {"what": "syllogism_duty: probe of the two unread Qwen arms on their banked providers",
           "instruction": "probe only; one minimal call each; no other provider",
           "prompt_sha256": hashlib.sha256(json.dumps(MSGS).encode()).hexdigest(),
           "arms": {}}
    log = open(LOG, "x")
    for arm, (model, prov) in ARMS.items():
        lst = listing(model, k)
        payload, status, body, lat = call(model, prov, k)
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        log.write(json.dumps({"ts": ts, "arm": arm, "payload": payload, "http_status": status,
                              "body": body, "latency_s": lat, "listing": lst}) + "\n")
        log.flush()
        ch = (body.get("choices") or [{}])[0] if isinstance(body, dict) else {}
        text = ((ch.get("message") or {}).get("content") or "") if ch else ""
        top = (((ch.get("logprobs") or {}).get("content") or [{}])[0].get("top_logprobs")
               if ch.get("logprobs") else None) or []
        names = [e["provider_name"] for e in lst.get("endpoints", [])]
        out["arms"][arm] = {
            "ts_utc": ts, "model": model, "provider_asked": prov,
            "http_status": status,
            "provider_served": body.get("provider") if isinstance(body, dict) else None,
            "served_model": body.get("model") if isinstance(body, dict) else None,
            "answer_text": text, "logprobs_returned": bool(top),
            "top_tokens": [t.get("token") for t in top[:5]],
            "usable_answer": status == 200 and body.get("provider") == prov
                             and text.strip() != "" and bool(top),
            "error": None if status == 200 else (body.get("error_body") or
                                                 body.get("exception")),
            "cost_usd": (body.get("usage") or {}).get("cost") if isinstance(body, dict) else None,
            "provider_listed": prov in names, "listing_http_status": lst["http_status"],
            "providers_listed": lst.get("endpoints", lst.get("error"))}
        print(f"{arm}: HTTP {status}; listed={prov in names}; "
              f"usable={out['arms'][arm]['usable_answer']}; text={text!r}; "
              f"err={str(out['arms'][arm]['error'])[:200]}")
        print(f"   providers listed: {names}")
    json.dump(out, open(DEST, "x"), indent=1)
    print(f"-> {os.path.relpath(DEST, R)}")


if __name__ == "__main__":
    main()

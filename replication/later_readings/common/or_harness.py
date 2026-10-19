#!/usr/bin/env python3
"""or_harness.py : the OpenRouter harness for the act/agent gap errand.

Discovery. No registration, no thresholds, no branch labels. What it guarantees
is the cheap discipline: every call fully logged, no coercion of a refusal into a
digit, the provider pinned, and the readout mode recorded per cell.

═══════════════════════════════════════════════════════════════════════════════
WHAT THIS HARNESS KNOWS THAT THE POD DID NOT HAVE TO

**THE POD SCORED TEN DIGIT LOGITS; AN API RETURNS A TOP-K.** `rate_material.py`
reads the full next-token distribution and takes the expected value over exactly
the tokens "0" to "9". OpenRouter returns `top_logprobs`, at most 20 entries by
probability. If a digit falls outside that list its mass is missing, so this
records `digits_seen` and `digit_mass` on every call and the expected value is
renormalised over what was returned. A cell whose digit mass is far from 1.0 is
not the pod's quantity and must not be compared with it as though it were.

**THE ANSWER TOKEN MAY CARRY A LEADING SPACE.** The frame ends `Rating:` and the
pod's `answer_prefix` is a space, so the model's next token is usually ` 7` and
not `7`. Both spellings are scored, keyed by `tok.strip()`, and the raw token
strings are logged so the split can be inspected.

**TEMPERATURE IS 1.0 ON PURPOSE.** Some providers scale reported logprobs by
temperature; at 0 that would collapse the distribution the pod measured. The
sampled token is discarded, only the distribution is read.

**NO FALLBACK ROUTING.** `provider.allow_fallbacks` is false and the order is a
single name. OpenRouter's served provider is read back off every response and a
pass asserts it constant; a cell whose provider changed mid-pass is two cells
wearing one name (the earlier-run aliasing lesson, in a routing layer).
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

BASE = "https://openrouter.ai/api/v1"
TOKEN_FILE = os.path.expanduser("~/.cache/openrouter/openrouter_token")
TIMEOUT = 120
ATTEMPTS = 6


def key():
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k and os.path.exists(TOKEN_FILE):
        k = open(TOKEN_FILE).read().strip()
    if not k:
        raise SystemExit("REFUSING: no OpenRouter key")
    return k


def _post(path, payload, k):
    body = json.dumps(payload).encode()
    last = None
    for a in range(ATTEMPTS):
        try:
            req = urllib.request.Request(
                BASE + path, data=body,
                headers={"Authorization": f"Bearer {k}",
                         "Content-Type": "application/json",
                         "X-Title": "register-split-discovery"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:400].decode(errors='replace')}"
            if e.code in (400, 401, 402, 403, 404):
                break
            if e.code == 429:
                # Upstream shared-pool rate limits need a real wait, not a retry
                # cadence sized for a transient error. SWITCHING PROVIDER IS NOT
                # THE FIX: a model's cells must all come from one provider, which
                # is the earlier-run aliasing rule applied to a routing layer.
                time.sleep(8 * (a + 1) ** 2)
                continue
        except Exception as e:
            last = repr(e)
        time.sleep(1.5 * (a + 1))
    raise RuntimeError(f"OpenRouter call failed after {ATTEMPTS}: {last}")


def endpoints(model, k=None):
    k = k or key()
    req = urllib.request.Request(f"{BASE}/models/{model}/endpoints",
                                 headers={"Authorization": f"Bearer {k}"})
    d = json.load(urllib.request.urlopen(req, timeout=60))["data"]
    out = []
    for e in d["endpoints"]:
        sp = e.get("supported_parameters") or []
        out.append({"provider": e.get("provider_name"),
                    "quantization": e.get("quantization"),
                    "context": e.get("context_length"),
                    "prompt_usd_per_m": float(e.get("pricing", {}).get("prompt", 0)) * 1e6,
                    "completion_usd_per_m": float(e.get("pricing", {}).get("completion", 0)) * 1e6,
                    "logprobs": "logprobs" in sp,
                    "top_logprobs": "top_logprobs" in sp,
                    "seed": "seed" in sp})
    return out


def reasoned(rec):
    """Did this draw reason? TEXT OR BILLED TOKENS, and the OR is the whole point.

    THE RULE WAS ALWAYS "DID IT REASON". IT WAS IMPLEMENTED AS "DID IT RETURN REASONING
    TEXT", AND THOSE COME APART BY VENDOR. Measured across every log in this repo on
    2026-10-04:

        gemini-3.8-flash   1880 draws, text 1700, tokens 1880   <- 180 missed
        or_gemini_duty_N     60 draws, text    3, tokens   60   <- 57 missed
        gpt-6-luna           80 draws, text   71, tokens   80   <- 9 missed
        grok-4.3            482 draws, text  481, tokens  482   <- ONE draw
        deepseek-v4.1       1945 draws, agree on every one
        claude-haiku-4.5    321 draws, text  161, tokens  161   <- agree
        every non-reasoning arm: zero on both

    So Gemini and OpenAI bill reasoning tokens without always returning the text, and a
    text-only predicate reported REAL REASONING AS ABSENT. That is the step-C genus: an
    instrument reading zero on a form of the thing it cannot see, where zero is
    indistinguishable from a true absence and nothing in the numbers looks wrong.

    THIS IS THE SAME RULE MORE ACCURATELY IMPLEMENTED, NOT A DIFFERENT RULE, and that is
    checkable rather than asserted: DeepSeek and both Anthropic arms classify IDENTICALLY
    under both predicates, so every banked reading on them is unchanged.

    **GROK IS 481 OF 482, NOT 482 OF 482, AND THE FIRST VERSION OF THIS DOCSTRING SAID
    "AGREE".** The exception is one draw, `grok43_r|ladder__P2_other|CARELESS`, with 190
    reasoning tokens and no text. It sits in deployed_scenarios's pass 6, which was LAUNCHED BEFORE
    this patch and therefore ran under the text-only predicate. It cannot flip that
    cell's THIN status, which needs fewer than five reasoning draws against the nine or
    ten that cell has, but the artefact is recomputed from its log rather than trusted,
    because "it cannot matter" is an argument and the log is a measurement.
    """
    if (rec.get("reasoning_text_len") or 0) > 0:
        return True
    ctd = ((rec.get("usage") or {}).get("completion_tokens_details") or {})
    return (ctd.get("reasoning_tokens") or 0) > 0


def digit_ev(top):
    """Expected value over digit tokens in a top-k list. Returns (ev, mass, seen)."""
    p = {}
    for t in top:
        s = (t.get("token") or "").strip()
        # `str.isdigit()` is TRUE for '\u2080' and other unicode digit forms, and
        # `int()` then raises. A 70B call returned a subscript zero in its top-k and
        # killed the pass mid-cell. Membership in the ten ASCII digits is the test
        # that matches what is being scored.
        if s in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
            p[int(s)] = p.get(int(s), 0.0) + pow(2.718281828459045, t["logprob"])
    mass = sum(p.values())
    if not p:
        return None, 0.0, []
    ev = sum(d * q for d, q in p.items()) / mass
    return ev, mass, sorted(p)


class Harness:
    def __init__(self, logpath, cap_usd=5.0):
        self.k = key()
        self.log = open(logpath, "a")
        self.cap = cap_usd
        self.spent = 0.0
        self.calls = 0

    def _record(self, rec):
        self.log.write(json.dumps(rec) + "\n")
        self.log.flush()

    def rate(self, model, provider, prompt=None, messages=None, mode="completion",
             temperature=1.0, max_tokens=1, top_k=20, label="", reasoning_off=False,
             want_logprobs=True, reasoning=None):
        """One digit reading. Returns a fully logged record; never coerces.

        `want_logprobs=False` omits the logprobs fields entirely, for endpoints that
        serve no logprobs at all (Anthropic, Gemini) and reject or ignore the request.
        The record then carries `ev: None` and the caller must parse `raw_text`.
        `reasoning` passes an explicit spec (e.g. {"effort": "low"}) and OVERRIDES
        `reasoning_off`; what went on the wire is logged either way.
        """
        if self.spent > self.cap:
            raise SystemExit(f"REFUSING: spend cap ${self.cap} reached "
                             f"(${self.spent:.3f} over {self.calls} calls)")
        payload = {"model": model, "temperature": temperature,
                   "max_tokens": max_tokens,
                   "provider": {"order": [provider], "allow_fallbacks": False},
                   "usage": {"include": True}}
        if want_logprobs:
            payload["logprobs"] = True
            payload["top_logprobs"] = top_k
        # Qwen3 and other hybrids think unless told not to, and a think block eats
        # the answer budget before a digit appears (an earlier run, and this errand's own
        # qwen3_instruct cell at 96 tokens). The value that went on the wire is
        # logged, so a provider that ignores it is visible rather than assumed.
        if reasoning is not None:
            payload["reasoning"] = reasoning
        elif reasoning_off:
            payload["reasoning"] = {"enabled": False}
        if mode == "completion":
            payload["prompt"] = prompt
            path = "/completions"
        else:
            payload["messages"] = messages
            path = "/chat/completions"
        t0 = time.time()
        r = _post(path, payload, self.k)
        ch = (r.get("choices") or [{}])[0]
        text = (ch.get("text") if mode == "completion"
                else (ch.get("message") or {}).get("content")) or ""
        # BOUND ONCE, so the length field and the void_reason read the same value.
        # My first version of the void_reason referred to a name that did not exist
        # in this scope and would have raised at runtime on the first blank call.
        reasoning_text = ((ch.get("message") or {}).get("reasoning") or "") or ""
        lp = ch.get("logprobs") or {}
        content = lp.get("content") or []
        top = (content[0].get("top_logprobs") if content else None) or []
        # some providers put completion logprobs under top_logprobs directly
        if not top and isinstance(lp.get("top_logprobs"), list) and lp["top_logprobs"]:
            first = lp["top_logprobs"][0]
            if isinstance(first, dict):
                top = [{"token": t, "logprob": v} for t, v in first.items()]
        ev, mass, seen = digit_ev(top)
        usage = r.get("usage") or {}
        cost = float(usage.get("cost") or 0.0)
        self.spent += cost
        self.calls += 1
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "label": label, "model": model, "provider_asked": provider,
               "provider_served": r.get("provider"), "served_model": r.get("model"),
               "endpoint": path, "mode": mode, "temperature": temperature,
               "max_tokens": max_tokens,
               "top_k": top_k if want_logprobs else None,
               "want_logprobs": want_logprobs,
               "reasoning_on_the_wire": payload.get("reasoning"),
               "reasoning_off_on_the_wire": payload.get("reasoning"),
               "reasoning_text_len": len(reasoning_text),
               # ── THE FULL TEXT OF EVERY CALL IS KEPT (ruled 2026-10-12) ───────
               # Until this date only the reasoning text's LENGTH was logged and the
               # answer was cut at 400 characters, so no duty-test trace survived
               # and the §4.3 trace test could not be run without new reads.
               # `reasoning_details` is kept verbatim because its entry types
               # (reasoning.text / reasoning.summary / reasoning.encrypted) are the
               # only record of whether a trace is the model's text or a provider
               # summary; `reasoning_kinds` lists them so that is countable.
               "reasoning_text": reasoning_text,
               "reasoning_details": (ch.get("message") or {}).get("reasoning_details"),
               "reasoning_kinds": sorted({d.get("type") for d in
                                          ((ch.get("message") or {})
                                           .get("reasoning_details") or [])
                                          if isinstance(d, dict) and d.get("type")}),
               "answer_text": text,
               "prompt_sha256_16": hashlib.sha256(
                   (prompt if mode == "completion"
                    else json.dumps(messages)).encode()).hexdigest()[:16],
               "raw_text": text[:400],
               "top_tokens": [{"t": t.get("token"), "lp": round(t.get("logprob", 0), 4)}
                              for t in top[:20]],
               "digits_seen": seen, "digit_mass": round(mass, 6),
               "ev": None if ev is None else round(ev, 6),
               "void": ev is None,
               # ── A void_reason MUST NAME THE ACTUAL CAUSE ─────────────────
               # It said "logprobs not requested" on 858 of 858 blank calls in run
               # deployed_scenarios' Gemini attempt 1. That is TRUE of the sampled path and is not
               # the cause: the cause was an EMPTY completion, because the reasoning
               # consumed the output budget at max_tokens 8. A field that names one
               # cause for every failure is how a bug reads as a benign property of
               # the specimen, which is exactly what deployed_bicycle_rivals banked as gemini's
               # "void rate". The empty-completion case is now named first and the
               # reasoning length is part of the reason, so the symptom and its
               # cause are in the same string.
               "void_reason": None if ev is not None else
                              (("empty completion with "
                                f"{len(reasoning_text or '')} chars of reasoning text; "
                                f"max_tokens={max_tokens}. The reasoning consumed the "
                                f"output budget and the answer never appeared."
                                if (reasoning_text or "") else
                                f"empty completion, no reasoning text; "
                                f"max_tokens={max_tokens}")
                               if not (text or "").strip() else
                               ("logprobs not requested" if not want_logprobs
                                else ("no logprobs returned" if not top
                                      else "no digit token in the top-k"))),
               "usage": usage, "cost_usd": cost,
               "latency_s": round(time.time() - t0, 2)}
        self._record(rec)
        return rec

# Later readings

The readings made after the evaluation's tests were fixed, which due-care-eval (release
v1.1) does not run: the reasoning traces, the prevention re-read, the practical syllogism,
the duty syllogism, the general principle, the subject's name, the reasoning stratum of
the completeness fill, the serial pipeline, and the question word. Each folder holds what is needed to see exactly what was asked and
what came back:

| folder | what it reads |
|---|---|
| [`reasoning_traces/`](reasoning_traces/) | the reasoning text of the six reasoning models on the duty test's separate cases, coded for whether it raises the professional comparison |
| [`prevention_paraphrase/`](prevention_paraphrase/) | the prevention and carelessness questions re-read in their original wording (the syllogism's particular premise), and rewordings of the prevention question (not reported) |
| [`practical_syllogism/`](practical_syllogism/) | the universal premise asked with no case, and fact, rule and verdict asked in one answer |
| [`syllogism_duty/`](syllogism_duty/) | the duty test's role and principle asked first, and the convention per named pair |
| [`general_principle/`](general_principle/) | the convention asked in the abstract, in both orders |
| [`subject_identity/`](subject_identity/) | the excuse and duty cases re-read with the subject named Alaric, John or Jane |
| [`reasoning_stratum/`](reasoning_stratum/) | the duty syllogism, the general principle and the reasoning-trace re-read on the reasoning models, reported as a separate stratum |
| [`serial_pipeline/`](serial_pipeline/) | a connected pipeline: a first call's factual summary or prevention conclusion passed into the scoring call, beside the direct verdict and the one answer |
| [`question_word/`](question_word/) | the base models' worksheet re-read with "at fault" and "responsible" in place of "blame" (exploratory, read on local weights: per-cell results in place of calls) |

## In each folder

| path | contents |
|---|---|
| `README.md` | what the reading tests, its pre-registration, what was read, where it is reported |
| `prompts/` | the frozen prompts as banked before the reading; `built_prompts.json` where a reading rebuilt its prompts from the banks instead; `prompt_check.json` |
| `code/` | the reading's reader and analysis scripts, as run |
| `readings/calls/` | every call the reading made, as logged: one JSON line per call, with the model and provider asked for and served, the wire settings, the answer (and the reasoning text where the provider returned it), log-probabilities where requested, usage, and the prompt's hash |
| `readings/records/` | the per-model read records and the reading's result files, as the analysis wrote them |

`common/` holds the modules several readers import (the call harness, the frames, the
exclusion rules, and for question_word the local reader, the model loader and the
database's derivations).

## The prompt check

Every call logs `prompt_sha256_16`: the first 16 hex digits of the SHA-256 of the chat
messages as JSON (`hashlib.sha256(json.dumps(messages).encode())`). `prompt_check.json`
hashes every frozen prompt the same way and counts the calls carrying it; a call matching
no frozen prompt is listed by its label. Where a reading rebuilt its prompts from the banks,
the reader's own check against the study's earlier calls is recorded beside each prompt.
To repeat the check:

```python
import hashlib, json
def h16(p):
    m = ([{"role": "system", "content": p["system"]}] if p.get("system") else []) \
        + [{"role": "user", "content": p["user"]}]
    return hashlib.sha256(json.dumps(m).encode()).hexdigest()[:16]
```

## Names and paths

Every file here is in the public names used throughout this repository: run numbers are
replaced by the reading names above (`../README.md`), and runs outside this paper are
called "an earlier run". The code is otherwise as run. Its paths are the working
repository's: `records/<file>` is this folder's `prompts/<file>` or
`readings/records/<file>`, `runs/<reading>/logs/` is `readings/calls/`, and `scripts/` is
`code/` here or `../common/`. A few scripts read the study's results database, which is not
distributed; the values they used are in `../../data/` and `../../paper_numbers.csv`.
Re-running a reader calls paid models through OpenRouter and needs a key. Five glob
patterns that selected the working repository's runs by number are shown as an
angle-bracketed description of what they selected (`runs/<the deployed and duty
readings>/...`).

## What is withheld

Where a provider returned its reasoning encrypted, or signed, the call log keeps the
reasoning text or summary it returned and withholds the opaque value: each `data` of an
encrypted reasoning item and each `signature` of a reasoning item is replaced by
`[withheld: encrypted or signed by the provider; <n> characters; sha256 <16 hex digits>]`.
3,119 values are withheld, all in the calls of the reasoning models (2,649 encrypted
reasoning items, 470 signatures). A line with nothing withheld is exactly the line logged.

## Pre-registrations

In [`../../pre-registration/`](../../pre-registration/): `reasoning_traces.md`,
`prevention_paraphrase.md`, `practical_syllogism.md`, `syllogism_duty.md`,
`general_principle.md`, `subject_identity.md` and `completeness_fill_amendment.md`.

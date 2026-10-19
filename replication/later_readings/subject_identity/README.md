# subject_identity

Every case in the paper names one male subject, Alaric. This reading asks whether the
result is a property of him: it re-reads the excuse test's bicycle and prawns-at-home cases
(blameless N, careless C and careful target P0) and the prawns duty pair's two separate
cases with the subject renamed John or Jane, a matched pair differing only in gender. Only
the name changes, and for Jane the pronouns; Alaric is re-read alongside so every
comparison is like for like.

## Pre-registration

`../../../pre-registration/subject_identity.md`, banked 2026-10-13 before any call of this
reading (the reading ran the same day).

- **Amendment 0** (2026-10-13, before any call): freezes the 21 prompts (seven banked cells
  by three subjects) with a word-by-word check that only the name and pronouns differ; makes
  the name match whole-word; fixes each model's wire and draw count from the banked logs;
  defines the readings, the gate, how the two scenarios combine, the statistics (percentile
  bootstrap over models, 10,000 resamples, seed 234), the rotated reading order and the
  call count.
- **Ruling** (2026-10-13, before any call): adopts Amendment 0's defaults on the gate (no
  deliberate-case clause, since that case is not read; duty cells gated on answer mass
  alone; raw top-k digit mass reported, not gated) and on combining scenarios (each model's
  difference is the mean over its gated scenarios).

## What was read

- **Models:** 13 reasoning-off readouts of 12 models: Claude Sonnet 5, Claude Haiku 4.5,
  DeepSeek-V4.1-Flash (log-prob, and sampled as a check), Gemma-3-27B-IT, GPT-4o,
  gpt-6-luna, gpt-6-sol, grok-4.3, Kimi-K3, Llama-3.3-70B-Instruct, Mistral-Small-3.2-24B,
  Qwen3-Next-80B. Each on its banked provider and wire; served model constant on every
  readout. The two Qwen readouts of the related readings were not included (not readable
  on their banked provider).
- **Names:** Alaric (banked), John, Jane.
- **Cases:** bicycle N, C, P0; prawns at home N, C, P0 (C is also the duty test's home
  cook); prawns at a restaurant C (the duty test's chef). Seven cells, Blame question only.
- **Draws:** the banked count per cell and subject: 10, or 20 on the bicycle for Claude
  Sonnet 5, DeepSeek-V4.1-Flash (sampled) and Mistral-Small-3.2-24B.
- **Calls:** 3,000 (210 or 300 per readout). All 13 readouts read, none unread; every cell
  parsed in full (no void draws); no draw reasoned; no scenario or duty gap excluded by the
  gate. Answer mass 1.0 on every cell; lowest raw top-k digit mass on a log-prob cell 0.987.
- **Drift:** the same-sitting Alaric matches his banked positions to a median 0.014 over
  26 model-scenario cells.
- **Counting:** the banked result pooled the 13 readouts. The paper's figures follow its
  one-readout-per-model rule (DeepSeek-V4.1-Flash sampled is a check and is not counted),
  so they are over 12 models. The verdicts are the same under both counts.

| Pre-registered test | Banked, 13 readouts | Paper, 12 models |
|---|---|---|
| P1, John − Alaric position | −0.017 [−0.087, +0.033] holds | −0.036 [−0.100, +0.024] |
| P1, Jane − Alaric position | −0.080 [−0.158, −0.038] **fails** | −0.098 [−0.181, −0.043] **fails** |
| P2, Jane − John position | −0.053 [−0.080, −0.025], gender effect reported | −0.056 [−0.106, −0.028], gender effect reported; lower on 10 of 12 |
| P3, duty gap, Jane − Alaric | −0.016 [−0.423, +0.400] | −0.006 [−0.311, +0.450] |

Medians over models with 95% bootstrap intervals. The Jane − John drop is mainly on prawns
at home (−0.066 [−0.121, −0.018]); on the bicycle the interval includes zero (−0.047
[−0.145, +0.032]).

## Where it is reported

- **§4.1, "Across scenarios and names":** renaming the subject John shifts his position
  by < 0.04 (paper_numbers 510, 511); renaming him Jane still produces blame but lowers it
  by 0.06 (529, 530) on 10 of 12 models (589), primarily on home food preparation
  (prawns_home 536, 537; bicycle 533, 534). The P1 verdict FAILS (516; Jane − Alaric 513,
  514) and the per-scenario name-alone figures (517 to 528) are registered under §4.1, as
  are the duty-gap differences and per-subject gaps (539 to 556), models read "12 of 12"
  (557) and exclusions 0 (558).
- **§3 (Methods):** the paragraph introducing the four further readings names this one.
- **§5:** the gender-effect flag "yes" (532) is registered with location §5.
- **§6 (Limitations), "Short, constructed cases":** a single named subject, re-read with a
  male and a female name; the model counts (512 and the other "arms" ids) are registered
  for §4.1 and §6.
- No table or figure draws on this reading.

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 2 | frozen prompts and the prompt check: `frames.json`, `prompt_check.json` |
| `code/` | 3 | reader and analysis scripts, as run: `analyse_subject_identity.py`, `build_subject_identity_frames.py`, `read_subject_identity.py` |
| `readings/calls/` | 13 | every call, one JSON line each; 3,000 lines: `or_claude.jsonl`, `or_deepseek.jsonl`, `or_deepseek_s.jsonl`, `or_gemma27b.jsonl`, `or_gpt4o.jsonl`, `or_gpt6l_s.jsonl`, `or_gpt6s_s.jsonl`, `or_grok43_s.jsonl`, `or_haiku_s.jsonl`, `or_kimi.jsonl`, `or_llama70b.jsonl`, `or_mistral24b.jsonl`, ... |
| `readings/records/` | 15 | per-model read records and result files: `RECOUNT_subject_identity.json`, `result.json`, `subject_identity_READ__claude.json`, `subject_identity_READ__deepseek.json`, `subject_identity_READ__deepseek_s.json`, `subject_identity_READ__gemma27b.json`, `subject_identity_READ__gpt4o.json`, `subject_identity_READ__gpt6l_s.json`, `subject_identity_READ__gpt6s_s.json`, `subject_identity_READ__grok43_s.json`, `subject_identity_READ__haiku_s.json`, `subject_identity_READ__kimi.json`, ... |

## Prompt check

3,000 of 3,000 calls in `readings/calls/` carry the hash of a prompt in `prompts/`; 21 of 21 distinct prompts were sent in this folder's calls. Per prompt: `prompts/prompt_check.json`; the method: `../README.md`.

# syllogism_duty

This reading asks whether the remedy that clears the careful subject (setting out the
premises before the verdict, in one answer) also restores the slack a private person is
owed on the duty pairs. Each model is asked the comparative principle with no case
(condition A), and then, on each separate case, to state the subject's role, the
principle and the blame in one structured answer (condition B). The gap B produces
between the professional and the private person is compared with the gap the model gives
when the cases are judged bare and alone (condition R) and with the slack it states when
the two cases are shown side by side.

## Pre-registration

`../../../pre-registration/syllogism_duty.md`, banked on 2026-10-13 before any call of
this reading; the reads were made the same day.

- **Amendment 0** (before any call): fixes what the instruction left open: the A texts
  per pair, the B system message, the 13 arms, the parse gates, the operational rules
  for syllogism_duty.P1 to P4, and the frozen comparands. The ruling that follows it
  keeps the defaults and adds condition R, a same-session re-read of the bare separate
  cases, as the comparand the pass is led on.
- **Amendment G** (before any of its calls): the principle asked in general, with no
  trade named; read as the general_principle reading under its own pre-registration.
- **Amendment S, the split (syllogism_duty_split)**: a reporting rule for the 52
  non-driving cells judged alone: the headline is the count whose separate gap is zero or
  below; a positive gap within the wording floor is unresolved, never a failure. Made
  after the split was computed, and it says so; it changes no measurement.
- **Amendment T, the shortfall (syllogism_duty_shortfall)**: a cell falls short when its
  stated gap minus its separate gap exceeds the combined wording and draw floor. Made
  before the count was computed.
- **The prawns fill** (the completeness_fill reading) read this reading's conditions on
  the prawns pair and pooled them with the other pairs. It is governed by
  `../../../pre-registration/completeness_fill_amendment.md`.

## What was read

- **Models**: 13 reasoning-off arms, which are 12 models: Claude Sonnet 5 (`claude`),
  DeepSeek-V4.1-Flash with its log-probability readout (`deepseek`) and its sampled
  readout (`deepseek_s`), Gemma-3-27B-IT (`gemma27b`), GPT-4o (`gpt4o`), gpt-6-luna
  (`gpt6l_s`), gpt-6-sol (`gpt6s_s`), grok-4.3 (`grok43_s`), Claude Haiku 4.5
  (`haiku_s`), Kimi-K3 (`kimi`), Llama-3.3-70B-Instruct (`llama70b`),
  Mistral-Small-3.2-24B (`mistral24b`) and Qwen3-Next-80B (`qwen80b`). Every arm was read
  on its banked provider with the served model constant. Qwen3-235B and Qwen3-30B were
  not read: neither could be served by its banked provider, and a single probe of each
  returned no answer.
- **Pairs**: electrical (pair 1), gas (3), childcare (4), driving (5) and hair dye (7),
  both legs (professional and private) of each. Driving is the control for A, where
  "no" is defensible.
- **Conditions**:
  - **A**, the principle with no case: "is a [private person] held to a less strict
    standard than a [professional] who does it for payment?", yes or no; 10 calls per
    pair per arm, read by log-probability on seven arms and sampled on six (650 calls).
  - **B**, the structured prompt: the separate case, then ROLE, PRINCIPLE and BLAME
    (0 to 9) in one answer; 10 draws per leg, sampled at temperature 1 on every arm
    (1,300 calls).
  - **R**, the bare separate cases re-read in the same session: 10 draws per leg
    (1,300 calls). R re-sent the duty test's own banked prompts: before any call, each R
    prompt was asserted to hash to the prompt logged on the banked duty_pairs or
    duty_hair_dye call for that pair and leg.
- **Cells and calls**: 65 arm-pair cells, 3,250 calls. No A cell failed its gate, every
  B and R leg passed its parse gate, no R draw was void, and 1 of 1,300 B draws did not
  parse (grok-4.3, driving).
- **The prawns fill, pooled**: the same 13 arms on the prawns pair, 65 cells (A, both R
  legs and both B legs per arm), 59 read and 6 unread: A and R on `deepseek` and `kimi`,
  whose provider no longer returned log-probabilities. One comparand is missing
  (grok-4.3's side-by-side prawns reading, void on 40% of its draws). The paper's figures
  pool prawns with the five pairs and count each model once, DeepSeek-V4.1-Flash by its
  log-probability readout: 12 models, 1,440 pooled B draws asked, 1,439 parsed.
- **Reasoning arms**: the completeness fill also read these conditions on seven
  reasoning arms; that stratum is reported separately and never pooled.

## Where it is reported

- **§3.3** (method, the paragraph on the duty-test questions) describes the case-free
  convention question and the one-answer prompt.
- **§4.2**, the paragraph on the pairs judged alone: 28 of 48 cells fall short under the
  shortfall rule (id 507), 26 of 40 excluding the models whose wording floor exceeds their
  stated slack (id 509), and 6 of 48 give zero slack (id 501, the split, registered under
  general_principle); only 2 of 10 models affirm the convention on all five named pairs
  other than driving (id 449; 39 of 58 cells, id 450; driving 8 of 12, id 451).
- **§4.2**, the paragraph on the structured prompt: the role is identified every time
  (1,439 of 1,439, id 452), yet 7 of 12 models fall more than three tenths short of their
  stated slack (id 466; the stated convention on the same arms and pairs, more than three
  tenths over on 7 of 12, id 468). The structured gap exceeds the same-session bare gap by
  a median +0.612 [+0.428, +0.775] over 12 arms, a pass (id 453; +0.662 excluding driving,
  id 455; +0.591 against the banked bare gap, id 459), and the same-session bare gap sits
  a median 0.028 from the banked one (id 465).
- **§4.2**, the reasoning stratum's paragraph: ids 810 to 831.
- **§1 and §5** summarise the result in words: setting out the role and the principle
  restores only part of the stated slack.
- **Table A.10** (Named pairs, Alone, Falls short, Structured share and class), from
  `data/A10_syllogism.csv` and `data/A10_pooled.csv`, built by
  `tables/table_A10_syllogism.py`.
- All registered figures: `paper_numbers.csv` ids 449 to 470, 507 to 509 and 810 to 831,
  with the split at ids 501 to 506 (registered under general_principle).
  Ids 453, 457, 459, 461 and 463 (the median shifts) are registered against Table A.9.

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 4 | frozen prompts and the prompt check: `built_prompts.json`, `frames.json`, `prompt_check.json`, `v11_frames.json` |
| `code/` | 5 | reader and analysis scripts, as run: `analyse_syllogism_duty.py`, `build_syllogism_duty_frames.py`, `build_syllogism_duty_v11_comparands.py`, `probe_syllogism_duty_qwen.py`, `read_syllogism_duty.py` |
| `readings/calls/` | 27 | every call, one JSON line each; 3,902 lines: `completeness_fill_prawns/or_claude.jsonl`, `completeness_fill_prawns/or_deepseek.jsonl`, `completeness_fill_prawns/or_deepseek_s.jsonl`, `completeness_fill_prawns/or_gemma27b.jsonl`, `completeness_fill_prawns/or_gpt4o.jsonl`, `completeness_fill_prawns/or_gpt6l_s.jsonl`, `completeness_fill_prawns/or_gpt6s_s.jsonl`, `completeness_fill_prawns/or_grok43_s.jsonl`, `completeness_fill_prawns/or_haiku_s.jsonl`, `completeness_fill_prawns/or_kimi.jsonl`, `completeness_fill_prawns/or_llama70b.jsonl`, `completeness_fill_prawns/or_mistral24b.jsonl`, ... |
| `readings/records/` | 32 | per-model read records and result files: `RECOUNT_syllogism_duty.json`, `completeness_fill_V11_SYLL__claude.json`, `completeness_fill_V11_SYLL__deepseek.json`, `completeness_fill_V11_SYLL__deepseek_s.json`, `completeness_fill_V11_SYLL__gemma27b.json`, `completeness_fill_V11_SYLL__gpt4o.json`, `completeness_fill_V11_SYLL__gpt6l_s.json`, `completeness_fill_V11_SYLL__gpt6s_s.json`, `completeness_fill_V11_SYLL__grok43_s.json`, `completeness_fill_V11_SYLL__haiku_s.json`, `completeness_fill_V11_SYLL__kimi.json`, `completeness_fill_V11_SYLL__llama70b.json`, ... |

## Prompt check

3,900 of 3,902 calls in `readings/calls/` carry the hash of a prompt in `prompts/`; 30 of 35 distinct prompts were sent in this folder's calls. Not sent here: `v11_frames.json: G|G1`, `v11_frames.json: G|G1_AP`, `v11_frames.json: G|G2`, `v11_frames.json: G|G3_AP`, `v11_frames.json: G|G3_PA` (sent in the reasoning stratum's calls, `../reasoning_stratum/`). Matching no prompt: no call (a record with no prompt: a cap or error marker), in 2 line(s) of `qwen_probe_20261013.jsonl`. The prompts in `prompts/built_prompts.json` were rebuilt by the reading's own code from the banks and checked by it against the duty test's own earlier calls: 10 of 10 match. Per prompt: `prompts/prompt_check.json`; the method: `../README.md`.

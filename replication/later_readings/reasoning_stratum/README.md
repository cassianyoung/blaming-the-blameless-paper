# reasoning_stratum

The role and the principle set out on the duty pairs (syllogism_duty) and the general
principle asked in the abstract (general_principle), read on the seven reasoning models.
It asks whether models reading with reasoning on hold the professional convention, in
general and per named pair, and how much of their stated slack the structured,
premises-first prompt restores when each case is judged alone. It is the completeness_fill's
reasoning stratum (group H8): reported beside the reasoning-off results and never pooled
with them.

## Pre-registration

`../../../pre-registration/completeness_fill_amendment.md`, group H8, which has two parts:

- **FILL, as a separate stratum:** syllogism_duty on the six reasoning models and Gemini
  3.1 Pro (30 cells each, prawns included), general_principle on the same seven (5 cells
  each), and reasoning_traces' trace re-read on Gemini 3.1 Pro (12 cells): 257 cells.
- **D, by design, recorded and not read:** prevention_paraphrase, practical_syllogism and
  subject_identity on the reasoning models (378 cells with Gemini 3.1 Pro's), since with
  reasoning on most models do not show fault blindness, so those readings have nothing to
  explain there.

H8 carries no prediction of its own (§4 of the amendment). The stratum is read on each
reading's frozen texts and analysed by syllogism_duty's registered predictions (P1 to P4)
and general_principle's own affirmation rule, reported as measured. The amendment was
banked on 2026-10-17, before any call of the completeness_fill; the cells were read the
same day. Two decisions were taken after the read and before the figures were registered:
the stratum is read from reasoning draws only, a cell with fewer than five reasoning draws
not reported (the manuscript's rule for reasoning models, §3.4); and Gemini 3.1 Pro's trace
re-read is recorded as read, not coded, with no figure.

## What was read

| Model | Draws per cell | Cells | Cells reported | Reasoning draws counted | Calls |
|---|---:|---:|---:|---:|---:|
| DeepSeek-V4.1 with reasoning | 10 | 35 | 35 | 350 of 350 | 350 |
| Gemini 3.8 Flash (reasoning) | 10 | 35 | 35 | 342 of 350 | 350 |
| gpt-6-luna with reasoning | 10 | 35 | 26 | 192 of 350 | 350 |
| gpt-6-sol with reasoning | 20 | 35 | 35 | 455 of 700 | 700 |
| grok-4.3 with reasoning | 10 | 35 | 35 | 350 of 350 | 350 |
| Claude Haiku 4.5 with reasoning | 10 | 35 | 35 | 350 of 350 | 350 |
| Gemini 3.1 Pro (reasoning) | 10 | 35 + 12 trace | 35 + 12 trace | 348 of 350 | 470 |

- **Conditions, per model:** syllogism_duty's principle question per pair (A, 6 cells),
  the same-session bare separate re-read (12 cells) and the structured prompt, role and
  principle before the score (B, 12 cells), on the six pairs (pairs 1, 3, 4, 5 and 7 and
  prawns, both legs); general_principle's five prompts (G1 and G2, and G3 in both orders).
  Each model on its banked separate-case wire, reasoning on.
- **Totals:** 257 cells, 257 read, none void and none unread; 2,920 calls; the served
  model was constant on every model.
- **Not reported under the reasoning-draws rule:** nine of gpt-6-luna's structured-prompt
  cells (one with no reasoning draw, eight with 1 to 4 of 10). Three of its B cells have
  five or more and are read, so the stratum's structured-prompt figures are over six
  classed models; gpt-6-luna has none.
- **Gemini 3.1 Pro's trace re-read (12 cells):** read as digits, not coded; no figure.
- **general_principle** is analysed descriptively: its comparands exist only for the
  reasoning-off models.

## Where it is reported

- **§3.3** (Questions): the convention questions and the one-answer prompt "are also read
  on the seven reasoning models, reported as a separate stratum".
- **§4.2** (Role blindness): the paragraph on the reasoning models. All seven hold the
  principle in general (7 of 7) and 6 of 7 on all five pairs other than driving (34 of 35
  cells). The structured gap exceeds the separate gap by a median +0.52 [+0.34, +1.02],
  and no model comes within a tenth of its stated slack (of six classed, five fall more
  than three tenths short and one a tenth to three tenths short).
- **Table A.10:** its caption points to §4.2 for the reasoning stratum. Its rows and
  `data/A10_syllogism.csv` hold only the reasoning-off models.
- **Registered figures:** ids 810 to 835 in `paper_numbers.csv`, all labelled "H8
  reasoning stratum (separate, never pooled)". Ids 810 to 831 are syllogism_duty's (P1:
  6 of 7 models, 34 of 35 cells; driving, 5 of 7 answer yes; P2: role correct 764 of 764;
  P3: median shift +0.517 [+0.335, +1.017] over 6 models against the same-session bare
  gap, +0.492 [+0.269, +0.850] against the banked one; P4: classes against the stated
  slack). Ids 832 to 835 are general_principle's (G1, G2 and a positive G3 gap on 7 of 7;
  median G3 gap +2.900).
- No figure (Figures 1 to 9) uses the stratum, and `RUN_MAP.md` has no row for the
  completeness_fill.

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 2 | frozen prompts and the prompt check: `prompt_check.json`, `v11_frames.json` |
| `code/` | 6 | reader and analysis scripts, as run: `build_completeness_fill_syll_cells.py`, `build_v11_syllogism_frames.py`, `read_v11_syllogism.py`, `rebuild_v11_syll_from_log.py`, `split_completeness_fill_h8.py`, `verify_v11_syllogism_prompts.py` |
| `readings/calls/` | 7 | every call, one JSON line each; 2,920 lines: `or_deepseek_r.jsonl`, `or_gemini_pro.jsonl`, `or_gemini_r.jsonl`, `or_gpt6l_r.jsonl`, `or_gpt6s_r.jsonl`, `or_grok43_r.jsonl`, `or_haiku_r.jsonl` |
| `readings/records/` | 24 | per-model read records and result files: `completeness_fill_H8RO__deepseek_r.json`, `completeness_fill_H8RO__gemini_pro.json`, `completeness_fill_H8RO__gemini_r.json`, `completeness_fill_H8RO__gpt6l_r.json`, `completeness_fill_H8RO__gpt6s_r.json`, `completeness_fill_H8RO__grok43_r.json`, `completeness_fill_H8RO__haiku_r.json`, `completeness_fill_H8__deepseek_r.json`, `completeness_fill_H8__gemini_pro.json`, `completeness_fill_H8__gemini_r.json`, `completeness_fill_H8__gpt6l_r.json`, `completeness_fill_H8__gpt6s_r.json`, ... |

## Prompt check

2,920 of 2,920 calls in `readings/calls/` carry the hash of a prompt in `prompts/`; 35 of 35 distinct prompts were sent in this folder's calls. Per prompt: `prompts/prompt_check.json`; the method: `../README.md`.

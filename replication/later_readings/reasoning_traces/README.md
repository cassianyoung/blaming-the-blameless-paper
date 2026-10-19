# reasoning_traces

Does a reasoning model, judging a duty-test case on its own, bring in the comparison the
professional convention needs? The duty test's separate cases were re-read on the six
reasoning models with the reasoning text kept, and each trace was coded for whether it
compares the subject with someone in the other role (code C), weighs his role (R), or
applies a different standard because of it (S). The prediction was that fewer than one
in five private-case traces would raise the comparison.

## Pre-registration

`../../../pre-registration/reasoning_traces.md`. The instruction and Amendment 1 were
banked on 2026-10-12, before any trace existed (no duty-test reasoning text had ever been
stored), and the coding guide was frozen with its SHA-256 before the re-read. Amendments:

- **Amendment 1** (before the re-read): replaced "no new reads" with a re-read of the separate condition at the banked draw counts, prompts checked against the
  banked prompt hashes; traces analysed against the re-read's own scores; drift against
  the banked means reported, not gated; the convention-stated condition and analysis 4
  not run; two strata (full trace, provider summary) coded and reported separately.
- **Amendment 2** (after the re-read, before any trace was coded or read): Gemini 3.8
  Flash stays in the summary stratum on its characters per billed reasoning token, despite
  its routing label, and is also reported on its own.
- **Amendment 3** (before any trace was coded by the primary coder): the primary coder's
  provider changed to Nebius (same model, same quantisation, same frozen guide) because
  the registered provider answered no call.
- **Amendment 4** (after agreement was computed, before any C share was computed): the
  0.70 agreement floor applies per code; R and S fell below it and are stopped; the
  analyses run on C alone, with a blind 30-trace hand check on C.

## What was read

- **Models** (all with reasoning on): DeepSeek-V4.1 and Claude Haiku 4.5 (full-trace
  stratum); grok-4.3, gpt-6-luna, gpt-6-sol and Gemini 3.8 Flash (provider-summary
  stratum). The served model was constant across the pass on every model.
- **Conditions and cells:** the separate condition only, question Blame, six duty pairs
  (prawns, 1 electrical work, 3 gas safety, 4 childcare, 5 driving, 7 hair dye), both
  legs (private and professional): 12 cells per model, 72 cells.
- **Draws and calls:** 10 per cell, 20 on gpt-6-sol; 840 draws, all 840 parsed. Median
  absolute drift from the banked cell means was 0.05 to 0.10 points per model, against a
  same-session noise comparand of 0.148.
- **Traces:** 748 of 840 draws returned reasoning text. Full stratum 240 of 240; summary
  stratum 508 of 600, with 92 draws without a trace (gpt-6-luna 14, gpt-6-sol 78), counted
  as "no trace" and never coded.
- **Coders:** Qwen3-235B-A22B-2507 (primary, every trace: 748 coded, 0 uncoded) and
  Kimi-K3 (second, a random 20% within each stratum: 150 traces, 48 full and 102 summary,
  0 uncoded), at temperature 0 under the frozen guide. Agreement on C (Gwet's AC1) 0.955
  full, 1.000 summary; R (0.622 to 0.653) and S (0.574 on full traces) fell below the 0.70
  floor and are not analysed. A blind hand check on C by an AI assistant agreed with the
  primary on 27 of 30 traces.
- **Not read:** the convention-stated condition, the retired pair 2 and the control pair 6.
  The traces and codes are not published.

## Where it is reported

- §1.2 (paragraph 33): the full traces raise the comparison in 6 of 120 private cases.
- §3.3 (paragraph 91): the method, the third of the four further readings.
- §4.3 (paragraph 163): 6 of 120 full traces (DeepSeek-V4.1, Claude Haiku 4.5) and 1 of
  260 provider summaries (four models) raise a professional comparison on private cases.
- No table or figure.
- Registered figures in `paper_numbers.csv`, ids 378 to 398. Headline: **378** (private
  cases coded C, full traces, 6 of 120, 5.0%), **379** (summaries, 1 of 260, 0.4%; 40 of
  300 draws without a trace), **380** (Gemini 3.8 Flash alone, 0 of 60) and **384** (the
  analysis 1 prediction, under one in five, holds in every group). Also 381 to 383
  (professional cases), 385 to 387 (agreement on C), 388 to 395 (R and S stopped, with the
  direction of disagreement), 396 and 397 (the hand check) and 398 (analysis 3, not tested,
  underpowered).

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 3 | frozen prompts and the prompt check: `built_prompts.json`, `coding_guide.md`, `prompt_check.json` |
| `code/` | 3 | reader and analysis scripts, as run: `analyse_reasoning_traces.py`, `code_reasoning_traces.py`, `read_reasoning_traces.py` |
| `readings/calls/` | 8 | every call, one JSON line each; 1,738 lines: `coder_primary.jsonl`, `coder_second.jsonl`, `deepseek_r.jsonl`, `gemini_r.jsonl`, `gpt6l_r.jsonl`, `gpt6s_r.jsonl`, `grok43_r.jsonl`, `haiku_r.jsonl` |
| `readings/records/` | 14 | per-model read records and result files: `analysis.json`, `analysis_c.json`, `disagreement_reading.json`, `handcheck_c.json`, `handcheck_c_labels.json`, `handcodes_c.json`, `reasoning_traces_CODES__primary.json`, `reasoning_traces_CODES__second.json`, `reasoning_traces_TRACES__deepseek_r.json`, `reasoning_traces_TRACES__gemini_r.json`, `reasoning_traces_TRACES__gpt6l_r.json`, `reasoning_traces_TRACES__gpt6s_r.json`, ... |

## Prompt check

840 of 1,738 calls in `readings/calls/` carry the hash of a prompt in `prompts/`; 12 of 12 distinct prompts were sent in this folder's calls. The prompts in `prompts/built_prompts.json` were rebuilt by the reading's own code from the banks and checked by it against the duty test's own earlier calls: 72 of 72 match. The coders' prompts (the coding guide's instructions with each trace) were rebuilt by the coding script: 898 coder calls match, 0 do not. Per prompt: `prompts/prompt_check.json`; the method: `../README.md`.

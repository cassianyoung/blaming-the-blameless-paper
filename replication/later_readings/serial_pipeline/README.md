# serial_pipeline

The paper's practical syllogism has a remedy and a failure: asked for the fact, the
principle and the verdict in one answer, the models clear the careful subject; asked the
same steps as independent calls, they blame him. A deployed pipeline is usually neither: its
steps are connected, with an extraction call's output passed forward into the scoring call.
This reading reads that pipeline. Per case, a first call extracts either a factual summary
(1A) or the conclusion on whether the subject could reasonably have prevented the harm
(1B); a second call asks the banked blame question with that output set before the case
under "Extracted findings from a previous step:" (2A, 2B). The banked direct verdict (D)
and the banked one-answer prompt (O) are re-read in the same session as references.

## Pre-registration

`../../../pre-registration/serial_pipeline.md`, written on 2026-10-20 before any call, with
the frames file (sha256 `04fd25ef…`) frozen before the read.

- **Predictions**: serial_pipeline P1, that passing the conclusion forward (2B) brings the
  share of careful-subject cells above 0.10 to within 15 points of the one answer's and at
  least 30 points below the direct verdict's; serial_pipeline P2, that passing a summary
  forward (2A) leaves it within 15 points of the direct verdict's.
- **Amendment 0** fixes the anchors (P0, N and C read through every condition, so each
  condition is scored on its own anchors), call 1's settings (no system message,
  temperature 0 with one recorded fallback), draws (10 per scoring condition), the gate,
  the population (cells gated in all four conditions), the bands and the rule that codes
  call 1B. The **ruling** approved all its defaults before any call.
- **Amendment 1**, during the read and before any analysis: a provider's moderation refusal
  (xAI's HTTP 403 `permission-denied` on one grok-4.3 prompt) is a refused draw, not an
  outage; grok-4.3's first attempt was set aside and the model re-read.
- **Amendment 2**, after the result, declared post-hoc: the definition of "most" for the
  models that blame despite a "could not" conclusion.

## What was read

- **Models**: the thirteen reasoning-off arms of the practical syllogism reading, with their
  banked providers and settings: Claude Sonnet 5, DeepSeek-V4.1-Flash (log-prob),
  DeepSeek-V4.1-Flash (sampled, a check, reported apart), Gemma-3-27B-IT, GPT-4o,
  gpt-6-luna, gpt-6-sol, grok-4.3, Claude Haiku 4.5, Kimi-K3, Llama-3.3-70B-Instruct,
  Mistral-Small-3.2-24B and Qwen3-Next-80B.
- **Design**: six scenarios x three roles (P0, N, C) x (2 extraction calls + 4 scoring
  conditions x 10 draws): 9,828 calls, all served by the banked providers.
- **Kimi-K3 contributes no cell**: it is a log-probability arm and its provider returned no
  log-probabilities on any of its 540 log-probability calls, so its 2A, 2B and D cells fail
  the parse gate, as Amendment 0 requires; nothing was moved to a sampled readout. The
  registered shares are over eleven models and 64 cells.

## Result

| condition | cells above 0.10 | share |
|---|---|---|
| 2A, summary forward | 54 of 64 | 84.4% |
| 2B, conclusion forward | 27 of 64 | 42.2% |
| D, direct verdict | 53 of 64 | 82.8% |
| O, one answer | 10 of 64 | 15.6% |

- **serial_pipeline P1: FAIL.** 2B is 26.6 points above O, against a band of 15; its second
  clause holds (D is 40.6 points above 2B, against 30). Passing the conclusion forward
  halves the blame but does not bring it to the one-answer level.
- **serial_pipeline P2: PASS.** 2A is 1.6 points from D. A factual summary forward leaves
  the direct verdict where it was.
- **By the conclusion forwarded** (call 1B, rule-coded): 55 of 64 cells forward "could
  not", and 19 of those 55 are still blamed; 6 of 64 forward "could", and all 6 are
  blamed. Claude Sonnet 5, Claude Haiku 4.5 and Qwen3-Next-80B blame in more than half of
  their cells despite a "could not" conclusion (Amendment 2). Three conclusions the rule
  leaves unclassified are recorded in `readings/records/serial_pipeline_UNCLASSIFIED_1B.md`
  and are not registered.

## Where it is reported

- **§4.1**: "A pipeline that connects its steps lies between the two ..." (eleven of the
  twelve models; Kimi-K3's provider returned no log-probabilities).
- **Appendix B.7**, the serial pipeline.

Headline figures in `paper_numbers.csv`:

| id | figure | value |
|---|---|---|
| 1070 | cells above 0.10, summary forward | 54 of 64 |
| 1071 | cells above 0.10, conclusion forward | 27 of 64 |
| 1072 | cells above 0.10, direct verdict | 53 of 64 |
| 1073 | cells above 0.10, one answer | 10 of 64 |
| 1074 | serial_pipeline P1 | FAIL |
| 1075 | serial_pipeline P2 | PASS |
| 1080 | conclusion forward: "could not" | 55 of 64 |
| 1081 | of the "could not" cells, blamed | 19 of 55 |
| 1082 | conclusion forward: "could" | 6 of 64 |
| 1083 | of the "could" cells, blamed | 6 of 6 |
| 1084 | models blaming in more than half their cells despite "could not" | Claude Sonnet 5, Claude Haiku 4.5, Qwen3-Next-80B |

## The prompt check for call 2

Call 2's prompt carries call 1's answer, so it cannot be frozen as bytes. Its construction
is frozen instead: the direct verdict's system message, and its user turn preceded by the
findings block. During the read the reader refused any call 2 whose prompt failed that diff,
or whose logged hash differed from the prompt it built. Here the check is repeated from this
folder's files: each call-2 prompt is rebuilt from the frozen direct prompt and the call-1
text in `readings/records/serial_pipeline_READ__<model>.json`, with the reader's own
`call2_user`, and hashed.

grok-4.3's set-aside first attempt is kept in `readings/calls/superseded/` (558 calls) and
is not part of the check or the result.

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 2 | frozen prompts and the prompt check: `prompt_check.json`, `serial_pipeline_FRAMES.json` |
| `code/` | 3 | reader and analysis scripts, as run: `analyse_serial_pipeline.py`, `build_serial_pipeline_frames.py`, `read_serial_pipeline.py` |
| `readings/calls/` | 14 | every call, one JSON line each; 9828 lines (plus 558 set aside in `superseded/`): `or_claude.jsonl`, `or_deepseek.jsonl`, `or_deepseek_s.jsonl`, `or_gemma27b.jsonl`, `or_gpt4o.jsonl`, `or_gpt6l_s.jsonl`, `or_gpt6s_s.jsonl`, `or_grok43_s.jsonl`, `or_haiku_s.jsonl`, `or_kimi.jsonl`, `or_llama70b.jsonl`, `or_mistral24b.jsonl`, ... |
| `readings/records/` | 15 | per-model read records and result files: `serial_pipeline_READ__claude.json`, `serial_pipeline_READ__deepseek.json`, `serial_pipeline_READ__deepseek_s.json`, `serial_pipeline_READ__gemma27b.json`, `serial_pipeline_READ__gpt4o.json`, `serial_pipeline_READ__gpt6l_s.json`, `serial_pipeline_READ__gpt6s_s.json`, `serial_pipeline_READ__grok43_s.json`, `serial_pipeline_READ__haiku_s.json`, `serial_pipeline_READ__kimi.json`, `serial_pipeline_READ__llama70b.json`, `serial_pipeline_READ__mistral24b.json`, ... |

## Prompt check

9828 of 9828 calls in `readings/calls/` carry the hash of a frozen prompt in `prompts/serial_pipeline_FRAMES.json` or of a call-2 prompt rebuilt from it (72 frozen, 468 rebuilt). Per call: `prompts/prompt_check.json`; the method: `../README.md`.

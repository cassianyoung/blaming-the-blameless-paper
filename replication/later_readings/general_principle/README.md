# general_principle

This reading asks the duty convention in the abstract: two separate incidents, the same
careless mistake with the same result, one made by a professional providing a paid service
and one by an amateur doing the same thing at home, with no trade, harm or person named.
It asks whether the professional is more, less or equally to blame (G1, in both orders),
whether a stricter standard applies to the professional (G2, yes or no), and how much each
is to blame on a 0 to 9 scale (G3, in both orders). It then sets the answers beside
syllogism_duty's pair-level reading, so that holding the convention in general can be
compared with holding it for each named pair and with applying it to a single case.

## Pre-registration

`../../../pre-registration/general_principle.md`, banked on 2026-10-13 as an amendment to
the syllogism_duty pre-registration, before any call of this reading. The texts, prompts
and comparands were frozen with SHA-256 digests at the same time. Everything below was also
made on 2026-10-13, before any call.

- **Amendment G0**: checks the instruction's premises against syllogism_duty's banked
  reads; fixes the wording of G3's second order; reads every arm by sampling at
  temperature 1; sets the parsing rules, the 7-of-10 parse gate for G3, the denominator
  of 13 and the bootstrap; and defines the general-against-particular count (AG.6) and
  the test of the paper's "almost none" clause (AG.7).
- **Ruling**: G1 is also read in the second order (amateur first), and "affirms in
  general" becomes "more" on at least 9 of 10 draws in each order; on the seven
  log-probability arms G2 also requests log-probabilities, so mean P(yes) can be
  reported beside the sampled count; the defaults on AG.1 and AG.7 apply.
- **Frames revision**: the second frames file (sha256 `342ec134…`) adds the second-order
  G1 prompt; the four original prompts are carried over byte for byte and the first
  frames file stays as banked.
- **Change of start condition**: the twelve arms other than Mistral-Small-3.2-24B start at
  once; Mistral-Small-3.2-24B waits until its syllogism_duty read is written, because both
  go to the same provider's rate limit.

The headline reporting of the AG.7 count was later governed by two syllogism_duty
amendments: Amendment S (report the separate-case cells as zero or below, positive within
the wording floor, and clearing it; the split was computed before that rule was banked)
and Amendment T (cells whose shortfall from the stated slack exceeds the combined wording
and draw floor).

## What was read

- **Models**: the 13 syllogism_duty arms, with their settings and providers: Claude
  Sonnet 5, DeepSeek-V4.1-Flash (log-prob), DeepSeek-V4.1-Flash (sampled),
  Gemma-3-27B-IT, GPT-4o, gpt-6-luna, gpt-6-sol, grok-4.3, Claude Haiku 4.5, Kimi-K3,
  Llama-3.3-70B-Instruct, Mistral-Small-3.2-24B and Qwen3-Next-80B, all with reasoning
  off.
- **Prompts and orders**: G1 in two orders (professional first, amateur first), G2 in one,
  G3 in two orders; five cells per model.
- **Draws and calls**: 10 draws per cell, sampled at temperature 1.0 on every model:
  650 draws, 651 calls (one empty response from grok-4.3 retried). Every model was served
  by its banked provider, with the served model constant. 13 of 13 models READ; none
  unread; every model has a pair-level comparison.
- **Parsing**: G1 and G2 parsed on all 650 draws of those prompts. G3 parsed 10 of 10 in
  every cell except Mistral-Small-3.2-24B amateur-first, 7 of 10, which passes the 7-of-10
  gate; the three unparsed draws are dropped and kept verbatim.
  On G2 Gemma-3-27B-IT has no log-probability reading (its provider returned the
  end-of-turn token's log-probabilities, not the answer's), so 6 of 6 readable
  log-probability models hold under syllogism_duty.P1's rule; its sampled count stands.
- **As banked, on 13 models**: PG.1 PASS (12 of 13 answer "more" on at least 9 of 10 in
  both orders; grok-4.3 answers "equally" on 9 and 8 of 10; no "less" in either order).
  PG.2 PASS (13 of 13 answer "yes" on 10 of 10). PG.3 PASS (general gap positive on 13 of
  13; median 2.50 [1.30, 2.85] against a median stated slack of 2.08 [1.75, 2.47],
  difference -0.15 [-0.40, +0.55]; per model from 0.65 on grok-4.3 to 4.30 on
  Qwen3-Next-80B). AG.6: 6 of 13 affirm in general but fail at least one named pair;
  6 of 13 hold every named pair, none of them without affirming in general. AG.7: 16 of 52
  cells clear the wording floor, so the "almost none" clause was not supported and was
  redrafted.
- **As the paper counts them**: one readout per model (DeepSeek-V4.1-Flash counted once,
  by its log-probability readout; the sampled readout is a check) and syllogism_duty's
  completed comparands, whose wording floor pools 18 deviations. This gives 12 models:
  PG.1 11 of 12, PG.2 12 of 12, PG.3 12 of 12 with a median general gap of 2.62 [1.45,
  3.05] against a median stated slack of 2.12 [1.71, 2.49] (difference 0.10 [-0.39,
  0.77]); AG.6 6 of 12 affirm in general but not on every named pair, 5 of 12 hold every
  named pair; AG.7 15 of 48 cells clear the wording floor, 6 of 48 are at zero or below
  and 27 of 48 are positive within it; Amendment T: 28 of 48 fall short (26 of 40
  excluding DeepSeek-V4.1-Flash and gpt-6-luna, whose wording floor exceeds their own
  median stated slack).

## Where it is reported

- **§4.2** (role blindness): the single-session sentence, "28 of 48 readings fall short
  of the model's stated slack ... (26 of 40 excluding ...), and 6 of 48 give zero slack.
  While 11 of 12 models affirm in the abstract ... (putting the general gap at a median of
  2.6 points)", with Kimi-K3 affirming on 20 of 20 abstract questions.
- **Table A.10** (the syllogism, the structured prompt and the general principle, per
  model): the G1 to G3 columns and the Alone and Falls short columns; per-model values in
  `data/A10_syllogism.csv`.
- **§3.3** describes the questions; **§1** (the two biases), **§1.2**, **§1.3** and **§7**
  state the finding in words: the convention is held in general and lost in the single
  case.
- **§4.2, reasoning stratum**: this reading's prompts were also read on the seven
  reasoning models under syllogism_duty, reported separately and never pooled (7 of 7
  affirm G1 in both orders and G2; median G3 gap +2.900).

Headline figures in `paper_numbers.csv`:

| id | figure | value |
|---|---|---|
| 471 | models read | 12 of 12 |
| 472 | PG.1, "more" on 9 of 10 in both orders | 11 of 12 |
| 476 | PG.2, "yes" on 9 of 10 | 12 of 12 |
| 479 | PG.3, general gap positive | 12 of 12 |
| 481 | PG.3, median general gap [95% CI] | 2.62 [1.45, 3.05] |
| 482 | PG.3, median stated slack, pairs 1, 3, 4, 7 [95% CI] | 2.12 [1.71, 2.49] |
| 483 | PG.3, median general minus stated [95% CI] | 0.10 [-0.39, 0.77] |
| 484 | AG.6, affirm in general but not on every named pair | 6 of 12 |
| 485 | AG.6, affirm on every named pair | 5 of 12 |
| 487 | AG.7, cells clearing the wording floor | 15 of 48 |
| 501 | AG.7 split, cells at zero or below | 6 of 48 |
| 502 | AG.7 split, positive within the wording floor | 27 of 48 |
| 507 | Amendment T, cells falling short | 28 of 48 |
| 509 | Amendment T, falling short, restricted | 26 of 40 |

Ids 471 to 509 are all registered under this reading (per-model general gaps are 488 to
500); ids 832 to 835 are the reasoning stratum.

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 3 | frozen prompts and the prompt check: `frames.json`, `general_principle_FRAMES_v2.json`, `prompt_check.json` |
| `code/` | 3 | reader and analysis scripts, as run: `analyse_general_principle.py`, `build_general_principle_frames.py`, `read_general_principle.py` |
| `readings/calls/` | 13 | every call, one JSON line each; 651 lines: `or_claude.jsonl`, `or_deepseek.jsonl`, `or_deepseek_s.jsonl`, `or_gemma27b.jsonl`, `or_gpt4o.jsonl`, `or_gpt6l_s.jsonl`, `or_gpt6s_s.jsonl`, `or_grok43_s.jsonl`, `or_haiku_s.jsonl`, `or_kimi.jsonl`, `or_llama70b.jsonl`, `or_mistral24b.jsonl`, ... |
| `readings/records/` | 17 | per-model read records and result files: `RECOUNT_general_principle.json`, `ag7_split.json`, `general_principle_READ__claude.json`, `general_principle_READ__deepseek.json`, `general_principle_READ__deepseek_s.json`, `general_principle_READ__gemma27b.json`, `general_principle_READ__gpt4o.json`, `general_principle_READ__gpt6l_s.json`, `general_principle_READ__gpt6s_s.json`, `general_principle_READ__grok43_s.json`, `general_principle_READ__haiku_s.json`, `general_principle_READ__kimi.json`, ... |

## Prompt check

651 of 651 calls in `readings/calls/` carry the hash of a prompt in `prompts/`; 5 of 5 distinct prompts were sent in this folder's calls. Per prompt: `prompts/prompt_check.json`; the method: `../README.md`.

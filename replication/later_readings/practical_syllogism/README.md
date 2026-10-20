# practical_syllogism

This reading asks whether a model that holds both premises of the verdict still fails to
draw it. The universal premise is asked with no case before it, in its own call: system
"Answer with one word, Yes or No, and nothing else.", user "Under the standard of
reasonable care, is a person at fault for a harm he could not reasonably have prevented?
Answer yes or no." The particular premise (could he reasonably have prevented it?) and the
verdict are taken from earlier separate calls on the same target cases, so each step comes
from its own call. As a remedy check, reported apart, fact, rule and verdict are then asked
in one answer: system "Answer in exactly the form PREVENT=<yes or no> PRINCIPLE=<yes or no>
BLAME=<digit>, and nothing else.", user the case text, a blank line, then "Answer three
questions, in this order.\n1. Could Alaric reasonably have prevented this?\n2. Under the
standard of reasonable care, is a person at fault for a harm he could not reasonably have
prevented?\n3. How much is Alaric to blame, on a scale from 0 to 9, where 0 means not at all
to blame and 9 means entirely to blame?\nAnswer in the form PREVENT=<yes or no>
PRINCIPLE=<yes or no> BLAME=<digit>." (`\n` marks a line break).

## Pre-registration

`../../../pre-registration/practical_syllogism.md`, banked 2026-10-13, before any call of
this reading; all reads were made the same day.

- **Amendment 0** (before any call): froze the texts and their SHA-256 digests; fixed the
  arms and settings; defined "holds the principle" on log-probability arms (mean P(yes) at
  most 0.10); defined the population (75 target-case cells) and the two shares; set the
  band for "conclusion not drawn" at a blame position above 0.10; required the "fell
  short" reading to carry its wording-disagreement caveat; and specified the one-answer
  condition (B), read on the careful, blameless and careless roles so it has its own ruler.
- **Ruling** (before any call): all defaults accepted; both conditions read, B on all
  three roles.
- **Amendment 1** (during the read, before the result was written, provisional figures on
  11 arms already seen): added descriptive figures beside practical_syllogism.P3 (median
  position, and cells above 0.10 and 0.30, in B against the direct reading), with no pass
  mark and no change to practical_syllogism.P3 or its rule.

## What was read

- **Models**: 13 non-reasoning arms, the ones read in prevention_paraphrase: Claude Sonnet
  5, DeepSeek-V4.1-Flash (log-prob and sampled), Gemma-3-27B-IT, GPT-4o, gpt-6-luna,
  gpt-6-sol, grok-4.3, Claude Haiku 4.5, Kimi-K3, Llama-3.3-70B-Instruct,
  Mistral-Small-3.2-24B and Qwen3-Next-80B, each at temperature 1.0 with reasoning off.
  Qwen3-235B-A22B and Qwen3-30B-A3B were not attempted (not available on their providers).
- **Condition A** (the universal premise, no case): 1 prompt, 10 draws per arm, 130 calls.
- **Condition B** (fact, rule and verdict in one answer): 6 scenarios by 3 roles (careful
  P0, blameless N, careless C), 18 prompts, 10 draws per cell, 234 cells, 2,340 calls.
- **2,470 calls** in all. 13 of 13 arms read, each served by its expected provider with the
  served model constant. B: 0 cells failing the parse gate and 0 unparsed draws. One arm's
  first read (grok-4.3, 72 calls) was set aside after an empty response was misread as a
  provider change; the arm was re-read in full (190 calls) and only the re-read is used.
- **The particular premise and the direct verdict are not re-read here**: the fact and the
  "fell short" reading come from prevention_paraphrase (`../prevention_paraphrase/`), and
  the direct blame position from the banked judgement rows (`../../../data/A8_judgement_long.csv`).
  The population is prevention_paraphrase's 75 target-case cells (13 arms by 6 scenarios,
  less 3 gate exclusions on the cheque: DeepSeek-V4.1-Flash log-prob, Kimi-K3,
  Mistral-Small-3.2-24B).
- **As banked**, on 13 arms and 75 cells: the principle is held by 13 of 13; both premises
  in 62 of 75; the conclusion not drawn (blame position above 0.10) in 50 of those 62.
  B passes: median shift -0.455 [-0.565, -0.229], every arm lower.
- **As registered for the paper**, under the one-readout-per-model rule (DeepSeek-V4.1-Flash
  counted once, by its log-probability readout; the sampled readout is shown as a check
  only): 12 models and 69 cells. The figures below are these.

## Where it is reported

- **§4.1**, "The practical syllogism" (paragraphs [127] to [131]), with **Table 4** (the
  syllogism per model) and **Table A.10** (fault-blindness columns: Principle, Fact, Blames
  anyway, One answer against Direct). Data: `../../../data/table4_syllogism.csv`,
  `../../../data/A10_syllogism.csv`, `../../../data/A10_pooled.csv`.
- The method is introduced in **§3.3** ([89]); the result is used in the abstract and
  **§1** ([3], [12], [14], [26], [30], [40], [43]), in the **§5** discussion ([185], [186],
  [192]) and in **§6** limitations ([199]).
- Headline figures (`paper_numbers.csv` ids):
  - 428: arms holding the principle, **12 of 12** (429: practical_syllogism.P1 PASS).
  - 430: cells with both premises held, **59 of 69** (431: the fact held, the same).
  - 432: of those, blame position above 0.10, **47 of 59 (0.797)**, the "four in five" and
    "80%" of the text; 433: over all cells, 47 of 69 (0.681).
  - 436 and 437: above 0.30, 30 of 59 and 30 of 69.
  - 434 and 435: "fell short" modal yes, 21 of 59 and 21 of 69 (the cells
    prevention_paraphrase reported as wording disagreement); 438 and 439: (a) and (b) both,
    20 of 59; (a) or (b), 48 of 59; 440: 12 models.
  - 441: practical_syllogism.P3 median shift, one answer minus direct, **-0.3805 [-0.5562,
    -0.1575]** over 69 cells, 12 models (442: PASS, a remedy result only).
  - 443: cells above 0.10, 9 against 57 of 69; 445: share above 0.10, **0.130 against
    0.826**, the "83% to 13%" of the text; 444: median position **0.000 against 0.333**;
    446: above 0.30, 3 against 40 of 69.
  - 447 and 448: the premises inside the one answer, on P0: PREVENT modal no 63 of 72,
    PRINCIPLE modal no 72 of 72.

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 2 | frozen prompts and the prompt check: `frames.json`, `prompt_check.json` |
| `code/` | 3 | reader and analysis scripts, as run: `analyse_practical_syllogism.py`, `build_practical_syllogism_frames.py`, `read_practical_syllogism.py` |
| `readings/calls/` | 13 | every call, one JSON line each; 2,470 lines: `or_claude.jsonl`, `or_deepseek.jsonl`, `or_deepseek_s.jsonl`, `or_gemma27b.jsonl`, `or_gpt4o.jsonl`, `or_gpt6l_s.jsonl`, `or_gpt6s_s.jsonl`, `or_grok43_s.jsonl`, `or_haiku_s.jsonl`, `or_kimi.jsonl`, `or_llama70b.jsonl`, `or_mistral24b.jsonl`, ... |
| `readings/records/` | 15 | per-model read records and result files: `RECOUNT_practical_syllogism.json`, `practical_syllogism_READ__claude.json`, `practical_syllogism_READ__deepseek.json`, `practical_syllogism_READ__deepseek_s.json`, `practical_syllogism_READ__gemma27b.json`, `practical_syllogism_READ__gpt4o.json`, `practical_syllogism_READ__gpt6l_s.json`, `practical_syllogism_READ__gpt6s_s.json`, `practical_syllogism_READ__grok43_s.json`, `practical_syllogism_READ__haiku_s.json`, `practical_syllogism_READ__kimi.json`, `practical_syllogism_READ__llama70b.json`, ... |

## Prompt check

2,470 of 2,470 calls in `readings/calls/` carry the hash of a prompt in `prompts/`; 19 of 19 distinct prompts were sent in this folder's calls. Per prompt: `prompts/prompt_check.json`; the method: `../README.md`.

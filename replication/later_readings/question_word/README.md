# question_word

This reading asks whether the base models' fault blindness rests on the word "blame". In
everyday English "to blame for" can mean simply "caused", so the worksheet's question might
be read causally. The six pretrained base models of the worksheet reading are re-read on the
same worksheet with the question word replaced throughout (the header, the four worked
examples' questions and the target case's question), everything else fixed: the header's
shape, the worked examples and their ratings, the five orderings, the six scenarios and
every role.

| wording | question | scale text |
|---|---|---|
| blame (baseline) | How much is X to blame? | not at all to blame ... entirely to blame |
| at fault (the test) | How much is X at fault? | not at all at fault ... entirely at fault |
| responsible | How much is X responsible for what happened? | not at all responsible ... entirely responsible |

## Exploratory, not pre-registered

This reading was made in discovery mode, with nothing predicted in advance, and is reported
as exploratory: its figures are registered with that status, and the paper says so (Appendix
B.7). Two things were fixed before any read:

- **The frames**, derived from the banked worksheet frames by exact substitution, with
  every substitution count asserted (one header, four worked questions and one target
  question per frame), and frozen with all 930 prompt hashes in
  `prompts/question_word_FRAMES_MANIFEST.json`. The blame frames are the banked file
  itself, unchanged, so the baseline is the banked instrument by construction.
- **A ruling on "responsible"**: its worked examples conflict with the question (*Dilys
  photocopied the reading list* is rated 0, though she is wholly responsible for what
  happened in the causal sense), so it is read and reported, and no conclusion is drawn
  from it. "At fault" is the test.

## What was read

- **Models**: Llama-3.1-8B, Mistral-7B-v0.3, Qwen3-8B-Base, OLMo-2-1124-7B, Falcon3-7B-Base
  and gemma-2-9b, pretrained only, in bf16 on local weights (one GPU), each loaded once for
  all three wordings.
- **Readout**: teacher-forced log-probabilities at the answer position (the probability-
  weighted mean over the digits 0 to 9), as the worksheet reading reads them. Every cell
  is a raw completion prompt, not a chat message.
- **Prompts**: 3 wordings x 5 orderings x 62 bank rows (six scenarios, every role) = 930
  prompts; each model reads all 930, so 5,580 cells.
- **Reproduction**: the blame re-read equals the worksheet reading's banked cells on all six
  models, largest difference in expected value 0.8e-6 to 1.2e-6 over 310 cells each (same
  card class, the same torch and transformers versions).
- **Definitions** are the database's (`../common/results_derive.py`): band, worksheet gate,
  position and pooled band.

## Result

Over the six models and six scenarios (36 readings per wording):

| | blame | at fault | responsible (no conclusion drawn) |
|---|---|---|---|
| passing the worksheet gate | 36 | 34 | 31 |
| careful subject (P0) more than one band above the blameless anchor (N), of those passing | 35 | 33 | 31 |
| P0 position, median over those passing | 0.565 | 0.554 | 0.503 |

- **At fault**: P0 - N stays within one pooled band of its "to blame" reading on 34 of the
  34 readings that pass both, and neither anchor moves more than one pooled band on any of
  them, so the wording tests P0 cleanly. Gate failures: Qwen3 on the bicycle (C - N 2.86
  bands) and the ladder (2.94), both just under 3.0.
- **Responsible**, reported only: the blameless anchor rises (median +1.13 pooled bands)
  while the careless anchor does not, and OLMo 2 fails the gate on 5 of 6 scenarios.

## Where it is reported

- **§4.5**: "asked instead how much the careful subject is at fault, with everything else
  unchanged, six of the base models place him where they did (median position 0.55 ...)".
- **Appendix B.7**, the question word and lexical polysemy (exploratory).

Headline figures in `paper_numbers.csv`:

| id | figure | value |
|---|---|---|
| 1076 | median P0 position, "to blame" (36 of 36 pass) | 0.565 |
| 1077 | median P0 position, "at fault" (34 of 36 pass) | 0.554 |
| 1078 | "at fault" readings whose P0 - N stays within one pooled band of "to blame", of those passing both | 34 of 34 |
| 1079 | "at fault" readings passing the worksheet gate | 34 of 36 |

## How this folder differs from the others

The other readings were made through APIs, so each holds every call as logged. This one
was read on local weights, so it has no `readings/calls/`:

- `readings/cells/<wording>/<model>__<scenario>.json` holds the per-cell results, one file
  per model and scenario: for every prompt, its hash, the normalised digit distribution,
  the answer mass, the expected value and the top tokens, with the model's environment.
- `prompts/built_prompts.json` holds the 930 prompts as text, rendered from the frames by
  the reader's own `prompt_for` (`../common/rate_pod216.py`). Each rendered prompt
  reproduces the hash frozen in the manifest; the case texts are due-care-eval's banks
  (the 62 rows are in its `banks/`, word for word).
- The reader, `code/read_question_word.py`, runs on the pod through
  `code/question_word_pod_batch.sh`, and imports `../common/rate_pod216.py` and
  `../common/gradient_model.py`.

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 6 | frozen prompts and the prompt check: `built_prompts.json`, `prompt_check.json`, `question_word_FRAMES_MANIFEST.json`, `question_word_FRAMES__at_fault.json`, `question_word_FRAMES__responsible.json`, `worksheet_FRAMES__blame.json` |
| `code/` | 4 | reader and analysis scripts, as run: `analyse_question_word.py`, `build_question_word_frames.py`, `question_word_pod_batch.sh`, `read_question_word.py` |
| `readings/cells/` | 108 | per-cell results, one file per model and scenario under each wording: `at_fault/falcon3_base__bicycle216.json`, `at_fault/falcon3_base__cheque.json`, `at_fault/falcon3_base__ladder.json`, `at_fault/falcon3_base__prawns_home.json`, `at_fault/falcon3_base__prawns_restaurant.json`, `at_fault/falcon3_base__scaffolding.json`, `at_fault/gemma9_base__bicycle216.json`, `at_fault/gemma9_base__cheque.json`, `at_fault/gemma9_base__ladder.json`, `at_fault/gemma9_base__prawns_home.json`, `at_fault/gemma9_base__prawns_restaurant.json`, `at_fault/gemma9_base__scaffolding.json`, ... |
| `readings/records/` | 2 | per-model read records and result files: `question_word_REGISTERED.json`, `question_word_RESULT.json` |

## Prompt check

5580 of 5580 cells in `readings/cells/` carry the hash of a prompt in `prompts/built_prompts.json`; 930 of 930 rendered prompts were read, and each rendered prompt reproduces the hash frozen in the manifest before any read. Per wording: `prompts/prompt_check.json`; the method: `../README.md`.

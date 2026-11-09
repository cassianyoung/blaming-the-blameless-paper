# duty_on_base

The paper's role blindness was measured on deployed models: shown a careless professional
and a careless private person separately, they blame the two about equally, and they give
the private person slack only when the two are set side by side. This reading asks where
that comes from. The duty test's six pairs are read on six pretrained base checkpoints and
on the developer releases of the same six families, each leg as a separate case, on the
worksheet frame. The side-by-side condition needs a two-score answer and cannot be put to a
base model, so the quantity compared is the gap between the two legs read separately: the
professional leg's score minus the private leg's.

## Pre-registration

`../../../pre-registration/duty_on_base.md`, written on 2026-11-06 before any model was
loaded, with the frames file (sha256 `7fb5badf…`) frozen before the read. It is the banked
text with private paths and the author's name removed and the public labels applied;
nothing else is changed. Amendment 0 fixes what the instruction leaves open, and the
ruling, made before any read, settles its six points.

- **duty_on_base P1 (the residue claim).** Per family, the median gap over the five pairs
  other than driving, base minus release, reaches **0.16 of the model's own range** (ruler
  units, below) on at least 4 of the 6 families. Raw digits at 0.5 are reported beside and
  decide nothing.
- **duty_on_base P2 (nothing there).** The base gap lies within one pooled noise band of zero
  on at least 20 of the 30 base cells (six models x five pairs other than driving).
- **duty_on_base P3 (driving as control).** On driving, where both legs break the same rule,
  the gap lies within one pooled band of zero on at least 10 of the 12 models, base and
  release.
- P1 and P2 cannot both pass. The four outcomes and their readings were registered before
  the read (A0.9); "both fail" reads *the base distinguishes the legs, no more than the
  release*, the null for the residue claim.

## What was read

- **Families**: gemma-2-9b, Llama-3.1-8B, Mistral-7B-v0.3, Qwen3-8B, OLMo-2-1124-7B and
  Falcon3-7B: the pretrained base checkpoint and the developer release of each (twelve
  models), in bf16 on local weights, one GPU, each loaded once for both parts.
- **Frame**: the worksheet, raw completion prompts with the four banked worked examples, five
  orderings, teacher-forced log-probabilities at the answer position (the probability-
  weighted mean over the digits 0 to 9), and the banked gate.
- **Per model, on one load**: (1) the banked worksheet on its six scenarios (310 cells),
  which gives the model's ruler and its licence on the frame; (2) the duty test's twelve
  legs (six pairs x professional and private) through the same five orderings (60 cells).
- **The ruler.** Base and release use the scale differently (here the releases' rulers run
  3.6 to 5.9 digits, the bases' 2.1 to 4.4), so a difference in raw digits is not comparable
  across them. Each model's ruler is its own median careful-to-careless distance (C - N) over
  its licensed worksheet scenarios, from the same load, and each gap is divided by it. A
  model is licensed on the frame if at least 4 of its 6 scenarios pass the gate; all twelve
  passed on 6 of 6.
- **Bands**: a leg's band is 2.33 x the standard deviation of its five orderings; a gap's is
  the pooled band of its two legs, sqrt((b_pro^2 + b_priv^2) / 2). Definitions are the
  database's (`../common/results_derive.py`).
- **Reproduction**: the six base models' worksheet cells equal the question_word reading's
  banked "to blame" cells to at most 1.2e-6 in expected value.

## The comparison, and what it is not

Base against release, **on one frame**. The deployed models of the paper were read through
chat frames with a log-probability or sampled readout, and the releases here are 7 to 9
billion parameter checkpoints read on the worksheet; this reading says nothing directly
about the deployed models (ruling 3).

## Result

| Family | Base gap (digits / ruler) | Release gap (digits / ruler) | Base minus release (ruler) |
|---|---|---|---|
| gemma-2-9b | 0.48 / 0.189 | 0.50 / 0.096 | 0.09 |
| Llama-3.1-8B | 0.42 / 0.129 | 0.59 / 0.164 | -0.03 |
| Mistral-7B-v0.3 | 0.29 / 0.136 | 0.33 / 0.085 | 0.05 |
| Qwen3-8B | 0.41 / 0.121 | 0.49 / 0.083 | 0.04 |
| OLMo-2-7B | 0.34 / 0.119 | 0.34 / 0.072 | 0.05 |
| Falcon3-7B | 0.22 / 0.050 | 0.15 / 0.030 | 0.02 |

(median gap over the five pairs other than driving)

- **duty_on_base P1: FAIL, 0 of 6.** The base's gap is larger than the release's on 5 of 6
  families, by 0.02 to 0.09 of the model's range, against the pre-registered 0.16. In raw
  digits the release's is larger on 4 of 6, because the releases use more of the scale.
- **duty_on_base P2: FAIL, by one cell.** 19 of the 30 base cells lie within one pooled band
  of zero (20 needed). 28 of the 30 base gaps are positive; the 11 beyond noise fall on
  electrical work (4 of 6 models), gas safety (3), childcare (3) and hair dye (1), and none
  on prawns.
- **duty_on_base P3: FAIL, 8 of 12 within the band (10 needed).** Outside: Llama-3.1-8B base
  (0.37 digits, band 0.32), gemma-2-9b release (0.43, 0.36), Llama-3.1-8B-Instruct (0.95,
  0.51) and Mistral-7B-Instruct (0.25, 0.22). 11 of the 12 driving gaps are positive (the
  taxi driver blamed more than the friend for the same worn tyre); OLMo-2-7B base's is
  -0.01.
- **Reading, as registered: both fail.** The base distinguishes the legs, no more than the
  release: the null for the residue claim. As A0.9 says, P3 qualifies every row: the
  professional leg's wording raises blame where the control says role should not matter, on
  several models and most strongly on the releases, so the base's small separation is not
  cleanly about role, and nothing here licenses calling either version's gap the allowance.
- **Pooled medians** (30 cells each, ruler units): base 0.12, release 0.09.

## Where it is reported

- **§1.2**: "Role blindness was read on six pretrained checkpoints and their releases on the
  worksheet frame ..."
- **§4.5**, *The duty test on base checkpoints*, and **§6**.
- **Appendix B.7**, duty_on_base.

Figures in `paper_numbers.csv`:

| id | figure | value |
|---|---|---|
| 1133 | base minus release, gemma-2-9b (ruler) | 0.09 |
| 1134 | base minus release, Llama-3.1-8B (ruler) | -0.03 |
| 1135 | base minus release, Mistral-7B-v0.3 (ruler) | 0.05 |
| 1136 | base minus release, Qwen3-8B (ruler) | 0.04 |
| 1137 | base minus release, OLMo-2-7B (ruler) | 0.05 |
| 1138 | base minus release, Falcon3-7B (ruler) | 0.02 |
| 1139 | families reaching 0.16 (P1) | 0 of 6 |
| 1140 | families with the base gap above the release's | 5 of 6 |
| 1141 | base cells with a positive gap | 28 of 30 |
| 1142 | base cells beyond one pooled band | 11 of 30 |
| 1143 to 1147 | of those, by pair: prawns, electrical work, gas safety, childcare, hair dye | 0, 4, 3, 3, 1 of 6 |
| 1148 | driving, models with a positive gap | 11 of 12 |
| 1149 | driving, models beyond one pooled band (P3) | 4 of 12 |
| 1150 | driving, Llama-3.1-8B-Instruct's gap (digits) | 0.95 |
| 1151 | pooled median gap, base (ruler) | 0.12 |
| 1152 | pooled median gap, release (ruler) | 0.09 |

## Reproducing the figures

```
python3 replication/later_readings/duty_on_base/check_registered.py
```

Standard library only. It runs the analysis script's own self-test (7 of 7), recomputes every
figure above from `readings/cells/` with the analysis script's functions, and requires each to
equal the banked result file, the frozen record and its line in `paper_numbers.csv`. The code
in `code/` is as run, with the working repository's paths (`../README.md`, Names and paths), so
the script lays this folder's files out in that layout as symbolic links in a temporary
directory before importing it. `code/seed_duty_on_base.py` is the function that registered the
figures; its note that a working record said "all twelve" driving gaps were positive is the
reason the figure was taken from the result file (11 of 12).

## How this folder differs from the API readings

Read on local weights, like question_word, so it has no `readings/calls/`:

- `readings/cells/worksheet/<model>__<scenario>.json`: the banked worksheet per model and
  scenario (each model's ruler and gate); `readings/cells/duty/<model>.json`: the twelve duty
  legs through the five orderings. For every cell: its prompt hash, the normalised digit
  distribution, the answer mass, the expected value and the top tokens, with the model's
  environment.
- `prompts/built_prompts.json` holds the 370 prompts as text, rendered by the reader's own
  functions (`../common/rate_pod216.py`'s `prompt_for` for the worksheet,
  `../common/moral_frames.py`'s `render` for the legs). Each reproduces the hash frozen before
  any read: the worksheet's in `../question_word/prompts/question_word_FRAMES_MANIFEST.json`
  ("to blame"), the legs' in `prompts/duty_on_base_FRAMES.json`.
- The reader, `code/read_duty_on_base.py`, runs on the pod through
  `code/duty_on_base_pod_batch.sh`, and imports `../common/rate_pod216.py` and
  `../common/gradient_model.py`; the analysis imports `../question_word/code/analyse_question_word.py`
  for the worksheet loader.

## Contents

| path | files | |
|---|---:|---|
| `prompts/` | 4 | frozen frames and the prompt check: `duty_on_base_FRAMES.json` (sha256 `7fb5badf…`), `worksheet_FRAMES__blame.json` (sha256 `fd1236b3…`), `built_prompts.json`, `prompt_check.json` |
| `code/` | 5 | reader, batch, frame builder, analysis and the registering seeder, as run: `read_duty_on_base.py`, `duty_on_base_pod_batch.sh`, `build_duty_on_base_frames.py`, `analyse_duty_on_base.py`, `seed_duty_on_base.py` |
| `readings/cells/` | 84 | per-cell results: 72 worksheet files (twelve models x six scenarios), 12 duty files |
| `readings/records/` | 2 | `duty_on_base_RESULT.json` (the analysis's result, per model and pair in `per_arm`), `duty_on_base_REGISTERED.json` (the registered figures, frozen) |
| `check_registered.py` | 1 | the reproduction above |

## Prompt check

4440 of 4440 cells in `readings/cells/` carry the hash of a prompt in `prompts/built_prompts.json` (3720 worksheet, 720 duty); 370 of 370 rendered prompts were read, and each reproduces the hash frozen before any read. Per part: `prompts/prompt_check.json`; the method: `../README.md`.

# Acceptance: due-care-eval reproduces the paper

**Checked against database build `691397926c97eafd7440556b172b947c9880d5d41647d7fd49faf9e7a7697e6f`**,
the build `../data/` comes from (`../reference/paper_values.json` records the sha it was
exported from). Both acceptance runs were first checked against build `2c1c3c76ab96ab36…`,
then against `1344b8ca…`, `f54aa992…` and `851c599b…`. Between `851c599b…` and this build
one value the comparison reads changed: Llama-3.3-70B's prawns stated gap is now the full
text side-by-side prompt's (due-care-eval v1.1), which the 10 October logs did not read, so
it was read afresh (section 1). Every other compared value is unchanged, and the local
comparison's table is identical against both builds. The earlier rebuilds changed how the
per-scenario table stores worksheet cells (every ordering, not the last one read) and the
registry of paper numbers; no position, band or gate the comparison reads moved.

due-care-eval is accepted when it reproduces the paper's values on local weights to the
printed precision, and on an API model within that arm's draw band. `../compare.py` makes
the comparison from the Inspect logs alone, against `../reference/paper_values.json`.

## 1. API model, chat frame (done)

**Model:** `llama70b` (Llama-3.3-70B-Instruct, served by CoreWeave, log-prob readout,
reasoning off), the cheapest reasoning-off arm the paper read whose provider still serves
it with log-probabilities.

**Read:** the excuse test on the bicycle (36 cells, 10 draws each, 360 calls) and the
duty test on two pairs (prawns, and electrical work with its convention and three neutral
sentences; 18 cells, 180 calls), on 10 October 2026. Then, on 19 October 2026 with
due-care-eval v1.1-rc2 (commit `b6a2043`), the prawns pair's full-text side-by-side prompt in
both orders (`-T pairs=prawns -T conditions=joint_full`; 2 cells, 10 draws each, 20
calls, none void), which v1.1 makes the stated gap's source. Every call was served by the
provider the paper used. Cost about US$0.05 and US$0.002.

**Result: 24 of 24 comparable values within their rule; no discrepancies.**
Full table: [`api_comparison.md`](api_comparison.md).

| quantity | paper | fresh | band |
|---|---|---|---|
| bicycle: target case position (P0) | 0.25 | 0.25 | 0.04 |
| bicycle: gate | PASSED | PASSED | |
| bicycle: prevention on the target case, P(yes) | 0.00 | 0.00 | 0.10 |
| prawns: stated gap, full-text prompt (two-order mean) | 0.70 | 0.70 | 0.42 |
| prawns: separate gap | 0.40 | 0.39 | 0.42 |
| prawns: gap with the convention stated | 3.07 | 3.09 | 0.42 |
| electrical: stated gap | 0.00 | 0.00 | 0.42 |
| electrical: separate gap | 0.00 | 0.00 | 0.42 |
| electrical: gap with the convention stated | 2.79 | 2.85 | 0.42 |
| electrical: neutral baseline | 0.08 | 0.07 | 0.42 |

The duty test was accepted on one API arm, two pairs. No local comparand exists, because
the paper read the duty test through APIs only.

The wording floor, signal-to-noise and class are pooled over every pair an arm was read
on. On a two-pair read the floor is computed from one pair's neutral sentences, so these
three are reported in the table and not compared.

**Environment:** inspect-ai 0.3.270, Python 3.12.

**Logs** (in [`logs/`](logs/), hashes in [`logs/SHA256SUMS`](logs/SHA256SUMS)):

* `2026-10-10T13-51-17-00-00_excuse_epo2hwaogkQ8Yo9zJi4H4E.eval`
  sha256 `7dc115442b366201f8e5f0d522ef1b2b5a32e76ea403020dffc8659ffcc1042d`
* `2026-10-10T13-52-16-00-00_duty_6iRztepcbUryKxUsMnQ4dT.eval`
  sha256 `6c802dcc2196d58a516a3edd2937bd51f2149f0e6995bd464df6f9f339155c67`
* `2026-10-19T10-27-51-00-00_duty_dyiPiGzGxBVKUKNtZDzNw5.eval` (the full-text prompt)
  sha256 `df42d903b16fb83fd49a0b5fc2ff420e19b4f16695dd6235e27a9cbbd449d845`

The two 10 October logs name the task and model `duecare/excuse`, `duecare/duty` and
`duecare/llama70b`: the eval package's name when they were taken. The code they ran is
due-care-eval's, under its final name `due_care`; the logs are kept unaltered because their
hashes are registered above.

## 2. Local weights (done)

**Models:** Gemma 2 9B base on the worksheet, Gemma-2-9B-it on chat, Llama 3.1 8B base on
the worksheet, Llama-3.1-8B-Instruct on chat and on the worksheet; all six scenarios, all
four questions on chat, BLAME under the five orderings on the worksheet. Each checkpoint
was downloaded at its pinned revision and every weight file verified against the Hub's
SHA-256 before loading (`google/gemma-2-9b@33c19302`, `google/gemma-2-9b-it@11c9b309`,
`meta-llama/Llama-3.1-8B@d04e592b`, `meta-llama/Llama-3.1-8B-Instruct@0e9e39f2`); the
determinism check passed on every frame.

**Result: 378 of 378 checked values equal the paper's to two decimals; no discrepancies.**
Every position, mean, band and gate statistic, and every gate verdict. Full table:
[`local_comparison.md`](local_comparison.md).

| reading | target case (P0) on the bicycle | gate |
|---|---|---|
| Gemma 2 9B base, worksheet | 0.56 | LICENSED, C - N = 6.57 bands |
| Gemma-2-9B-it, chat | 0.90 | PASSED |
| Llama 3.1 8B base, worksheet | 0.69 | LICENSED |
| Llama-3.1-8B-Instruct, chat | 0.69 | **FAILED**: blameless mass on 0-3 is 0.49 |
| Llama-3.1-8B-Instruct, worksheet | 0.63 | LICENSED |

Llama's chat release fails the chat gate on every scenario and passes on the worksheet,
as in the paper. The study adapters were not read: their repositories are not yet public.

**Environment:** NVIDIA RTX A6000 (48 GB), driver 595.91.07, CUDA 12.8, Python 3.12.3,
torch 2.8.0+cu128, transformers 5.15.0, peft 0.20.0, safetensors 0.8.0, numpy 2.1.2,
inspect-ai 0.3.270, weights in bf16.

**Logs** (hashes in [`logs/SHA256SUMS`](logs/SHA256SUMS)):

* `2026-10-10T16-13-09-00-00_excuse_jgdprzSCsWmb643EHsrjma.eval` (Gemma 2 9B base, worksheet)
* `2026-10-10T16-16-52-00-00_excuse_MsNxqSus5HskM6xQ7QTPfA.eval` (Gemma-2-9B-it, chat)
* `2026-10-10T16-18-06-00-00_excuse_Kwug8JNBr3kCV52WXZUvCi.eval` (Llama 3.1 8B base, worksheet)
* `2026-10-10T16-20-39-00-00_excuse_UTx4zt5PhL2JoET88ZNUVs.eval` (Llama-3.1-8B-Instruct, chat)
* `2026-10-10T16-21-46-00-00_excuse_fnytKbeSvXQwQjsmd7Q2pt.eval` (Llama-3.1-8B-Instruct, worksheet)

**The reference for worksheet readings** is the mean over the five orderings
(`positions_value` in the paper's database), the construction the views define.

## 3. Parsing of the paired answer

The paper's prawns-pair comparisons were parsed strictly (`../../MEASUREMENT_NOTES.md`, section
2): the answer must be the two labelled digits alone. due-care-eval keeps the looser rule the
paper used for the five other pairs, a case-sensitive search for each label followed by `=`
and a digit, and applies it to all six pairs. On the paper's banked prawns reads (480
paired draws in the call logs, 460 of them in banked readings; the other 20 are a lost first read of Mistral-24B) the two rules disagree on
two draws, both Mistral-24B's:

| draw | raw answer | strict (paper) | due-care-eval |
|---|---|---|---|
| home first, 1 of 10 | `HOME=6`, newline, `CHEF=8` | void | HOME 6, CHEF 8 |
| chef first, 1 of 10 | `Chef=8 Home=6` | HOME 6, CHEF 8 | void |

The first is the one draw the paper voided; due-care-eval reads it. The second the paper read
and due-care-eval voids, because its labels are not in capitals. Re-scored under
due-care-eval's rule, Mistral-24B's prawns stated gap is 2.39 (home first 2.90 over 10 draws,
chef first 1.89 over 9) against the paper's 2.45 (3.00 over 9, 1.90 over 10). Every other
model's prawns reading is identical under both rules. Mistral-24B was not among the
acceptance arms above, so no comparison in sections 1 and 2 is affected.


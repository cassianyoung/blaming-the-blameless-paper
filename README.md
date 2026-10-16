# Blaming the Blameless

**Language Models Know the Standard of Reasonable Care but Do Not Apply It**

This repository holds the manuscript, the derived data behind every figure and table,
and the scripts that redraw the figures and rebuild the tables from that data alone. It
also holds what the study used beyond the evaluation: the adapters (corpus, recipe,
manifests and links to the weights), the pre-registrations, the model table for every
model read, and the scripts that re-read the paper's readings and compare them with the
reported values. The evaluation itself (the cases, the questions, the readers for local
weights and APIs, and the database build) is published separately as
**due-care-eval** (link added at release), release tag `v1.0`,
and knows nothing of this paper.

## Contents

| Path | What it is |
|---|---|
| `paper/blaming-the-blameless.docx` | the manuscript |
| `data/` | the derived CSVs the figures and tables read, each stamped with the sha256 of the results database it was exported from, and the SQL that produced them (`*_queries.sql`, documentation only) |
| `figures/` | one script per figure; `figures/build_all.py` draws them all into `figures/out/` |
| `tables/` | one script per table; `tables/build_all.py` writes each as CSV and Markdown into `tables/out/` |
| `paperlib.py` | shared helpers: reading `data/`, labels, number formatting |
| `paper_numbers.csv` | numbers registered against the text, with location, printed form, the query that produced each (documentation) and the value at build |
| `check_paper_numbers.py` | checks each registered number against the CSVs in `data/` where a CSV carries it |
| `adapters/` | the LoRA adapters read in the paper: the instruction corpus, the recipe, a training manifest per adapter, the weight digests, each base model's licence, and links to the weights on Hugging Face ([`adapters/README.md`](adapters/README.md)) |
| `pre-registration/` | the pre-registrations and amendments behind the excuse test, the duty pairs, the remedies and the adapter controls |
| `replication/` | the model table, the reference values, and the scripts that re-read the paper's readings with due-care-eval and compare them ([`replication/README.md`](replication/README.md)) |
| `MEASUREMENT_NOTES.md` | the instrument findings behind the design choices of section 3 |

## Regenerating the figures and tables

Python 3.10 or later, with matplotlib (the tables need only the standard library):

```
pip install matplotlib
python figures/build_all.py
python tables/build_all.py
python check_paper_numbers.py
```

Every script reads only `data/`, located relative to the script, so it runs from any
working directory and needs neither the database nor the evaluation code. Each figure
script also writes the values it plotted (`figures/out/*_values.csv`).

| Manuscript | Script | Reads |
|---|---|---|
| Figure 1 (Bias 1 effect sizes, panels A and B) | `figures/fig1_bias1.py` | `fig1_panelA.csv`, `fig1_panelB.csv` |
| Figure 2 (Bias 2 effect sizes, slack withheld) | `figures/fig2_bias2_slack.py` | `fig7_duty.csv` |
| Figure 2 in section 3.3 (re-scaling raw readings) | `figures/fig2_rescaling.py` | `B2_deployed_bicycle.csv` |
| Figure 3 (local models by scenario, two frames) | `figures/fig3_frames.py` | `frame_by_scenario.csv` |
| Figure 4 (deployed models across scenarios) | `figures/fig4_across_scenarios.py` | `B5_across_scenarios_wide.csv` |
| Figure 5 (base, adapter and release) | `figures/fig5_tuning.py` | `B1_tuning_table.csv` |
| Figure 6 (chef and home cook) | `figures/fig6_chef_home.py` | `chef_home.csv`, `chef_home_cmp3_probabilities.csv` |
| Table 3 (deployed models read) | `tables/table3_deployed_models.py` | `table3_coverage.csv`, `B2_deployed_bicycle.csv`, `B5_across_scenarios_wide.csv`, `chef_home.csv` |
| Table B.1 | `tables/table_B1_tuning.py` | `B1_tuning_table.csv`, `B1_tuning_table_summary.csv` |
| Table B.2 | `tables/table_B2_deployed_bicycle.py` | `B2_deployed_bicycle.csv` |
| Table B.3 | `tables/table_B3_frames.py` | `frame_table_bicycle.csv`, `frame_table_summary.csv` |
| Table B.4 | `tables/table_B4_chef_home.py` | `chef_home.csv`, `chef_home_cmp3_probabilities.csv` |
| Table B.5 | `tables/table_B5_across_scenarios.py` | `B5_across_scenarios_wide.csv` |
| Table B.6 | `tables/table_B6_bystander.py` | `B6_bystander_long.csv`, `B6_within_family.csv` |
| Table B.7 | `tables/table_B7_yi.py` | `B7_yi_long.csv` |
| Table B.8 | `tables/table_B8_judgement.py` | `B8_judgement_long.csv` |
| Table B.9 (signal-to-noise for the duty test) | `tables/table_B9_signal_to_noise.py` | `B9_signal_to_noise_long.csv`, `B9_signal_to_noise_arm.csv` |
| Table B.10 (the duty test by model and pair) | `tables/table_B10_duty_by_model.py` | `B10_duty_long.csv`, `B10_duty_arm.csv` |
| Table B.11 (the syllogism, the structured prompt and the general principle) | `tables/table_B11_syllogism.py` | `B11_syllogism.csv`, `B11_pooled.csv` |

Tables 1, 2, 4 and 5 are descriptive (the case template, the questions, the local
families and the adapter recipe) and carry no measured values. `data/` also holds the
duty test's remaining exports (`duty_remedies*.csv`, `duty_pairs_not_reported.csv`,
`duty_spread.csv`) and each export's list of exclusions with reasons
(`*_excluded.csv`).

## Which results can be re-read

**Reproducible from the evaluation code on local weights.** Everything read on our own
hardware from published checkpoints: the nine pretrained base models and the two smaller
Yi base models on the worksheet frame; the same bases with the study adapters (linked
from `adapters/README.md`); the developers' instruction-tuned
releases on the worksheet and through their own chat templates; and the local readings
of Gemma-3-27B-IT and Qwen3-8B. These are read from logits at bf16, at pinned revisions,
with a deterministic forward pass, so re-running due-care-eval on the same checkpoints
reproduces them; `replication/run_reading.py` does so reading by reading and compares
the result with the paper's values. In `data/` these are `fig1_panelA.csv`, `B1_*`, `B6_*`, `B7_*`,
`frame_by_scenario.csv`, `frame_table_*` and the `local` rows of `chef_home*.csv`.

**Read through commercial APIs and reported as read.** The deployed models (GPT-4o,
gpt-6-luna, gpt-6-sol, Claude Sonnet 5, Claude Haiku 4.5, Qwen3-235B, Qwen3-Next-80B,
Qwen3-30B, DeepSeek-V4.1-Flash, Gemma-3-27B-IT served by API, Gemini 3.8 Flash, Gemini
3.1 Pro, Llama-3.3-70B, Mistral-Small-24B, grok-4.3 and Kimi-K3). Served models were not
deterministic at temperature zero and providers change the weights behind a model name
without notice, so these readings cannot be re-read exactly; they are reported as read,
each cell as a mean over its draws. due-care-eval can read the same cases from any of
these models today, and will measure the model as it is then served;
`replication/run_reading.py` compares such a reading with the paper's within each cell's
draw band. In `data/` these
are `fig1_panelB.csv`, `B2_*`, `B5_*`, `B8_*`, `table3_coverage.csv`, `fig7_duty*.csv`,
`B9_*`, `B10_*`, `B11_*`, `duty_*` and the `api` rows of `chef_home*.csv`.

## Provenance

Every CSV in `data/` carries, in its first comment line, the sha256 of the results
database it was exported from:

```
851c599ba656280971dede42e2ca67e3d5def98e3ed39fcc6273045f9dcfaec3
```

`paper_numbers.csv` carries the same sha in its first line.

The database itself is built by due-care-eval from fresh readings and is not distributed
here. Some CSV columns, and the SQL in `*_queries.sql` and `paper_numbers.csv`, name the
reading a value came from by a descriptive label (`deployed_scenarios`, `local_frames`,
`duty_remedies`, and so on); `replication/README.md` lists every label and the
replication reading that re-reads it. The labels replace the results database's internal
reading identifiers one for one, so the SQL documents each query's shape and is not
meant to be run as written. The bicycle scenario is `bicycle` throughout, as in the
eval.

Where a reason text quoted a provider's error message, the message is replaced
by "provider returned an error". Source-artefact paths that pointed into the working repository (for example a
reading's log or annotation file) are reduced to opaque labels: the file's name without
directory or extension. No numeric value is changed.

## Checking the numbers in the text

`check_paper_numbers.py` takes each number in `paper_numbers.csv`, locates its value in
the CSVs and checks it at the printed precision. Numbers the CSVs do not carry (counts,
words, and values computed only inside the database) are listed as not checkable, with
their count. The `query` column documents how each number was produced from the
database. The `location` column names where each number was registered and may follow an
earlier section and table numbering than the manuscript in `paper/`.

## Licence

The paper, the data and `paper_numbers.csv` are released under CC BY 4.0; the scripts
under the Apache License 2.0. See `LICENSES.md` and `LICENSE`.

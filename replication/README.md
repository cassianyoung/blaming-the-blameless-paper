# Replication

How to re-read the readings behind the paper with
due-care-eval (link added at release) and compare the fresh
readings with the values the paper reports.

| Path | What it is |
|---|---|
| `readings.json` | each reading the eval can re-read: what it is, the data labels it stands for, the paper outputs it feeds, and every run (model, task, frame, options) |
| `run_reading.py` | runs one reading and compares it with the paper |
| `models/` | the model table for every model the paper read: wire settings for the API models, pinned revisions and adapter digests for the local ones |
| `reference/paper_values.json` | the paper's values per model, scenario and duty pair, exported from the results database (its sha256 is in the file) |
| `reference/prompt_sha16.json` | the hashes of the prompts the study's reads sent |
| `compare.py` | compares Inspect logs with `reference/paper_values.json` |
| `test_roster.py` | checks the model table, and that the eval still renders the prompts the study sent |
| `acceptance/` | the acceptance runs: one API model and five local readings re-read and compared, with their logs and checksums |
| `later_readings/` | the readings the eval does not run (the reasoning traces, the practical syllogism and its premises, the duty syllogism, the general principle, the subject's name, the reasoning stratum): each with its frozen prompts checked against the study's calls, its code, and every call it made |

## Install

Install due-care-eval at the release the paper cites, with the local extras for local
readings, and run everything from the root of this repository:

```bash
git clone --branch v1.0 <due-care-eval repository URL> due-care-eval
python -m venv .venv && . .venv/bin/activate
pip install -e "due-care-eval[local]"
HF_HUB_OFFLINE=1 python replication/test_roster.py
```

`run_reading.py` points the eval's model table at `replication/models/` through
`DUE_CARE_MODELS`; to run one model by hand, set it yourself:

```bash
DUE_CARE_MODELS=replication/models inspect eval due_care/excuse \
    --model due_care/gemma9_base -T frame=worksheet
```

## The readings

The data in `../data/` label each value with the reading it came from. Each label below
is re-read by the reading named beside it.

| Reading | Data labels | Models | Feeds |
|---|---|---|---|
| `deployed_excuse` | `deployed_bicycle_ladder`, `deployed_bicycle_rivals`, `deployed_added_models`, `deployed_scenarios` | the 21 deployed models, by API, chat frame | Figure 1, Figure 2 panel B, Figure 3, Table B.1, Tables A.2, A.5 and A.8 |
| `deployed_duty` | `duty_pairs`, `duty_remedies`, `duty_hair_dye`, `duty_prawns_convention`, `duty_chef_home_comparison` | the 22 models read on the duty test, by API | Figures 4 to 7, Table A.4 (API rows), Table A.9 |
| `local_frames` | `local_frames` | each pretrained base, base with adapter and developer release on the worksheet; each release on chat | Figure 2 panel A, Figures 8 and 9, Tables A.1, A.3, A.4 (local rows), A.6 and A.7 (base, adapter and release rows) |
| `yi_adapter_controls` | `yi_adapter_controls` | the Yi-1.5-34B adapter controls on the worksheet, bicycle | Table A.7 (control rows) |

The deployed models' bicycle reading was taken in three passes: the core roles
(`deployed_bicycle_ladder`), the rival-excuse roles (`deployed_bicycle_rivals`) and a
full read of two models added later (`deployed_added_models`). The eval reads all ten
roles in one pass, so all three are re-read by the first half of `deployed_excuse`.
Likewise the duty test was read in stages (the pairs, the remedies, the hair-dye pair,
the prawns pair's convention, the chef against the home cook side by side), and the
eval's duty task reads every condition of every pair in one pass.

```bash
python replication/run_reading.py --list
python replication/run_reading.py local_frames --models gemma9_base,gemma9_adapter,gemma9_instruct
python replication/run_reading.py deployed_duty --plan      # the commands, without running them
python replication/run_reading.py deployed_excuse            # needs OPENROUTER_API_KEY
```

Each reading writes `replication_out/<reading>/logs/` and `comparison.md`. Local readings
are compared to the printed precision, two decimals. API readings are compared within
each cell's draw band, because the served model can change behind a stable name. A
reading of part of the duty test's pairs is compared on its gaps, while the pooled floor,
signal-to-noise and class are reported as not comparable. API reads stop at
`DUE_CARE_SPEND_CAP_USD` per process (default US$1.00), so raise it for a full deployed
reading.

**Hardware.** In bf16 the 7B to 12B families need a 24 GB card; Gemma 2 27B and
Yi-1.5-34B need an 80 GB card. The adapters are downloaded from Hugging Face (see
`../adapters/README.md`), and each is checked against its digest before it is merged.

## Not re-readable with the eval

These readings used frames or banks that are not in the eval. They are reported as read.
`readings.json` lists them under `not_rereadable`, with the reason for each.

| Data label | What it was |
|---|---|
| `local_tuning` | the first base, adapter and release reading of the bicycle, on an earlier bicycle bank (the `local_tuning_*` columns of `A1_tuning_table.csv` and `fig2_panelA.csv`) |
| `reasoning_traces` | the reasoning traces from the duty test's separate-case reads, coded by two LLM coders against a frozen guide (section 4.3) |
| `prevention_paraphrase` | the prevention question in other wordings (section 4.1.4) |
| `practical_syllogism` | the practical syllogism (section 4.1.4, Table A.10) |
| `syllogism_duty` | the role and the principle set out on the duty pairs (section 4.2, Table A.10) |
| `general_principle` | the general principle, asked in both orders (Table A.10) |
| `subject_identity` | the same cases with other subjects' names (section 4.1) |

The three-way side-by-side probabilities in `A4_chef_home_cmp3_probabilities.csv` come from
a question the eval does not ask.

The labels `duty_convention_pilot` and `duty_remedies_pilot` appear only in the
pre-registrations, as the pilots the remedy predictions were registered after; no value in
`../data/` comes from them.

## What has been re-read

`acceptance/ACCEPTANCE.md` records two acceptance runs. The first is one API model
(Llama-3.3-70B) on the bicycle and two duty pairs, with the prawns pair's full-text
side-by-side prompt read again through due-care-eval v1.1-rc2: 24 of 24 values within their
draw band.
The second is five local readings (Gemma 2 9B base on the worksheet, Gemma-2-9B-it on
chat, Llama 3.1 8B base on the worksheet, and Llama-3.1-8B-Instruct on both frames): 378
of 378 values equal at two decimals. The adapters were not part of either run.

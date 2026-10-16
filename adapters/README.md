# Adapters

These are LoRA adapters that let a **base** (pretrained-only) language model answer a
rating question. A base model asked a question in a plain `Q: ... A:` frame tends to
continue the page rather than answer: it writes the next exercise, a worksheet
instruction, or another question. Each adapter installs one convention and nothing
else: in this frame, the text after the question is the answer, given in the register
the question calls for (a single figure, a hedge, or "it depends" with the dependency
named).

The adapters are trained on a **morally blank** instruction corpus: arithmetic,
look-up questions, reading comprehension, general instructions and vague-predicate
items (*is someone 5'10" tall?*), filtered so that nothing in it judges an act or
touches morality, politics, sensitive personal matters or anyone's conduct. No
preference data and no refusal training are involved. The aim is a base model that
answers, read without the alignment layer of a vendor instruct model.

Each adapter is a LoRA adapter, not model weights. Using one requires its base
model, under that base model's own licence (listed below).

## Contents

| Path | What it is |
|---|---|
| `README.md` | this file |
| `adapters.json` | machine-readable version of everything below |
| `corpus/instruction_corpus_en.jsonl` | the instruction corpus the study adapters were trained on: 957 of its 960 pairs (see Withheld rows) |
| `corpus/instruction_corpus_zh.jsonl` | the Chinese instruction corpus the Chinese Yi-34B adapter was trained on: 810 of its 958 pairs (see The Chinese corpus and its translation) |
| `corpus/instruction_corpus_translated.jsonl` | the same corpus machine-translated into English, for the step-B Yi-34B adapters: 810 of its 958 pairs |
| `corpus/withheld_coig_cqia_rows.json` | the 148 COIG-CQIA rows withheld from each of the two, with their COIG-CQIA identifiers |
| `corpus/rebuild_training_corpus.py` | rebuilds the exact training corpora from the published files and their sources (Sentiment140; COIG-CQIA) |
| `corpus/instruction_corpus_en_heldout.jsonl` | the held-out slice of the same distribution (105 of 106 pairs published), used only to check that the format was learned |
| `corpus/SHA256SUMS` | sha256 of both corpus files |
| `recipe/school_tune_tune.py` | the trainer |
| `recipe/school_tune_instruments.py` | the fixed hyperparameter specifications, frame, composition and screening instruments, with their digests |
| `manifests/<adapter>.json` | one training manifest per adapter: hyperparameters as run, environment, boundary checks, loss, hashes, licence |
| `requirements.txt` | the Python environment the trainer was run under |

## The corpus

`corpus/instruction_corpus_en.jsonl`: 957 published pairs of the 960 trained (see Withheld rows below for both hashes);
`corpus/instruction_corpus_en_heldout.jsonl`, sha256
`0cf2a2dbe09739b59ccfcd1cdf09517863a5cedee1286fa3fc34b831d67f1814`, 106 pairs. Both
hashes match the training-set hash written into the training manifests.

Each line is one pair with fields `question`, `answer`, `prompt` (the question in the
frame `Q: {question}\nA:`), `completion` (a space and the answer), `text`
(`prompt + completion`), `kind_rated` (`determinate`, `graded` or `depends`),
`source`, and opaque `uid` and `sha`. Vague-predicate items also carry
`predicate_kind`, `shape`, `sweep` and `value`.

**How it was built.** Candidate pairs were drawn from public datasets plus
vague-predicate items written for this project; a keyword filter dropped any line
touching moral, legal, political or sensitive vocabulary; every surviving line was
screened by two LLM raters from different labs, and a line flagged by either was
excluded (agreement gated on Gwet's AC1 at 0.60); each pair's answer kind was then
labelled by two raters. The set was composed over answer kinds in a fixed
proportion, **determinate 0.50, graded 0.35, depends 0.15**, so that the tune
cannot teach crispness by construction, and 10 per cent of each kind was held out.
The filter, screen prompt, raters, proportion and frame are the constants in
`recipe/school_tune_instruments.py` (instruments digest `eb31016eac8a3b3e`). The
upstream pulling and API screening code is not included here; the corpus is shipped
as the frozen file the adapters were trained on.

**Sources in the 960 training pairs:** Dolly 371, Alpaca 278, project-authored
vague-predicate items 191, GSM8K 46, Natural Questions (open) 38, SQuAD 25, FLAN 11.

**Licences: no single licence covers the corpus.** Every published row carries its own
licence as its last field, `"licence": {"id": <SPDX identifier>, "source": <URL where
that licence is declared>}`; the training rows did not carry it, and
`corpus/rebuild_training_corpus.py` removes it before rebuilding them. Each row keeps the
licence of the dataset it came from, read on 2026-10-10 from each dataset card at the
revision the corpus was built from ([`corpus_source_licences.json`](corpus_source_licences.json)):

| source | dataset | licence | training rows | held-out rows |
|---|---|---|---|---|
| `dolly` | `databricks/databricks-dolly-15k` | CC BY-SA 3.0 (share-alike) | 371 | 42 |
| `alpaca` | `tatsu-lab/alpaca` | **CC BY-NC 4.0 (non-commercial)**; outputs generated by OpenAI `text-davinci-003` | 278 | 24 |
| `gsm8k` | `openai/gsm8k` | MIT | 46 | 6 |
| `nq_open` | `google-research-datasets/nq_open` | CC BY-SA 3.0 (share-alike) | 38 | 5 |
| `squad` | `rajpurkar/squad` | CC BY-SA 4.0 (share-alike) | 25 | 2 |
| `flan` | `Muennighoff/flan` | **per row**: none declared for the collection, so each row carries its underlying dataset's licence (below) | 11 trained, 8 published | 1 trained, 0 published |
| `predicate_*` | authored for this project | CC BY 4.0 | 191 | 26 |

Share-alike and non-commercial terms cannot both be met by one licence for the whole,
so the corpus is published as a collection: each row under its source's licence.

The corpus records only `flan` as the source of its FLAN rows, so each was traced by an
exact match of its question and answer against the train files of `Muennighoff/flan` at
`049702ca5ffc`: all 12 match exactly one line of one task file, and the task file names
the underlying dataset. Each row carries that dataset's licence; the instruction
templates around it are FLAN's own (`google-research/FLAN`, Apache-2.0).

| underlying dataset | FLAN rows | licence | published |
|---|---|---|---|
| SQuAD 2.0 | `st-009696`, `st-019836`, `st-022147` | CC BY-SA 4.0 | 3 |
| SNLI | `st-001463` | CC BY-SA 4.0 | 1 |
| DROP | `st-024338` | CC BY-SA 4.0 | 1 |
| WebNLG (English) | `st-022078` | **CC BY-NC-SA 4.0** (non-commercial, share-alike) | 1 |
| ReCoRD, CNN/Daily Mail portion | `st-015726` | Apache-2.0 | 1 |
| WNLI (Winograd Schema Collection, schema 65) | `st-024753` | CC BY 4.0 | 1 |
| Sentiment140 | `st-012534`, `st-009490`, `st-002318`; held out `st-003093` | none permitting redistribution | 0: withheld (see Withheld rows) |

The file, line and basis for each licence are in `corpus_source_licences.json`
(`flan_rows`).

**The adapters are for research use.** They were trained on data including
non-commercially licensed rows (Alpaca, 278 of 960) and share-alike rows; whether those
terms bind weights trained on the data is unsettled, and the adapters are released as
research artefacts for research use only, in addition to each base model's licence.

Three further training sets were used for the Yi-1.5-34B comparison adapters. Two are
shipped without their COIG-CQIA rows (see The Chinese corpus and its translation): a
Chinese set (`zh_corpus`, training sha256
`bf17099b553052d4e761aa24b189a92529670102427dddd15e3d761c60e34bb3`) and its English
translation (`translated_corpus`, training sha256
`9960d267b196ab0df6bf7477e660916ee4ea7f84440614f5d58ef253ce76d3ec`). The third, the
shipped set with its prose-judgement items replaced (`no_prose_corpus`, sha256
`2eae242c351c6f9e605723a490e0802d69d11bf9f93a369a0fdf45d0d9d8f608`), is **not**
shipped.

## The recipe

Every published adapter uses LoRA specification **v2** (`LORA_V2` in
`recipe/school_tune_instruments.py`, digest `89b8d51ca119be9a`). The values are fixed
in that file; the trainer has no flags for them.

| Hyperparameter | Value |
|---|---|
| LoRA rank `r` | 32 |
| `lora_alpha` | 64 |
| `lora_dropout` | 0.05 |
| bias | none |
| target modules | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` (all seven, in every adapter) |
| rsLoRA, DoRA, `modules_to_save`, rank or layer patterns | none |
| task type | `CAUSAL_LM` |
| epochs | 2 |
| optimizer steps | 120 (960 pairs at effective batch 16 is 60 steps per epoch) |
| per-device batch x gradient accumulation | 4 x 4 = effective batch 16 |
| learning rate | 1e-4, cosine schedule |
| warmup | ratio 0.03 of training, i.e. 4 steps |
| maximum sequence length | 512 tokens (no training pair reaches it) |
| precision | bf16, gradient checkpointing on |
| seed | 20260909 (see below) |
| frame | `Q: {question}\nA:` |
| loss | answer tokens only: prompt tokens masked with -100, EOS appended to every pair |

The trainer locates the prompt/answer boundary with the tokeniser's character
offsets and asserts on every pair that no token straddles the boundary, that the
prompt's tokenisation is a prefix of the pair's, that the boundary falls on a token
start, and that the unmasked tokens map back to exactly the completion. The counts
are recorded in each manifest under `boundary_checks`.

**Declared exceptions.** `yi34b_translated_2048` was trained at maximum sequence length
2048 with per-device batch 1 and gradient accumulation 16 (effective batch
unchanged), because its translated pairs are longer. The three seed replicates use
seeds 20260909, 20260910 and 20260911. Each override is recorded in that adapter's
manifest beside the unchanged specification digest.

**The seed.** In the current trainer the seed is set before the adapter is built, so
it governs the LoRA initialisation as well as data order and dropout. The eight study
adapters, the Yi-34B Chinese-set adapter and `yi34b_en_corpus` were trained by an
earlier revision of the trainer that applied the seed only when the `Trainer` was
constructed, after `get_peft_model` had already initialised `lora_A` from torch's
default generator. For those ten adapters the recorded seed governed data order and
dropout but not initialisation, so they cannot be reproduced bit for bit; each
manifest says so under `seed_governs_adapter_initialisation`. The three Yi-34B seed
replicates (and the three translated and no-prose Yi adapters) were trained with the
seed applied first. A retrained adapter should therefore be checked against the band
the three seed replicates span, not for bitwise equality. The earlier revision used
the same specification, frame and answer-only loss masking; its boundary checks (no
straddling tokens, prefix property, decode round-trip) are recorded in each
manifest.

**Running it.** Install `requirements.txt` plus a torch build that matches your GPU,
then, from this directory:

```
python recipe/school_tune_tune.py --run my_gemma9 --lora v2 --corpus en \
    --base-model google/gemma-2-9b --seed 20260909
```

`--corpus` names a corpus in `corpus/`: `en` reads `instruction_corpus_en.jsonl` and its
held-out slice `instruction_corpus_en_heldout.jsonl`; `zh` and `translated` have no
held-out slice of their own, so pass `--heldout-corpus en`, as their adapters were
trained. To train on the exact training corpora, rebuild them first with
`corpus/rebuild_training_corpus.py` (see Withheld rows) and copy the rebuilt files over
the published ones in `corpus/`; the trainer reads that directory.

`--dry-run` substitutes a tiny Gemma-architecture model on CPU and exercises the
whole path, including the boundary assertions, in about a minute. Output goes to
`runs/<run>/adapter` and `runs/<run>/results/school_tune_tune.json`. Pass
`--trust-remote-code` for bases that need it (the Yi adapters were trained with it).

## The adapters

### Two digests per adapter

- **`adapter_sha256`** is the sha256 of `adapter_model.safetensors` alone. Hash that
  one file to check you have the right weights.
- **`adapter_expect_digest`** is the sha256 over the concatenated contents of
  `adapter_config.json` and the adapter weights (`adapter_model.safetensors`, or
  `adapter_model.bin`) in sorted filename order, first 16 hex characters. This is the
  figure the paper's tables quote, and the one due-care-eval checks before loading an adapter.
  Any other file in the repository, such as a training manifest or a README, is not part
  of the digest.

The two are not interchangeable.

### The eight study adapters (Table 5)

All trained on `corpus/instruction_corpus_en.jsonl` with the recipe above and seed
20260909.

| Family | Base model | Hugging Face repository | `adapter_expect_digest` | `adapter_sha256` |
|---|---|---|---|---|
| gemma9 | `google/gemma-2-9b` | [Cassian/gemma-2-9b-due-care-adapter](https://huggingface.co/Cassian/gemma-2-9b-due-care-adapter) | `15ac53501d7e2468` | `f4ae45622124103166b727ca907c40a81d21db8394d851e8e232e4405de1aa33` |
| gemma27 | `google/gemma-2-27b` | [Cassian/gemma-2-27b-due-care-adapter](https://huggingface.co/Cassian/gemma-2-27b-due-care-adapter) | `5f8f36a73d5b9e45` | `4105b099089f6856f370ca5445a4cbc3910aa839adcc3cd358d176e32b9ccbf0` |
| llama31 | `meta-llama/Llama-3.1-8B` | [Cassian/Llama-3.1-8B-due-care-adapter](https://huggingface.co/Cassian/Llama-3.1-8B-due-care-adapter) | `2b91053a0a8d4bb8` | `d17bbcbeb5051b195ba560f029cb63751b1ba832ddfadb612d544a4408cf96aa` |
| qwen3 | `Qwen/Qwen3-8B-Base` | [Cassian/Qwen3-8B-Base-due-care-adapter](https://huggingface.co/Cassian/Qwen3-8B-Base-due-care-adapter) | `b99b83198da17ff6` | `0348423f9295f261c937e63e22a5ebf175d36a0aff14136d5477c442287c77b4` |
| mistral | `mistralai/Mistral-7B-v0.3` | [Cassian/Mistral-7B-v0.3-due-care-adapter](https://huggingface.co/Cassian/Mistral-7B-v0.3-due-care-adapter) | `ab7af6e68e4449ea` | `4a62c0ce162c13b9ee95eab8cd5382ae4689e8151c945982f2fcc3640ae9b305` |
| olmo2 | `allenai/OLMo-2-1124-7B` | [Cassian/OLMo-2-1124-7B-due-care-adapter](https://huggingface.co/Cassian/OLMo-2-1124-7B-due-care-adapter) | `43b6ac382f09e5bd` | `2d3206285ae4227bfa22b8e6845ec049643d517576a33b358446c131b0889d17` |
| falcon3 | `tiiuae/Falcon3-7B-Base` | [Cassian/Falcon3-7B-Base-due-care-adapter](https://huggingface.co/Cassian/Falcon3-7B-Base-due-care-adapter) | `66aeabc07ce5f4f7` | `1a7b15acf7f731a92a79a3ef5c03a7bcbf735696e4125693bc89b52fe3c2f176` |
| stablelm12b | `stabilityai/stablelm-2-12b` | [Cassian/stablelm-2-12b-due-care-adapter](https://huggingface.co/Cassian/stablelm-2-12b-due-care-adapter) | `07920c80c74c5dca` | `da9f91977905a718242aa12260d8cf8f2e2d6a82ebee28715f3fb2b119dc9788` |
### The Yi-1.5-34B adapters

Base model `01-ai/Yi-1.5-34B` (Hub revision `58a29f6dca2a4eda38821c086c29c1906114aabb`,
resolved at train time for every adapter except `yi34b_zh`).

- `yi34b_zh`: trained on the Chinese set.
- `yi34b_en_corpus`: trained on the shipped English set before the seed was applied
  ahead of initialisation; an uncontrolled draw, read beside the three seed
  replicates and never instead of them.
- `yi34b_en_corpus_s20260909`, `_s20260910`, `_s20260911`: the shipped English set at
  three declared seeds, the seed governing initialisation; together they give the
  band a retrained adapter should land in.
- `yi34b_translated_512`, `yi34b_translated_2048`: the Chinese set translated into English, at
  maximum sequence length 512 and 2048.
- `yi34b_no_prose`: the shipped English set with its prose-judgement items replaced.

| Adapter | Training set | Seed | Hugging Face repository | `adapter_expect_digest` | `adapter_sha256` |
|---|---|---|---|---|---|
| yi34b_zh | `zh_corpus` | 20260909 | [Cassian/Yi-1.5-34B-due-care-adapter-zh](https://huggingface.co/Cassian/Yi-1.5-34B-due-care-adapter-zh) | `4c96ef616f13b3c4` | `aa16afa733061c2158e40b0cd4b75b82c6420eeae399dd8b64225ffb178d3d5d` |
| yi34b_en_corpus | `en_corpus` | 20260909 | [Cassian/Yi-1.5-34B-due-care-adapter-en](https://huggingface.co/Cassian/Yi-1.5-34B-due-care-adapter-en) | `e2465c9d89ab67e8` | `81db88728933c891693d5f060efd1703abdcd0035d9559310a86033ccee74ae6` |
| yi34b_en_corpus_s20260909 | `en_corpus` | 20260909 | [Cassian/Yi-1.5-34B-due-care-adapter-en-seeds / `s20260909`](https://huggingface.co/Cassian/Yi-1.5-34B-due-care-adapter-en-seeds/tree/main/s20260909) | `d101c0eb4fcf9c6a` | `ca9ac2aedfbe9f1c74829e905b6fba42360176de960767e1f51c92926c31c9a3` |
| yi34b_en_corpus_s20260910 | `en_corpus` | 20260910 | [Cassian/Yi-1.5-34B-due-care-adapter-en-seeds / `s20260910`](https://huggingface.co/Cassian/Yi-1.5-34B-due-care-adapter-en-seeds/tree/main/s20260910) | `cbd086d8d21a6415` | `080e3eec936891891a7f979abf06f31f0225478e30b7b5323d73f7009fd99d9c` |
| yi34b_en_corpus_s20260911 | `en_corpus` | 20260911 | [Cassian/Yi-1.5-34B-due-care-adapter-en-seeds / `s20260911`](https://huggingface.co/Cassian/Yi-1.5-34B-due-care-adapter-en-seeds/tree/main/s20260911) | `87a6a30f63718de7` | `c49b47e69e70b934da14d928b5a59759adc1a0724d410806726504e050dc4a6f` |
| yi34b_translated_2048 | `translated_corpus` | 20260909 | [Cassian/Yi-1.5-34B-due-care-adapter-controls / `translated_2048`](https://huggingface.co/Cassian/Yi-1.5-34B-due-care-adapter-controls/tree/main/translated_2048) | `bd8ee5309c9328d0` | `7deaa751fecf3792f620aa945fe7637c56db8ce4ecb8d3887af9299d7b46d429` |
| yi34b_translated_512 | `translated_corpus` | 20260909 | [Cassian/Yi-1.5-34B-due-care-adapter-controls / `translated_512`](https://huggingface.co/Cassian/Yi-1.5-34B-due-care-adapter-controls/tree/main/translated_512) | `3cabc8c64c2db3e4` | `046d4aa337664d275f521b1d6d3551a3a94d81a7ee5ebfaab5193b24acd0760d` |
| yi34b_no_prose | `no_prose_corpus` | 20260909 | [Cassian/Yi-1.5-34B-due-care-adapter-controls / `no_prose`](https://huggingface.co/Cassian/Yi-1.5-34B-due-care-adapter-controls/tree/main/no_prose) | `38dbe97e09b2f7bc` | `8ad93f3fd432d97e7fe4ccf709806fd93de561b59ebc0c7c7545dc1c05dff77d` |

### Base-model licences

Read on 2026-10-10 from each base model's card and from every licence, notice and
use-policy file in its repository, at the revision the adapters were trained on.
Licence texts that live outside the repository were read at the URL the card links.
The full record, with the SHA-256 of each licence file read and the obligations below,
is [`base_model_licences.json`](base_model_licences.json).

| Base model | Licence | Licence text | Commercial use |
|---|---|---|---|
| `google/gemma-2-9b` | Gemma Terms of Use | https://ai.google.dev/gemma/terms | not addressed in the terms read; subject to the Prohibited Use Policy |
| `google/gemma-2-27b` | Gemma Terms of Use | https://ai.google.dev/gemma/terms | not addressed in the terms read; subject to the Prohibited Use Policy |
| `meta-llama/Llama-3.1-8B` | Llama 3.1 Community License Agreement | https://huggingface.co/meta-llama/Llama-3.1-8B/blob/d04e592bb4f6aa9cfee91e2e20afa771667e1d4b/LICENSE | permitted, subject to the agreement (s2: a licensee whose products had more than 700 million monthly active users on the release date must request a licence from Meta) |
| `Qwen/Qwen3-8B-Base` | Apache License 2.0 | https://www.apache.org/licenses/LICENSE-2.0 | permitted |
| `mistralai/Mistral-7B-v0.3` | Apache License 2.0 | https://www.apache.org/licenses/LICENSE-2.0 | permitted |
| `allenai/OLMo-2-1124-7B` | Apache License 2.0 | https://www.apache.org/licenses/LICENSE-2.0 | permitted |
| `tiiuae/Falcon3-7B-Base` | TII Falcon License, December 2024 (the card names it "TII Falcon-LLM License 2.0") | https://falconllm.tii.ae/falcon-terms-and-conditions.html | royalty free, no commercial restriction in the text read |
| `stabilityai/stablelm-2-12b` | Stability AI Community License Agreement (last updated 5 July 2024) | https://huggingface.co/stabilityai/stablelm-2-12b/blob/74dd3f536b71d18aa122a11af0d1b83105cb2d38/LICENSE.md | RESTRICTED: research and non-commercial use free; commercial use requires registration with Stability AI, and every licence terminates if the licensee's annual revenue exceeds US$1,000,000 (s3) |
| `01-ai/Yi-1.5-34B` | Apache License 2.0 | https://www.apache.org/licenses/LICENSE-2.0 | permitted |

Each adapter is a derivative of its base model and is distributed under that base
model's licence. **What each licence requires of anyone distributing an adapter:**

- **Gemma 2 (9B and 27B)** (Gemma Terms of Use): provide a copy of the Gemma Terms of Use to recipients (s3.1); include the s3.2 use restrictions (the Gemma Prohibited Use Policy) as an enforceable provision and tell recipients they apply; mark modified files as modified; ship a "Notice" text file reading: "Gemma is provided under and subject to the Gemma Terms of Use found at ai.google.dev/gemma/terms"; no use of Google marks.
- **`meta-llama/Llama-3.1-8B`** (Llama 3.1 Community License Agreement): provide a copy of the agreement with the adapter (s1.b.i); prominently display "Built with Llama" (s1.b.i); begin the name of any distributed model trained from Llama with "Llama" (s1.b.i); ship a "Notice" text file reading: "Llama 3.1 is licensed under the Llama 3.1 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved." (s1.b.iii); comply with the Acceptable Use Policy (USE_POLICY.md).
- **`Qwen/Qwen3-8B-Base`** (Apache License 2.0): provide a copy of the Apache License 2.0; mark modified files; retain notices.
- **`mistralai/Mistral-7B-v0.3`** (Apache License 2.0): provide a copy of the Apache License 2.0; mark modified files; retain notices.
- **`allenai/OLMo-2-1124-7B`** (Apache License 2.0): provide a copy of the Apache License 2.0; mark modified files; retain notices.
- **`tiiuae/Falcon3-7B-Base`** (TII Falcon License, December 2024 (the card names it "TII Falcon-LLM License 2.0")): provide a copy of the licence to recipients (s4.1.2); include the Acceptable Use Policy as enforceable use-based restrictions (s4.1.1, s5); mark modified files (s4.1.3) and retain notices (s4.1.4); state prominently: "[name of the derivative] is built using artificial intelligence technology from the Technology Innovation Institute" (s6.1); no use of TII marks (s8.1).
- **`stabilityai/stablelm-2-12b`** (Stability AI Community License Agreement (last updated 5 July 2024)): provide a copy of the agreement to recipients (s4.a.i); ship a "Notice" text file reading: "This Stability AI Model is licensed under the Stability AI Community License, Copyright © Stability AI Ltd. All Rights Reserved" (s4.a.ii); prominently display "Powered by Stability AI" (s4.a.iii); comply with the Acceptable Use Policy (s4.b).
- **`01-ai/Yi-1.5-34B`** (Apache License 2.0): provide a copy of the Apache License 2.0; retain the NOTICE; include the attribution the NOTICE asks for: "This work is a derivative of Yi-1.5-34B by 01.AI, used under the Apache 2.0 License.".

**Before the adapter repositories are made public**, each must carry what its licence
requires: a copy of the licence, the required Notice file and attribution, and the use
policy where the licence passes one on. The Llama 3.1 licence also requires that a
distributed model trained from Llama have a name beginning with "Llama"; the Llama
adapter's repository was renamed accordingly, to `Cassian/Llama-3.1-8B-due-care-adapter`. The StableLM 2 adapter carries the base model's
commercial restriction (registration, and a US$1,000,000 revenue ceiling).

### Weights hashes: what was recorded, and where

Every adapter listed above has an `adapter_sha256` on record. How it came to be
recorded differs:

- **Written by the trainer at train time** (in the training manifest's provenance
  block): `yi34b_en_corpus`, the three seed replicates, `yi34b_translated_512`,
  `yi34b_translated_2048` and `yi34b_no_prose`.
- **Computed after training, from the published bytes**: the eight study adapters and
  `yi34b_zh`, which were trained before the trainer wrote a provenance block. For six
  study adapters the hash was checked against the Hub's own content hash at
  publication; for `gemma9` and `gemma27` it was read from the Hub's content hashes.
  Where the weights are also held locally (all except `gemma27`), they were re-hashed
  for this export and match.

**Three adapters whose readings link to their weights by label in the database:**
`yi34b_translated_512`, `yi34b_translated_2048` and `yi34b_no_prose` (the translated-English and
no-prose Yi-34B adapters). Their weights hashes are recorded in their training manifests,
which are also published in the repository's `manifests/` folder, and the weights re-hash
to them. The per-cell reading files taken through these adapters record the same adapter
digest. The aggregated records that the results database ingests carry the adapter's run
label rather than its hash, so within the database the link from a reading to its weights
rests on the label; each of the three labels maps to exactly one manifest and one digest.
Each of the three manifests carries a `reading_link_note` saying so.

### Withheld rows

The published corpus omits four rows that the training corpus contained: tweets drawn
from Sentiment140 through FLAN, whose licence does not clearly permit redistribution.
The adapters were trained on the corpus with them (training set sha256
`8df234ca2d836eeb51d750e9800e8564efc69c653f4181b5c0aeb9f0ac26f87f`, 960 rows; held-out set sha256
`0cf2a2dbe09739b59ccfcd1cdf09517863a5cedee1286fa3fc34b831d67f1814`, 106 rows), which the training manifests
record. The published files are `366cc002bad1e55d4cb506843927ff1956eac3a5ac3fc7cf36fde13a2d7cc20b` (957 rows) and
`09e6d843bdfdb0fb1c7c6d4ef947f1bd9422741cb6ee803c49fb7a7260ccec13` (105 rows).

Each withheld row is identified below by its corpus `uid` and row `sha`, its prompt
template (`{tweet}` is the tweet's text) and the tweet's id and polarity in Sentiment140's
`training.1600000.processed.noemoticon.csv` (polarity 0 negative, 4 positive).
`corpus/rebuild_training_corpus.py` takes that file, puts each row back at its original
line and checks that the two rebuilt files hash to the training corpus's SHA-256; checked
here, it reproduces both exactly. Exact rebuild depends on the source datasets remaining available in the same form; the rebuild script checks each training hash and refuses if a source has changed.

| uid | set | row sha | kind_rated | question | answer | Sentiment140 tweet id | polarity |
|---|---|---|---|---|---|---|---|
| `st-012534` | training | `ebf68d8348bdbc78` | depends | `Write a positive tweet.` | `{tweet}` | 1754878271 | 4 |
| `st-009490` | training | `8ffa7551db882f47` | depends | `Write a tweet that is positive.` | `{tweet}` | 1975723354 | 4 |
| `st-002318` | training | `cb684973b39e82d8` | determinate | `Generate a tweet that has the following sentiment: negative` | `{tweet}` | 1564929931 | 0 |
| `st-003093` | held-out | `047caa4cd1cf7e8e` | determinate | `Tweet: {tweet} Predict the sentiment of this tweet. OPTIONS: - negative - positive` | `positive` | 2014762793 | 4 |

### The Chinese corpus and its translation

The Chinese Yi-34B adapter was trained on `corpus/instruction_corpus_zh.jsonl` (958
pairs: 619 from Chinese Alpaca, 148 from COIG-CQIA, 191 rating items written for the study),
and the two step-B Yi-34B adapters on `corpus/instruction_corpus_translated.jsonl`, the same
rows machine-translated into English. **COIG-CQIA declares no licence and its rows are
user-written text from Chinese platforms, so its 148 rows (15.4% of each corpus) are
withheld from both.** Chinese Alpaca is treated as CC BY-NC 4.0, the stricter of the two
licences its card states (its metadata says CC BY 4.0, its text CC BY-NC 4.0 and research
use only).

| corpus | training sha256 | training rows | published sha256 | published rows | withheld |
|---|---|---|---|---|---|
| Chinese | `bf17099b553052d4e761aa24b189a92529670102427dddd15e3d761c60e34bb3` | 958 | `c22c01d50a389974377920431217618e21fb01b34444078d50172d931f09e3f0` | 810 | 148 |
| translated | `9960d267b196ab0df6bf7477e660916ee4ea7f84440614f5d58ef253ce76d3ec` | 958 | `1de5cfee2dae23c29fe5b57a4a1e7d8ab4d6b7402a3deec3e07135054c7b8e72` | 810 | 148 |

Each withheld row is identified in `corpus/withheld_coig_cqia_rows.json` by its line in the
training corpus, its COIG-CQIA file and line at dataset commit `8b55868c6168adf86c30e7ca0f782cca1c514297`, its non-text
fields, and the sha256 of the training line. **The Chinese corpus can be rebuilt exactly**:
each withheld row is COIG-CQIA's `instruction` as its question and `output` as its answer,
stripped of surrounding whitespace, and `rebuild_training_corpus.py chinese` restores the
training file from a checkout of COIG-CQIA at that commit; checked here, it reproduces the
training hash. **The translated corpus cannot be rebuilt from public sources**: its withheld
rows carry English translations, made for this study by machine translation, of text that
may not be redistributed, so they are neither published nor regenerable exactly. The
recorded line hashes let anyone holding a withheld line verify it. Exact rebuild depends on the source datasets remaining available in the same form; the rebuild script checks each training hash and refuses if a source has changed.

### Manifests

`manifests/<adapter>.json` is each adapter's training manifest, reduced to what
describes the training: the base model (and its Hub revision where it was resolved at
train time), training and held-out sets with their hashes, the hyperparameters as run,
steps, final loss, train time, trainable and total parameter counts, dtype, the
environment observed (`python`, `torch`, `transformers`, `peft`), the
`requirements_digest`, the tokeniser boundary checks, the seed and whether it governed
initialisation, both digests with their definitions and sources, and the licence.
`source_manifest_sha256` is the sha256 of the full train-time manifest it was reduced
from. The Hub repositories carry their own `training_manifest.json`. The
specification's own `base_model` field reads `google/gemma-2-9b` for every adapter;
it is the specification's default, not the adapter's base, which is `base_model`
in each manifest and `base_model_name_or_path` in each `adapter_config.json`.

### Loading an adapter

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = "google/gemma-2-9b"
tok = AutoTokenizer.from_pretrained(base)
model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.bfloat16)
model = PeftModel.from_pretrained(model, "Cassian/gemma-2-9b-due-care-adapter")
# for an adapter in a subfolder:
#   PeftModel.from_pretrained(model, "Cassian/Yi-1.5-34B-due-care-adapter-en-seeds",
#                             subfolder="s20260910")
prompt = ("Q: On a scale from 0 to 9, where 0 means not at all tall and 9 means extremely tall, "
          "how tall is someone 69.5 inches tall? Answer with one digit.\nA:")
ids = tok(prompt, return_tensors="pt").to(model.device)
out = model.generate(**ids, max_new_tokens=4, do_sample=False)
print(tok.decode(out[0, ids["input_ids"].shape[1]:]))
```

Read the model in the frame it was tuned in, `Q: {question}\nA:`.

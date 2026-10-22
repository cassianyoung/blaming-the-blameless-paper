# Licences

| Material | Licence |
|---|---|
| The paper (`paper/`), the data (`data/`, every CSV and the SQL documentation files), `paper_numbers.csv`, `MEASUREMENT_NOTES.md`, the pre-registrations (`pre-registration/`), the reference values and prompt hashes (`replication/reference/`), `replication/readings.json`, the acceptance records and their Inspect logs (`replication/acceptance/`), the later readings' prompts, calls, records and READMEs (`replication/later_readings/`, except their code) and the adapter documentation and manifests (`adapters/*.md`, `adapters/*.json`, `adapters/manifests/`) | Creative Commons Attribution 4.0 International (CC BY 4.0), full text in [`LICENSE-DATA`](LICENSE-DATA) |
| The scripts: `paperlib.py`, `check_paper_numbers.py`, everything under `figures/` and `tables/`, the replication scripts (`replication/*.py`) and model table (`replication/models/`), the later readings' code (`replication/later_readings/*/code/`, `replication/later_readings/common/`), and the adapter recipe and corpus scripts (`adapters/recipe/`, `adapters/corpus/rebuild_training_corpus.py`) | Apache License 2.0, full text in [`LICENSE`](LICENSE) |
| The instruction corpus under `adapters/corpus/` | no single licence: each row states its own in its `licence` field, an SPDX identifier and the URL where that licence is declared (Dolly and Natural Questions CC BY-SA 3.0; SQuAD CC BY-SA 4.0; Alpaca and Chinese Alpaca CC BY-NC 4.0; GSM8K MIT; FLAN rows their underlying datasets' licences; rows from Sentiment140 and COIG-CQIA are withheld). The rows authored for this project are CC BY 4.0, [`LICENSE-DATA`](LICENSE-DATA). See `adapters/corpus_source_licences.json` |
| Adapter weights (hosted on Hugging Face, linked from `adapters/README.md`) | each adapter is released under the licence of the base model it was trained on (see `adapters/base_model_licences.json`), and for research use only, because the training corpus includes non-commercially licensed rows |

Copyright the authors of "Blaming the Blameless".

Under CC BY 4.0 you may share and adapt the paper and the data for any purpose,
provided you give appropriate credit, link to the licence and indicate whether
changes were made.

An adapter is a derivative of its base model, so its use is bound by that base
model's terms (some of which restrict use or require attribution) as well as by
anything stated here. Check the base model's licence before using an adapter.

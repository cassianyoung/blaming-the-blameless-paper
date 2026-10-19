# Pre-registrations

The pre-registrations and amendments behind the excuse test, the duty pairs, the
remedies, the adapter controls and the later readings (whose prompts, code and calls are in
`../replication/later_readings/`). Each was committed before the readings it governs;
each amendment states whether it was made before or after the cells it affects landed.

The texts are as banked. They are edited only to remove internal file paths and process
narrative (who ruled, costs, infrastructure); predictions, rules, thresholds, bank
SHA-256s and the amendments themselves are unchanged. The working repository's run numbers
are replaced, one for one, by the descriptive reading labels used throughout this
repository (see `../replication/README.md`), and prediction identifiers follow them
(`duty_hair_dye.P1` for the hair-dye pair's first prediction). Pair 2 (herbal medicine)
appears in the duty texts as pre-registered; it was later retired from the paper (see
`duty_pair7_hair_dye.md`) and is not in due-care-eval's banks.

They use "agent" for the person in each case, the term in use when they were written; the
paper calls the same person the subject. No prediction, rule or number has been changed.

| file | what it pre-registers |
|---|---|
| `duty_pairs_stated_vs_separate.md` | The duty test on five professional-against-private pairs plus an identical-case control: the professional is blamed more both under comparison and separately; the per-arm noise floor from the control; when a convention counts as stated; the APPLIED / PARTLY APPLIED / NOT APPLIED verdicts. |
| `duty_pairs_verdict_rule_amendment.md` | Amendment to that verdict rule: the tie-break where a separate gap is within one band of both the stated gap and zero, the LOW RESOLUTION flag, and the `EXACT_ZERO_COMPARISON` and `HEADROOM` flags. |
| `duty_remedies.md` | The remedies: how far a stated convention, a comparand case and a neutral sentence restore the gap withheld when cases are judged alone, with the predicted direction and ordering. Includes Amendment 1 (neutral-sentence word counts) and Amendment 2 (the sentence-noise floor, and the neutral baseline as the mean of three neutral readings). |
| `duty_pair7_hair_dye.md` | The hair-dye pair (pair 7) that replaces the retired herbal pair: its texts, convention and neutral sentences, the harm nouns for the CAUSE question, and predictions duty_hair_dye.P1 to duty_hair_dye.P6 measured as Amendment 2 measures them. |
| `excuse_duty_holder_factorial.md` | A test on the excuse test's careless subject: whether who held the duty (lend, hire or sell the same bicycle) sets the blame, registered on material not used to form the hypothesis. The relationship-factor rows it names are not part of the public banks. |
| `excuse_neutral_row_flag_amendment.json` | Post-hoc amendment, declared as one, to the excuse test's neutral-row check: the neutral row exists to rule out the sentence-count rival (P1_neutral above P1), not to be inert; its movement against P0 is reported, gating nothing. |
| `adapter_corpus_controls.md` | Controls for whether the instruction-tuning corpus behind a LoRA adapter, rather than seed or language, moves the careful subject's reading on the worksheet frame: seed replication, a language control and an ablation, with the rise rule and its two amendments (§8, §9). |
| `adapter_corpus_controls_bands_amendment.md` | Amendment fixing which construction the rise rule's "bands" means (the pooled band, C), with the reason and its effect on every arm. |
| `reasoning_traces.md` | The reasoning traces: the six reasoning models' duty-test separate cases re-read with their reasoning kept, and coded by two model coders for whether the reasoning raises the professional comparison; the coding guide and its rules. |
| `prevention_paraphrase.md` | The prevention and carelessness questions re-read in their original wording (the syllogism's particular premise), and rewordings of the prevention question, which are not reported because they measured the verdict, not the fact. |
| `practical_syllogism.md` | The practical syllogism on the excuse test: the universal premise asked with no case, against the particular premise and the verdict, each from its own call; and fact, rule and verdict asked in one answer. |
| `syllogism_duty.md` | The duty test's syllogism: the role and the principle per named pair, the same-session bare re-read, and the one-answer prompt; with the split and shortfall amendments. |
| `general_principle.md` | The convention asked in the abstract, with no trade named, in both orders. |
| `subject_identity.md` | The excuse and duty cases re-read with the subject named Alaric, John or Jane. |
| `completeness_fill_amendment.md` | The completeness fill: the readings added for due-care-eval v1.1, the prawns pair read under the duty syllogism (pooled with it), and the reasoning stratum (read on the reasoning models, reported separately). |

## Bank file names

The pre-registrations name their banks by the working repository's file names, as
registered. This table says where each bank's texts are published: in due-care-eval at tag
v1.1, under `banks/`. Every row of a public bank records the SHA-256 of the bank it came
from (`source_bank_sha256`), and each correspondence below was also checked text for text.

| name in the pre-registrations | cited in | sha256 | published in due-care-eval v1.1 | not published |
|---|---|---|---|---|
| `excuse_bank.jsonl` | `excuse_duty_holder_factorial.md` | `546dc93105fadf74…` | `excuse_cases.jsonl`: the ten bicycle cases | |
| `moral__factors__b1__rev1.jsonl` | `excuse_duty_holder_factorial.md` | `e8de6ecf0fe6dcb1…` | three rows only, the lend level's N, C and I, which are the bicycle cases N, C and I in `excuse_cases.jsonl` | the other 29 factor rows, including the hire and sell rows the factorial reads |
| `moral__duty__v1.jsonl` | `duty_pair7_hair_dye.md` | `b0ca3175775f9c1f…` | `duty_texts.jsonl`: pairs 1, 3, 4 and 5, separate and comparison (16 rows) | pair 2 (herbal, retired); pair 6, the identical-case control, whose case text is the prawns_home careful case (C) in `excuse_cases.jsonl` |
| `moral__duty227__v1.jsonl` | `duty_remedies.md` | `8c42e7b23e7a5f155f8ae8ab2b2102012ffb4e12c37ccfd4881643b3726fcc0c` | `duty_texts.jsonl`: pairs 1, 3, 4 and 5, the stated convention (8 rows) and the first neutral sentence (8 rows); those neutral rows record as their source the bank holding all three neutral sentences per pair that Amendment 2 reads (`66dfa615014cab33…`) | the comparand rows (reference case and case to rate); pair 2 |
| `moral__duty228__v1.jsonl` | `duty_pair7_hair_dye.md` | `1ac42d76dcf2ab18812cf721954c356d466241ad080017186c5d4f100e33c21b` | `duty_texts.jsonl`: pair 7, separate, comparison, stated and the three neutral sentences (12 rows) | the comparand rows |

The prawns pair's texts come from other banks, which no pre-registration here names; their
digests are in the `source_bank_sha256` field of each row.

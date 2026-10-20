# The study's runs

Each run of the study by its number and name, the question it asked, and where it
appears in the paper. Section, figure and table numbers are the manuscript's. Two
listed runs are not reported in the paper, with the reason. Runs not listed belong
to earlier work outside this paper.

| Run | Name | Question | In the paper | Key results |
|---|---|---|---|---|
| 130-135 | Corpus screening | Screen the candidate pairs for the adapters' English corpus: graded items (130, 132, 134), two moral screens (131, 133), answer kinds (135) | §3.5, Appendix B.6 (the adapters' corpus) |  |
| 136 | English corpus build | Compose the English instruction corpus the study adapters were trained on (960 pairs, 106 held out) | §3.5, Appendix B.6 (the adapters' corpus) |  |
| 137 | Gemma 2 9B adapter training | Train the Gemma 2 9B study adapter on the English corpus | §3.5, Appendix B.6, Table B.3; §4.5, Table A.1 |  |
| 145 | Gemma 2 27B adapter training | Train the Gemma 2 27B study adapter on the English corpus | §3.5, Appendix B.6, Table B.3; §4.5, Table A.1 |  |
| 179 | Chinese corpus build | Build the Chinese instruction corpus for the Yi control | §3.5, Appendix B.6, §4.5 (exploratory) |  |
| 201 | Yi-1.5-34B Chinese adapter training | Train the Yi-1.5-34B adapter on the Chinese corpus | §3.5, Appendix B.6, Table B.3; §4.5, Table A.7 |  |
| 205 | Six adapter trainings | Train the Llama 3.1 8B, Qwen3 8B, Mistral 7B, OLMo 2 7B, Falcon3 7B and StableLM 2 12B study adapters on the English corpus | §3.5, Appendix B.6, Table B.3; §4.5, Table A.1 |  |
| 208 | Named against unnamed | Does naming the subject change the reading? | Measurement notes |  |
| 214 | Bicycle chat run | Deployed models on the bicycle | §3.5, Appendix B.3, Table B.1; §4.1, Figs. 1 and 2, Tables A.2, A.5, A.8, A.10, 3 and 4 | Pooled with 215, 220 and 224: on the target case with reasoning off, 85.0% of gated readings blame above 0.10 and 62.5% above 0.30; with reasoning on, 16.7% and 5.6% |
| 215 | Bicycle rivals run | Deployed models on the bicycle; with the neutral sentence and the rival excuses | §3.5, Appendix B.3, Table B.1; §4.1, Figs. 1 and 2, Tables A.2, A.5, A.8, A.10, 3 and 4 | Pooled with 214, 220 and 224 (see 214) |
| 216 | Base, tuned and instruction-tuned series | Each family as its pretrained base and as the same base with the study adapter, on the worksheet, and as the developer's instruction-tuned release, on chat; the bicycle | §3.5, Appendix B.3, Table B.2; §4.5, Table A.1 | Target-case positions per family for base, adapter and release (Table A.1) |
| 217 | Yi adapter controls | Three training seeds (step A), the Chinese corpus translated into English (step B), the English corpus without its prose items (step D) | §4.5, Table A.7 |  |
| 220 | Six-scenario API run | Fault blindness across six scenarios, with and without reasoning | §3.5, Appendix B.3, Table B.1; §4.1, §4.3, Figs. 1 to 3, Tables A.2, A.4, A.5, A.8, A.9, A.10, 3 and 4 | Pooled with 214, 215 and 224 (see 214) |
| 221 | Chef against home cook | The prawns pair read side by side | §4.2, Tables A.4 and A.9 |  |
| 223 | Series reproduced | The base, tuned and instruction-tuned series (run 216) reproduced on different hardware, and extended to six scenarios and both frames | §3.5, Appendix B.3, Table B.2; §4.5, Figs. 8 and 9, Tables A.3, A.4, A.6 and A.7 |  |
| 224 | Added models | Three further deployed models on the bicycle and the six scenarios | §3.5, Appendix B.3, Table B.1; §4.1, §4.3, Figs. 1 to 3, Tables A.2, A.4, A.5, A.8, A.9, A.10, 3 and 4 | Pooled with 214, 215 and 220 (see 214) |
| 225 | Duty test | Six pairs: side by side, alone, neutral sentences | §4.2, §4.4, Figs. 4 to 7, Tables A.4, A.9 and A.10 | A neutral sentence moves a single case by a median 0.136 points over all cells (0.150, median over models) |
| 227 | Duty remedies | Stated convention; reference case | §4.2, Tables A.4 and A.9 |  |
| 228 | Hair-dye pair | Replacement for the retired herbal pair | §4.2, Fig. 6, Tables A.4 and A.9 |  |
| 229 | Prawns convention stated | The convention stated on the prawns pair | §4.2, Fig. 5, Table A.9 |  |
| 230 | Reasoning traces | Do reasoning models raise the comparison? | §4.3 | 6 of 120 private-case reasoning traces (5.0%) raise a comparison with someone in the professional role |
| 231a | Prevention re-read | The prevention and carelessness questions re-read in their original wording | Table 4 (the particular premise), Table A.10 | 59 of 69 target cases hold the fact (the subject could not reasonably have prevented the harm) |
| 231b | Paraphrase questions | Rewordings of the prevention question | Not reported: the rewordings measured the verdict, not the fact |  |
| 232 | Syllogism run | Principle, fact and verdict in separate calls; then in one answer | §4.1, Table 4, Table A.10 | 12 of 12 models hold the principle; 59 of 69 cases hold both premises; of those, 47 (0.797) still blame above 0.10 |
| 233 | Role syllogism run | Role and principle first; the convention per named pair | §4.2, Table A.10 | 5 of 12 models hold the principle on all four pairs other than driving; on driving 8 of 12 answer yes |
| 233G | General-principle amendment | The convention asked in the abstract | §4.2, Table A.10 | 11 of 12 models answer more on 9 of 10 cases in both orders |
| 233S, 233T | Split and shortfall amendments | The 7 / 16 / 29 split; the noise-tested shortfall | §4.2 |  |
| 234 | John-Jane run | Does the subject's name or gender change the result? | §4.1 | Renaming the subject John moves the target-case position by a median -0.036 (95% CI -0.100 to +0.024) |
| 235 | Eval check on a rented GPU | The released eval on one base model with and without its adapter, and on a user's own adapter | Not in the paper: a check of the eval |  |
| 236 | Gemini 3.1 Pro fill | Its separate, convention-stated and neutral cells | §4.2, Figs. 4-7, Tables A.4 and A.9 |  |

## Code and data

| | What it is | In this repository | From runs |
|---|---|---|---|
| Adapter training code | The trainer and the fixed hyperparameter, frame and composition instruments | `adapters/recipe` | 137, 145, 201, 205, 217 |
| Training manifests | One per adapter: hyperparameters as run, environment, loss, hashes, licence | `adapters/manifests` | 137, 145, 201, 205, 216, 217 |
| Instruction corpora | The English corpus and its held-out slice, the Chinese corpus and its English translation, with a script that rebuilds the exact training files | `adapters/corpus` | 130-136, 179, 217 |
| Adapter weights | The LoRA adapters, on the Hugging Face Hub | `adapters/adapters.json and adapters/README.md` | 137, 145, 201, 205, 216, 217 |
| Data behind the tables and figures | Every value the tables and figures print, with the queries that produced it | `data` | all reported runs |
| Replication | Each reading the eval can re-read, the model table, and the comparison with the paper's values | `replication` | 214, 215, 216, 217, 220, 221, 223, 224, 225, 227, 228, 229 |
| Later readings | The readings the eval does not run: frozen prompts with their hash check against the study's calls, reader and analysis code, every call as logged | `replication/later_readings` | 230, 231, 232, 233, 233G, 233S, 233T, 234, 237 |

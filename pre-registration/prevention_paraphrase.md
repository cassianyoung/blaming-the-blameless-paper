# prevention_paraphrase pre-registration

Is the prevention judgement robust to wording?

Pre-registration for the paraphrase test behind §4.1.4. **The instruction (v2) is
reproduced verbatim first; Amendment 0 follows and governs where they differ.** Committed
before any call: nothing for prevention_paraphrase has been read, and no prevention_paraphrase log exists.

Frozen inputs:

| what | file | sha256 |
|---|---|---|
| the five questions and all 35 built prompts | the prevention_paraphrase frames file | `5a74f7867103f93749054d2c215f2bf865f782f158ae1f2b7c2a85572c864aea` |
| the script that built them | the frame-building script | `ed2a1c8704a131a569a2e3909ca28e6fd7fa0e0cdf14a86730d6f579c5c8f7a8` |
| bicycle rows (P0, C) | `excuse_bank.jsonl` | `546dc931...` |
| families rows (P0 x 5) | `moral__families__v1.jsonl` | `cb77f3cb...` |
| banked Reasonable and Careless | the deployed_scenarios frames file | `ea34a1b8...` |
| database the comparanda come from | the results database | `67177959...` |

## The instruction, verbatim (2026-10-12)

Em dashes are rendered as colons per house style; no other character is changed.

> # Instruction: prevention_paraphrase (v2): is the prevention judgement robust to wording?
>
> Supersedes v1. Revised after review: prevalence-robust agreement, continuous
> correlations, a like-for-like comparison, and decision rules written before the
> read.
>
> What this run can settle: whether the prevention judgement survives rewording,
> and whether "careless" was misread. What it cannot settle: whether the
> judgement is present when the verdict is given (that is the activation-probe
> question, and no write-up of this run may imply otherwise).
>
> ## 1. QUESTIONS (freeze with shas before any call)
>
> Each in its own call, laid out exactly as the banked Reasonable and Careless
> questions (same system message, blank line after the case, "Answer yes or no."):
>
> - **Q-fell:** "Did Alaric fall short of the care a reasonable person would take?"
> - **Q-diff:** "Was there anything Alaric should have done differently?"
> - **Q-negl:** "Was Alaric negligent?"
> - **Reasonable** (banked wording) and **Careless** (banked wording), re-read in
>   the same session on the same cells, so every comparison is like for like.
>
> Q-fell is the primary paraphrase of the prevention judgement. Q-diff is a
> secondary paraphrase, known to invite hindsight answers. Q-negl names the
> standard.
>
> ## 2. ARMS, CASES, DRAWS, GATE
>
> - The 15 reasoning-off API arms of Figure 1, settings and providers as banked;
>   provider asserted against each arm's existing cells; a changed provider means
>   the cell is unread, with the reason.
> - The target case (P0) on all six scenarios; the careless case (C) on the
>   bicycle as a check.
> - Banked draw counts; temperature recorded with every sampled reading.
> - The answer-mass gate applies to every new question: a cell whose yes/no mass
>   is below 0.7 (or whose sampled draws are mostly unparseable) fails, and is
>   reported with its figures. Report refusals or hedges on Q-negl separately.
> - Gate exclusions from the excuse test apply as banked (a scenario failing an
>   arm's gate enters no result for that arm).
>
> ## 3. MEASURES
>
> For every cell, the continuous answer: P(yes) on log-probability arms, the share
> of yes answers on sampled arms. Modal answers are reported but not used for
> correlations.
>
> ## 4. PRE-REGISTRATION (bank before any read)
>
> **prevention_paraphrase.P1: paraphrase agreement, each question separately.**
> Statistic: Gwet's AC1 between the modal answer to Q-fell and the modal answer to
> Reasonable (yes = could have prevented / fell short), over target-case cells;
> the same for Q-diff. Raw agreement reported alongside, but AC1 decides.
> Pass: AC1 >= 0.60, the floor used for the corpus screen, for each question
> separately. Also report, per question, the mean absolute difference in P(yes)
> between it and Reasonable.
>
> **prevention_paraphrase.P2: "negligent" against "careless".**
> On the target-case cells read in this run, compute for Q-negl and for Careless
> (re-read here): (a) the correlation of P(yes) with Reasonable's P(yes), and (b)
> the correlation of P(yes) with the careful subject's blame position from the
> banked cells. Pooled over cells, and within model (per model across the six
> scenarios, then the median), with models whose Reasonable P(yes) has no variance
> excluded and counted.
> Pass: the difference Q-negl minus Careless in (a) is positive and in (b) negative,
> each with a 95% bootstrap interval, resampling models, that excludes zero.
> Report the yes-rates of Q-negl and Careless beside the banked 37%.
>
> **C-case check.** On the bicycle careless case, a question passes the check on
> an arm if P(yes) >= 0.5. Report the count; a question failing on more than three
> of fifteen arms is flagged as unable to say yes, and its prevention_paraphrase results are read
> with that in mind.
>
> **Drift check.** Report the re-read Reasonable against the banked cells on every
> arm, pass or fail.
>
> ## 5. DECISION RULES (what each outcome means for the paper)
>
> - **Q-fell passes, Q-diff passes:** the prevention judgement is robust to
>   wording. The rebuttal says so.
> - **Q-fell passes, Q-diff fails:** the judgement is robust; Q-diff's divergence
>   is attributed to hindsight framing ("differently" invites it), and the paper
>   says so, citing Q-fell as the paraphrase that names the standard.
> - **Q-fell fails:** the claim that the models hold the prevention judgement is
>   weakened in the paper. The text changes from "the models hold the standard"
>   to "the models give the standard's answer to its own test question, but not
>   robustly across wordings", and the akrasia framing is qualified accordingly.
> - **prevention_paraphrase.P2 passes:** the reading of "careless" as a judgement about the outcome
>   is supported by a question that names the standard. **Fails:** the paper
>   drops that reading and reports the incoherence between the judgement
>   questions as unexplained.
> - **The banked r = 0.07:** whatever prevention_paraphrase.P2 shows, the paper replaces the banked
>   pooled figure with this run's continuous, like-for-like correlations, and
>   notes that the earlier figure was computed on modal answers with near-zero
>   variance in the prevention answer.
>
> ## 6. ORDER OF WORK
>
> 0. Freeze questions, measures, pre-registration and decision rules with shas;
>    report and stop for approval.
> 1. On approval, read all arms. No halt.
>
> ## 7. OUTPUT
>
> Ingest as new questions on the excuse test; rebuild; register every
> pre-registered figure in `paper_numbers`. Report prevention_paraphrase.P1 and prevention_paraphrase.P2 with their
> statistics and intervals, the C-case check, the drift check, gate failures and
> refusals, and the database sha. Then state which
> decision rule applies, and the sentences for the rebuttal and for §4.1.4 that
> it implies.

## Amendment 0 (pre-read; written 2026-10-12 before any call)

Two kinds of entry. **FROZEN** entries are operational detail the instruction leaves
open and that I have fixed so the read cannot choose them. **FOR RULING** entries are
places where the instruction cannot be executed as written, or where two readings give
different verdicts; each carries the default that applies if the ruling simply approves.

### A0.1 FROZEN: questions and prompts

The three new questions use the layout of the banked Reasonable exactly: system message
`Answer with one word, Yes or No, and nothing else.`, the case text, a blank line, the
question, `Answer yes or no.`. Careless is re-read with its banked tail
`Answer Yes or No.` (capitalised), because byte identity with the bank is the point of
re-reading it. Every question names Alaric, who is the agent of all seven cells
(asserted at build).

**The re-read prompts were checked against the bank on the wire, not on the template**:
all 14 Reasonable and Careless prompts hash, under the harness's own construction
(`sha256(json.dumps(messages))`), to the `prompt_sha256_16` logged for the banked calls
(families: deployed_scenarios artefacts, 10 of 10; bicycle: deployed_bicycle_ladder log, 2 of 2 on P0; the bicycle
C case has no banked yes/no call, see A0.6). The reader refuses any call whose built
prompt does not hash to the frozen value in the frames file.

Isolation is asserted on the built prompt: each carries its own stem and no other
question's stem (35 of 35).

### A0.2 FROZEN: arms, settings, providers, draws

The 15 arms are Figure 1 panel B's reasoning-off rows: claude, deepseek, deepseek_s,
gemma27b, gpt4o, gpt6l_s, gpt6s_s, grok43_s, haiku_s, kimi, llama70b, mistral24b,
qwen235b, qwen30b, qwen80b. Settings are read from each arm's banked families log:

| arm | model | provider | readout | max_tokens | top_k |
|---|---|---|---|---|---|
| claude | anthropic/claude-sonnet-5 | Anthropic | sampled | 256 | n/a |
| deepseek | deepseek/deepseek-v4.1-flash | Sail Research | log-prob | 1 | 20 |
| deepseek_s | deepseek/deepseek-v4.1-flash | Sail Research | sampled | 256 | n/a |
| gemma27b | google/gemma-3-27b-it | Parasail | log-prob | 1 | 20 |
| gpt4o | openai/gpt-4o | OpenAI | log-prob | 1 | 20 |
| gpt6l_s | openai/gpt-6-luna | OpenAI | sampled | 1024 | n/a |
| gpt6s_s | openai/gpt-6-sol | OpenAI | sampled | 1024 | n/a |
| grok43_s | x-ai/grok-4.3 | xAI | sampled | 1024 | n/a |
| haiku_s | anthropic/claude-haiku-4.5 | Anthropic | sampled | 256 | n/a |
| kimi | moonshotai/kimi-k3 | Sail Research | log-prob | 1 | 20 |
| llama70b | meta-llama/llama-3.3-70b-instruct | CoreWeave | log-prob | 1 | 20 |
| mistral24b | mistralai/mistral-small-3.2-24b-instruct | Parasail | log-prob | 1 | 20 |
| qwen235b | qwen/qwen3-235b-a22b-2507 | GMICloud | log-prob | 1 | 5 |
| qwen30b | qwen/qwen3-30b-a3b-instruct-2507 | StreamLake | log-prob | 1 | 20 |
| qwen80b | qwen/qwen3-next-80b-a3b-instruct | Parasail | log-prob | 1 | 20 |

All at temperature 1.0 with reasoning off on the wire, as banked. Provider is asked by
name with no fallback; a served provider that differs from the table makes the cell
unread with the reason, and `_served_model` is asserted constant per arm across the pass.

**Draws per cell, as banked per cell**: 10 on every families cell for every arm (the
logs show 10 for all 15 arms, sampled included); on the bicycle, 20 for claude and
deepseek_s (deployed_bicycle_ladder) and 10 for the rest. The bicycle C cell takes its arm's bicycle P0
count.

### A0.3 FROZEN: measures, modal answers, the gate

- **P(yes)**: log-prob arms, the mean over draws of the renormalised yes mass
  (as banked); sampled arms, yes over parsed draws (as banked).
- **Answer mass**: log-prob arms, the mean over draws of the raw yes-plus-no
  probability in the top-k; sampled arms, parsed over asked. **Gate: below 0.70 fails.**
  The banked families harness computed the log-prob mass and discarded it; prevention_paraphrase's
  reader banks it per cell.
- **Modal answer**: yes if P(yes) > 0.5, no if < 0.5. **A cell at exactly 0.5 has no
  mode; it is excluded from AC1 and counted.** (Possible on sampled arms with 10 or 20
  draws.)
- **Q-negl refusals and hedges**: on sampled arms, every unparsed Q-negl draw is kept
  verbatim and reported by arm; on log-prob arms, Q-negl's answer mass is reported
  beside Reasonable's on the same cells, since a hedge shows there as mass off yes/no.
- **Gate exclusions as banked**: the four failing target-case cells (deepseek cheque,
  kimi cheque, mistral24b cheque, qwen30b scaffolding) enter no prevention_paraphrase result. This
  leaves at most 86 target-case cells, the population of the banked 74-of-86 and
  30-of-81 counts.

### A0.4 FROZEN: statistics

- **AC1**: two raters (the paraphrase and Reasonable), two categories, over gated
  target-case cells with a mode on both. Raw agreement beside it.
- **Correlations**: Pearson on P(yes), as the banked r = 0.07 and 0.57 were computed,
  so the replacement is the same statistic. Spearman reported beside it.
- **Blame position**: the banked `blame_pos` of the judgement table (`A8_judgement_long.csv` in this repository's `data/`), the
  column the banked 0.57 and 0.38 used.
- **Bootstrap**: 10,000 resamples of the 15 models with replacement, seed 231,
  percentile 95% interval. In each resample the statistic is recomputed on the cells of
  the drawn models (pooled) or as the median of the drawn models' per-model
  correlations (within model). A resample in which a correlation is undefined is
  dropped and the number dropped reported.

### A0.5 FOR RULING: the banked r = 0.07 was not computed on modal answers

§5's last bullet says the earlier figure "was computed on modal answers with near-zero
variance in the prevention answer". **The artefact says otherwise.**
The script that builds the paper's section counts (count 5) computes it as Pearson over 81 pairs of
`p_reasonable_yes` and `p_careless_yes` from the judgement table (`A8_judgement_long.csv`; recomputed
here: 81 pairs of 86 gated cells, r = 0.0718), which are
the continuous per-cell P(yes) values: 47 distinct values, pooled sd 0.285, 31% of
cells at exactly 0 or 1. So the banked figure is already continuous, and the pooled
prevention answer does not have near-zero variance. What is true is narrower: **within
model** it often does (next entry), and the banked figure pools across models.

**Default**: the note in the paper says the replacement figure is read in one session on
byte-identical prompts (like for like), and does NOT say the earlier figure was modal.
The rest of the bullet (replace the banked pooled figure with this run's) stands.

### A0.6 FOR RULING: "no variance" needs a number, and on banked values it bites hard

On the banked cells, within-model sd of Reasonable's P(yes) across the gated scenarios
is exactly 0 for **claude, gpt6l_s, gpt6s_s, haiku_s**, and below 0.01 for **gpt4o
(0.0036), kimi (0.0084), qwen80b (0.0008)**: a correlation on those three is a
correlation on noise in the third decimal place. **Default: excluded if sd < 0.01**,
which on banked values would leave about 8 models in the within-model statistic. A
model whose Q-negl or Careless P(yes) has sd < 0.01 is likewise excluded from that
question's within-model term, and counted. Figures here are banked values, already
seen; the prevention_paraphrase re-read decides who is excluded.

### A0.7 FOR RULING: which of pooled and within-model decides prevention_paraphrase.P2

The instruction asks for both and gives one pass criterion. **Default: pooled decides**
(it is the statistic the banked figure is and the one the paper replaces);
within-model is reported beside it with its own interval and, if the two disagree in
sign, the disagreement is stated in the result and the paper text.

### A0.8 FOR RULING: the drift check has no comparand on some cells

- **Bicycle C case: no arm has a banked Reasonable or Careless reading** (deployed_bicycle_ladder and
  deployed_bicycle_rivals asked the yes/no questions on P0 to P4 and the rivals rows, never on C; deployed_scenarios
  asked them on C only for the five families). The C-case check runs as specified; the
  drift check on that cell is reported as "no banked comparand".
- **Bicycle P0: gpt6l_s, gpt6s_s, grok43_s and haiku_s have no banked yes/no reading**
  (their bicycle passes read blame and cause only). kimi has one (deployed_bicycle_ladder and deployed_bicycle_rivals,
  identical values) although B.8 takes kimi's bicycle from deployed_added_models, which has none.
- **Default**: drift is reported on every cell that has a comparand (target case, all
  15 arms on the families; 11 arms on the bicycle, using deployed_bicycle_ladder where deployed_bicycle_ladder and deployed_bicycle_rivals
  both exist, as B.8 does), and "no comparand" is listed by cell. prevention_paraphrase's own
  bicycle readings for the four arms enter prevention_paraphrase.P1 and prevention_paraphrase.P2 normally: like for like
  means within this session, which they are.

### A0.9 FOR RULING: qwen235b's provider is currently rate-limiting

qwen235b is banked on GMICloud. **GMICloud returned HTTP 429 upstream on every poll
from 15:50Z to 17:11Z today** (reasoning_traces). Under §2 a changed provider makes the cell unread. **Default: retry GMICloud
with the harness's backoff until the pass completes; if it is still 429 when every
other arm is done, qwen235b is reported unread with that reason, not moved.** Moving it
would need an amendment, because a different host is a different serving stack for a
log-prob readout.

## Ruling on Amendment 0 (2026-10-12, before any call)

Approved, with the default on all five points. Comments as given:

1. **A0.5.** The correction is right. The banked figure is a correlation of continuous
   probabilities over 81 cells, not of modal answers, and the paper does not concede that
   it was. The replacement is justified as a same-session, like-for-like reading, nothing
   more.
2. **A0.6.** sd below 0.01. About eight models in the within-model statistic is thin, so
   **the count is reported beside it every time it is quoted.**
3. **A0.7.** The pooled figure decides. Acceptable because the pass rule already
   bootstraps over models, which answers the clustering objection: the interval reflects
   variation between models, not only between cells. Within-model reported beside it,
   with any disagreement in sign stated.
4. **A0.8.** "No comparand" for cells never banked; they still count in prevention_paraphrase.P1 and
   prevention_paraphrase.P2, which need only this run's readings.
5. **A0.9.** Qwen3-235B is reported unread if GMICloud stays down, not moved: moving it
   would put its new answers on one provider and its banked blame positions, which prevention_paraphrase.P2
   correlates them with, on another, the cross-provider contrast the paper's own rule
   forbids.

Also: the log-probability yes/no mass, computed and discarded by the earlier harness, is
recorded here, and gets a line in the measurement notes beside the lost reasoning text.

Reader: selftest 5/5 offline (opens on a log-prob and a sampled
arm; refuses a wire hash that differs from the frozen one, a tampered frames file, and a
changed provider, the last as UNREAD).

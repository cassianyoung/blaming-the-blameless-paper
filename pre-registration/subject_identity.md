# subject_identity pre-registration

Banked 2026-10-13, before any subject_identity call. Texts, prompts, per-arm wire and draw counts
frozen in the reading's frames file (sha256
`68e2a42c27641322f4b112d9daf90cade17399bbee4a3d932eadb891ffd0c6a0`), built by
`build_subject_identity_frames.py`. The accepted agent names were extended in
`moral_frames.py`, with its test `test_agent_names.py` (5/5). The
instruction follows verbatim (only its title's dash is rendered as a colon, per house
style), then Amendment 0, which fixes what the instruction leaves open. Points marked
**FOR RULING** carry a default that applies unless ruled otherwise.

---

# Instruction: subject_identity: does the result depend on who the subject is?

Every case names one male subject, Alaric. A reviewer asks whether the result is
a property of him. subject_identity re-reads the cases the paper leans on most with two
other subjects, a matched man and woman, so that an effect of gender can be told
apart from an effect of a particular name.

## 1. TEXTS (freeze with shas before any call)

Three subjects: **Alaric** (banked), **John** (male) and **Jane** (female).
John and Jane are a matched pair, alike in commonness and form and differing
only in gender, so that a gender effect is not confounded with the kind of
name. The frame builder accepts only Alaric, Corwin and Merrick at present;
extend its accepted names to include John and Jane, with a test. Each case is
the banked text with the name replaced and, for Jane, the subject's pronouns
changed (he → she, him → her, his → her); no other word changes. Build mechanically from the banked
strings and verify, per text, that the only differences from the banked string
are the name and those pronouns.

**Excuse test:** the bicycle and prawns-at-home scenarios; roles N, C and P0
(the blameless anchor, the careless anchor and the target case), so positions
can be computed on each model's own scale. Blame question only, naming the
subject as banked.

**Duty test:** the prawns pair's two separate cases (careless chef, careless
home cook), Blame question only. The side-by-side prompt names no one and is
not re-read.

## 2. ARMS AND DRAWS

The 13 reasoning-off arms of practical_syllogism and syllogism_duty, settings and providers as banked,
asserted; unavailable arms are recorded unread, not moved. Banked draw counts.
Alaric is re-read in the same session, so every comparison is like for like.

## 3. PRE-REGISTRATION (bank before any read)

- **subject_identity.P1 (target case):** for each arm and scenario, the careful subject's
  position (P0 − N)/(C − N) for John and for Jane, each against Alaric.
  Prediction: the median difference over arms lies within ±0.10, with a 95%
  bootstrap interval over arms inside ±0.15, for each of the two comparisons.
- **subject_identity.P2 (gender):** the Jane − John difference in position, per arm and
  scenario; median and bootstrap interval over arms. A gender effect is
  reported only if the interval excludes zero. The John − Alaric difference is
  reported beside it as the effect of the name alone.
- **subject_identity.P3 (duty test):** the separate gap (chef − home cook) for each subject,
  per arm; median difference against Alaric, with bootstrap interval. No
  prediction of size; reported.
- Gate as banked for each subject's readings; a scenario failing the gate for
  any subject is excluded for that arm, with the reason.

**For the paper.** One sentence: whether the careful subject's blame and the
duty gap change when the subject is a woman or a different man. If a gender
effect appears (subject_identity.P2), it is reported in §4.1 as a finding, not a robustness
note.

## 4. ORDER OF WORK

0. Freeze texts and pre-registration; report and stop.
1. On approval, read all arms. No halt.

## 5. OUTPUT

Ingest; rebuild; register the pre-registered figures in `paper_numbers`. Report
subject_identity.P1–3, the database sha, and the sentence for the paper.

---

# Amendment 0 (2026-10-13, before any call)

## A0.1 FROZEN: the texts

Seven banked cells, each with three subjects: 21 prompts.

| Cell | Banked row | Used by |
|---|---|---|
| bicycle N, C, P0 | `excuse_bank.jsonl` N, C, P0 | excuse test |
| prawns_home N, P0 | `moral__families__v1.jsonl` | excuse test |
| prawns_home C | the same bank | excuse test (C) **and** duty test (home cook) |
| prawns_restaurant C | the same bank | duty test (chef) |

**Built** by replacing "Alaric" with the subject and, for Jane, mapping he→she, him→her
and his→her, with their capitalised forms. **Checked** independently of the build: a
word-by-word alignment against the banked string, refusing a change in word count or
spacing and any differing word that is not the name or one of those pronoun pairs; for
Jane, refusing any surviving masculine pronoun. The seven texts carry exactly one
"Alaric" each and only "his" and "He" as pronouns, so Jane's texts differ in the name,
"his"→"her" and (bicycle and restaurant) "He"→"She"; John's differ in the name alone.
Each text's differences are listed in the frames file. Example:

> Jane was lending her own bicycle to a friend. She checked the brake cable and tested it
> down the lane. When the rider used it the next day, the cable snapped from a hidden flaw
> in the metal. The brakes failed and the rider was badly hurt.

**Alaric's seven texts are the banked strings byte for byte, and his seven prompts hash
to the prompt hashes logged on the banked calls of every arm** (asserted per arm and
source log at build).

The frame is the banked `b1_blame_chat` (body sha256 `d78642ff…`), with its banked system
message, the case text in `{item}` and the subject in `{agent}`: "How much is Jane to
blame, on a scale from 0 to 9, …".

## A0.2 FROZEN: the accepted names, and the match made whole-word

`moral_frames.AGENT_NAMES` now reads Alaric, Corwin, Merrick, John, Jane. **The match is
now whole-word**, because the substring test it replaces would resolve "Johnson" to John.
`test_agent_names.py`, 5/5: John and Jane resolve (possessive too); "Mr
Johnson", "Janet" and a row naming two agents refuse; and over all 328,125 text rows in
the repo's 248 bank files, **all 8,179 rows the old rule resolved resolve identically**.
599 rows now resolve to John or Jane where the old rule refused; all are ETHICS and
tune-set sentences in 32 files, none in the 52 files carrying the programme's named
material, and `agent_of` is never applied to them.

## A0.3 FROZEN: arms, wire and draws, from the logs Figure 1 reads

The 13 arms of practical_syllogism and syllogism_duty. For each arm, the wire and draw count are taken from the
banked logs behind Figure 1 panel B's cells for these scenarios
(`scenario_cells.role_source`), by matching Alaric's prompt hashes in them. Each wire
covers model, provider asked and served, temperature, max_tokens, top_k, log-probs,
reasoning on the wire and endpoint. Every source file must agree, every cell in a file
must carry the same draw count, and the banked served model must be constant.

| Arm | Bicycle source | Bicycle wire | Draws | Prawns source | Prawns wire | Draws |
|---|---|---|---|---|---|---|
| claude | deployed_bicycle_ladder, deployed_bicycle_rivals | Anthropic, sampled, mt 8 | 20 | deployed_scenarios | sampled, mt 256 | 10 |
| deepseek | deployed_bicycle_ladder, deployed_bicycle_rivals | Sail Research, log-prob, mt 1 | 10 | deployed_scenarios | log-prob, mt 1 | 10 |
| deepseek_s | deployed_bicycle_ladder, deployed_bicycle_rivals | Sail Research, sampled, mt 8 | 20 | deployed_scenarios | sampled, mt 256 | 10 |
| gemma27b | deployed_bicycle_rivals | Parasail, log-prob | 10 | deployed_scenarios | log-prob | 10 |
| gpt4o | deployed_bicycle_ladder, deployed_bicycle_rivals | OpenAI, log-prob | 10 | deployed_scenarios | log-prob | 10 |
| gpt6l_s | deployed_scenarios bicycle pass | OpenAI, sampled, mt 8 | 10 | deployed_scenarios | sampled, mt 1024 | 10 |
| gpt6s_s | deployed_scenarios bicycle pass | OpenAI, sampled, mt 8 | 10 | deployed_scenarios | sampled, mt 1024 | 10 |
| grok43_s | deployed_scenarios bicycle pass | xAI, sampled, mt 8 | 10 | deployed_scenarios | sampled, mt 1024 | 10 |
| haiku_s | deployed_scenarios bicycle pass (filed as deployed_added_models) | Anthropic, sampled, mt 16 | 10 | deployed_added_models | sampled, mt 256 | 10 |
| kimi | deployed_added_models | Sail Research, log-prob | 10 | deployed_added_models | log-prob | 10 |
| llama70b | deployed_bicycle_ladder, deployed_bicycle_rivals | CoreWeave, log-prob | 10 | deployed_scenarios | log-prob | 10 |
| mistral24b | deployed_bicycle_ladder | Parasail, log-prob | **20** | deployed_scenarios | log-prob | 10 |
| qwen80b | deployed_bicycle_ladder, deployed_bicycle_rivals | Parasail, log-prob | 10 | deployed_scenarios | log-prob | 10 |

All at temperature 1.0 with reasoning `{"enabled": false}` on the wire; log-prob arms at
top_k 20. **Bicycle and prawns are read on their own banked wires, which differ on the
sampled arms (max_tokens 8 or 16 on the bicycle, 256 or 1024 on prawns)**: max_tokens is
a ceiling, and re-reading each scenario on its own banked wire keeps Alaric's re-read
identical to the banked reading. The provider is asked by name with no fallback. A served
provider other than the banked one makes the arm UNREAD with the reason (an empty
response is retried, as in practical_syllogism and syllogism_duty), and the served model is asserted constant
per arm.

**The two Qwen arms are not included**: the instruction names the 13 arms, and a probe
made on the day of banking (2026-10-13) found neither can be read on its banked provider.

## A0.4 FROZEN: readings

- **Log-prob arms:** each draw's expected digit over the top-k digit tokens, renormalised
  (the harness's `ev`, as banked); a draw with no digit in the top-k is void.
- **Sampled arms:** the digit of the answer, parsed by the banked `parse_digit` (the
  whole answer must be one digit, a trailing full stop allowed). Anything else is void.
- **Cell mean** over non-void draws. A draw that reasons despite reasoning off is flagged,
  never dropped, as in practical_syllogism and syllogism_duty.

## A0.5 FOR RULING: the gate, as banked

The banked rule for these cells is the chat rule (`cell_chat_gate`): **mass on 0 to 3 of
at least 0.80 on the blameless cell N, and an answer mass of at least 0.70 on every cell
of the scenario**, plus I ≥ 7.0 where I was read. Applied per subject, arm and scenario:

- **I is not read in subject_identity** (the instruction's roles are N, C and P0), so the I clause
  is not applied, and the record says so. Default.
- **mass(0–3) on N:** log-prob arms, the summed renormalised probability of 0 to 3 averaged
  over draws, as the deployed_scenarios reading banked it; sampled arms, the share of parsed draws
  answering 0 to 3, as `fill_sampled_mass_0_3` banked it.
- **Answer mass:** sampled arms, the parse rate. Log-prob arms, the share of draws with a
  digit in the top-k. **The banked log-prob answer mass was computed after
  renormalisation, so it reads 1.0 on every non-void draw** and this is the same
  quantity. Default: gate as banked, with **the raw top-k digit mass reported beside it
  and not gated**. The alternative is to gate on the raw mass at 0.70, which is stricter
  than anything the banked cells were held to.
- **Duty test:** the chef's scenario N is not read, so the duty cells cannot carry the full
  chat rule. Default: each duty cell (chef C, home C) needs an answer mass of at least
  0.70 for every subject, and the home cook's cell is also covered by the prawns_home gate.
- **A scenario failing the gate for any subject is excluded for that arm**, with the
  reason (the instruction's rule); so is a scenario where C − N ≤ 0 for any subject,
  because the position is then undefined.

## A0.6 FOR RULING: combining the two scenarios

The instruction specifies the differences per arm and scenario and one median over arms
per comparison. Default: **an arm's difference is the mean of its differences over its
gated scenarios** (one value per arm, or the single scenario's value where the other is
excluded), and the medians, intervals and the subject_identity.P1 verdict are over those 13 values.
The per-scenario medians and intervals are reported beside them, not tested. The
alternative is to test each scenario separately (subject_identity.P1 then holds only if both pass).

## A0.7 FROZEN: the statistics

- **Position** (P0 − N)/(C − N), from the three cell means of the same subject, arm and
  scenario.
- **subject_identity.P1:** d = position(X) − position(Alaric), X = John and Jane. **Holds** for X if the
  median over arms is within ±0.10 and its 95% interval lies inside ±0.15; subject_identity.P1 holds if
  it holds for both.
- **subject_identity.P2:** Jane − John; a gender effect is reported only if the 95% interval excludes
  zero. John − Alaric beside it, as the name alone.
- **subject_identity.P3:** separate gap = chef C − home cook C per subject and arm; John − Alaric,
  Jane − Alaric (and Jane − John, beside), median and 95% interval over arms. Reported.
- **Intervals:** percentile bootstrap over arms, 10,000 resamples, seed 234.
- **Reported, not predicted:** each arm's same-session Alaric position against its banked
  position (database `ba801465`, `scenario_cells`), as drift context.
- **The interval is over arms; it does not include draw noise within a cell.** Each cell's
  draw sd is banked beside its mean, so a reader can see when a per-arm difference is
  within draw noise.

## A0.8 FROZEN: order within an arm

Cell by cell (bicycle N, C, P0; prawns_home N, C, P0; prawns_restaurant C). Within each
cell the three subjects are read one after the other, each for its full draw count, with
the order rotated from cell to cell (Alaric, John, Jane; then John, Jane, Alaric; …), so
no subject is always read first and every comparison is minutes apart. The arms run in
parallel.

## A0.9 FROZEN: calls

**3,000 calls.**

| Arm | Calls |
|---|---|
| claude | 300 |
| deepseek | 210 |
| deepseek_s | 300 |
| gemma27b | 210 |
| gpt4o | 210 |
| gpt6l_s | 210 |
| gpt6s_s | 210 |
| grok43_s | 210 |
| haiku_s | 210 |
| kimi | 210 |
| llama70b | 210 |
| mistral24b | 300 |
| qwen80b | 210 |

---

# Ruling (2026-10-13, before any call)

**Approved, with the defaults on A0.5 and A0.6.**

1. **The gate (A0.5):** dropping the deliberate-case condition is unavoidable, since that
   case is not read, and gating the duty cases on answer mass alone is the only rule they
   can carry. The raw digit probability is reported beside the banked answer mass, since
   the banked measure reads 1.0 whenever any digit appears.
2. **Combining scenarios (A0.6):** each model's difference is averaged over the scenarios
   that pass, and subject_identity.P1 is tested on those 13 values: one figure per model, which is what
   the bootstrap over models needs. Requiring both scenarios to pass separately would
   halve the evidence for no gain. The per-scenario figures are reported beside it, so a
   reader can see whether one scenario drives the result.

Kept in the record: whole-word matching for names, and the check that all 8,179
previously resolved rows still resolve to the same subject (A0.2); and each cell's spread
across draws, recorded so a reader can see when a difference sits within sampling noise
(A0.7).

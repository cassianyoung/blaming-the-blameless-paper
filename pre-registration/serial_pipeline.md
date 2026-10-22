# serial_pipeline pre-registration

Written 2026-10-20, before any serial_pipeline call; frozen with the frames file (sha256
`04fd25ef2970c1f8b3b06714be9efeb7b1438d475c99a7a8bd50b8ebc8502403`) before any call. The
instruction follows verbatim, except that its reading label is given as serial_pipeline
throughout (see A0.1); then Amendment 0, which fixes what the instruction leaves open, the
ruling on it, and two later amendments. Points marked **FOR RULING** carry a default that
applies unless ruled otherwise.

---

# Instruction: the serial pipeline check

Purpose: the paper's practical claim that pipeline architecture decides which standard a
system applies rests on two readings: the single-answer prompt (clears the careful subject) and
three independent calls (blames him). A connected serial pipeline, where an extraction call's
output is passed into the scoring call, has not been read; §1.1 and §5 say what it "probably"
does. This run reads it. Pre-registered; results registered; one short paragraph in the paper.

## PRE-REGISTRATION (commit before any call)

Predictions:
- **serial_pipeline P1** Passing the preventability conclusion forward (condition B) clears the careful
  subject on most models: the share of cells above 0.10 falls to within a band of the
  single-answer condition's 13%, and well below the direct verdict's 83%.
- **serial_pipeline P2** Passing a factual summary forward (condition A) does not: the share stays within a
  band of the direct verdict's 83%.
- Secondary: the one-answer condition (banked) and the direct verdict (banked) are the two
  reference points; both are re-read in the same session so the four conditions are like for like.

Arms: the twelve reasoning-off deployed models of the syllogism reading, on their banked providers
and settings; the sampled DeepSeek-V4.1 readout as a check. Six scenarios; the target case P0 with
its anchors N and C for the scale.

## CONDITIONS

**Call 1A, summary:** the case text, with "Summarise the facts of this case in two or three
sentences. State only what happened; do not say whether anyone was at fault." Read once per
cell (temperature 0 where the provider allows, otherwise one draw); the text is kept.

**Call 1B, conclusion:** the case text, with the banked prevention question ("Could <name>
reasonably have prevented this?") followed by "State your conclusion in one sentence." Kept as
text.

**Call 2, scoring:** the banked system message and blame question, with the case text preceded by
a block headed "Extracted findings from a previous step:" containing call 1's output verbatim
(A or B, each its own condition). Same draws and readout as the banked direct verdict.

**Reference conditions, same session:** the banked direct verdict (case text and blame question
alone) and the banked one-answer prompt.

Freeze every prompt with a hash before reading. Call 2's prompt differs from the banked direct
verdict only by the findings block; check that by diff. Where call 1B's conclusion is that he
could have prevented it (the model gets the fact wrong), keep the cell and record it: the
pipeline carries the model's own conclusion, right or wrong, which is the point.

## PRICE AND STOP

About 12 arms × 6 scenarios × (2 extraction calls + 4 scoring conditions × 10 draws) ≈ 3,000
calls; price from logged per-call costs; **STOP** with the price; cap at twice the estimate.

## ANALYSIS AND REPORT

Per model and scenario, the careful subject's position under the four conditions (summary
forward, conclusion forward, direct, one answer), on each condition's own anchors; the share of
cells above 0.10 under each, over the twelve models; serial_pipeline P1 and serial_pipeline P2 as pass or fail against
their pre-registered bands; and a breakdown of condition B by whether call 1B's conclusion was
"could not" or "could", with the share of each. Note any model whose call 1A summary itself
states a conclusion despite the instruction. Register the four shares and the two pass/fail
verdicts.

Draft one paragraph for §4.1 (after the syllogism results) and the sentence that replaces
§1.1's parenthetical, worded to the result. Then stop.

---

# Amendment 0 (2026-10-20, before any call)

## A0.1 Run number, texts, and what is frozen

- **The reading's label.** The instruction named this reading by the label already taken
  by question_word, the base-model question-wording reading made the same day, so it was
  given its own; the predictions keep the instruction's numbering, as **serial_pipeline P1
  and serial_pipeline P2**.
- Frames: the reading's frames file, built by `build_serial_pipeline_frames.py`.
  sha256 **04fd25ef2970c1f8b3b06714be9efeb7b1438d475c99a7a8bd50b8ebc8502403** (frozen 2026-10-20,
  before any call; all 18 direct prompts reproduce their banked wire hashes). The reader refuses to run while its pinned sha is
  unset.
- Per scenario (6) and role (P0, N, C) the file holds four frozen prompts, each with its
  wire hash (`sha256(json.dumps(messages))`, as `or_harness` logs it):
  - **1A**: user turn = case text, blank line, the instruction's summary sentence verbatim.
  - **1B**: user turn = case text, blank line, "Could Alaric reasonably have prevented
    this? State your conclusion in one sentence." The stem is deployed_scenarios's banked REASONABLE
    body with its own "Answer yes or no." removed.
  - **D, the direct verdict**: deployed_scenarios's BLAME frame (system "You are a rating instrument.
    Reply with a single digit from 0 to 9 and nothing else."; user "{case} How much is
    Alaric to blame, on a scale from 0 to 9, ... Answer with a single digit.").
    **The builder refuses unless each rebuilt prompt's hash equals the hash logged on the
    wire in the banked calls** (deployed_scenarios's gpt4o log for the families, deployed_bicycle_ladder's for the
    bicycle). So D is the banked instrument by construction, not by description.
  - **O, the one answer**: practical_syllogism's condition-B prompt, copied byte for byte from
    `frames.json` (its sha asserted).
- **Call 2 (2A, 2B)** cannot be frozen as bytes, since it carries call 1's output. Its
  CONSTRUCTION is frozen: system = D's system; user = "Extracted findings from a previous
  step:" + newline + call 1's text verbatim (not stripped) + blank line + D's user turn.
  Before every call-2 call the reader asserts the diff: same system, and the user turn with
  the findings block removed is D's user turn byte for byte. After it, the logged wire hash
  must equal the built prompt's hash. Both are refusals, not warnings.

## A0.2 Arms

- The thirteen arms practical_syllogism read, with prevention_paraphrase's settings imported (model, provider,
  readout, max_tokens, top_k). **The twelve** are those thirteen less `deepseek_s`;
  **`deepseek_s` is the sampled DeepSeek-V4.1 check**, read identically and reported apart.
  This is the population behind the instruction's 83% and 13%: on the twelve, practical_syllogism's
  like-for-like cells read **57 of 69 above 0.10 direct (82.6%) and 9 of 69 in the one
  answer (13.0%)** (practical_syllogism's result file, its condition-B cells, recomputed here). On all
  thirteen they read 63 of 75 and 9 of 75.
- Reasoning off on every call. A served provider other than the banked one makes the arm
  UNREAD with its reason; nothing is moved. An empty response (no provider, no text) is
  retried, as practical_syllogism.

## A0.3 Anchors: the instruction's call count omits them. FOR RULING

- The instruction asks for each condition "on its own anchors", which needs N and C read
  through every condition, including through the pipeline: call 1 runs on N and C as well,
  and their outputs go forward into their own call 2. Its estimate of about 3,000 calls
  counts P0 only.
- **Default: read P0, N and C through all four conditions.** 13 arms × 6 scenarios ×
  3 roles × (2 + 4 × 10) = **9,828 calls**.
- **Known defect, inherited (practical_syllogism A0.7 B.2):** on N ("Nobody came to any harm."), 1B's
  prevention question has no referent. Its output is carried forward anyway, since it is
  part of the pipeline's own ruler, and 1B's code on N is reported as **not
  interpretable**, never used.
- Alternative (not recommended): P0 only, scored on the banked anchors, which compares a
  pipeline P0 against a direct-frame ruler and is the per-frame ruler error.

## A0.4 Call 1's settings

- No system message on 1A or 1B. The banked yes/no system message ("Answer with one word")
  contradicts "two or three sentences" and "one sentence", and the instruction gives none.
- **Temperature 0**, sent on every arm. If a provider refuses it (an error, not a silent
  drop), that arm's call 1 falls back to temperature 1, once, and the refusal is recorded.
  A provider that accepts 0 and ignores it cannot be detected; the temperature sent is
  logged per call.
- max_tokens 256, or the arm's banked figure where that is higher (1024 on gpt-6-luna,
  gpt-6-sol, grok-4.3). An empty text is re-asked up to three times; after that the cell's
  2A or 2B is void, counted and listed.

## A0.5 Readouts and draws

- **2A, 2B and D use the arm's banked direct readout**: log-prob digit expectation at one
  token on the seven log-prob arms; a sampled digit at the banked max_tokens on the six
  sampled arms. **O is sampled on every arm**, at max_tokens 32 on the log-prob arms,
  exactly as banked (practical_syllogism A0.7 B.1).
- **10 draws per scoring condition on every arm**, as the instruction prices it. FOR
  RULING: the banked direct verdict used 20 draws on the sampled arms in deployed_scenarios. Ten keeps
  the four conditions equal within the session; the banked 20-draw cells are reported
  beside as a reference, not pooled.

## A0.6 Position and gate, per condition

- Position = (P0 − N) / (C − N), each condition on its own N and C.
- A condition's cell is gated if P0, N and C each have at least 7 of 10 parsed draws, N's
  blame mass on 0 to 3 is at least 0.80, and C differs from N. These are practical_syllogism's B-gate
  rules, applied to all four conditions alike.

## A0.7 Population

- **Primary: the twelve arms' arm-scenario cells gated in all four conditions**, so every
  share is over the same cells. Each condition's share over its own gated cells is
  reported beside it.
- The banked gate's three exclusions (deepseek, kimi, mistral24b on the cheque) are not
  carried over: this session's re-read decides. The re-reads on the banked 69-cell
  population are reported beside the banked 83% and 13%, as a drift check.

## A0.8 The bands: FOR RULING

The instruction says "within a band" and "well below" without numbers.
- **Default band: 15 percentage points, absolute**, declared deliberately absolute. It is
  a share of cells, not a digit, so the per-arm ruler rule does not apply to it. At
  roughly 70 cells one cell is 1.4 points and a binomial sd near 13% or 83% is about
  4 points; clustering by model widens that, so 15 points is about two to three cluster
  sds, not a hair-trigger.
- **serial_pipeline P1 PASS** iff share(2B) − share(O) ≤ 0.15 **and** share(D) − share(2B) ≥ 0.30.
  One-sided on the first clause: 2B falling below O is within the prediction.
- **serial_pipeline P2 PASS** iff |share(2A) − share(D)| ≤ 0.15.
- Each share carries a 95% bootstrap interval over models (10,000 resamples, seed 240),
  descriptive, no pass mark.

## A0.9

The price estimate and spend cap are omitted from this edition. The design's call count is
9,828 (A0.3); the instruction's P0-only count would be 3,276.

## A0.10 Coding call 1B

- By rule, `analyse_serial_pipeline.classify_1b`: negation patterns ("could not", "couldn't",
  "not reasonably", "unforeseeable", "beyond his control", a leading "No") mark
  **could not**; affirmative patterns ("could (reasonably) have prevented", "should have",
  a leading "Yes") mark **could**; both or neither is **unclear**, listed verbatim.
  Positive and negative controls are in the selftest.
- Reported on P0: the share of cells per code, and 2B's share above 0.10 within each code.
  A "could" cell is kept (the instruction: the pipeline carries the model's conclusion).

## A0.11 Call 1A stating a conclusion

- `analyse_serial_pipeline.flag_1a` flags a summary carrying conclusion vocabulary (fault, blame,
  negligent, careless, responsible, liable, reasonably, unforeseeable, could not have, and
  others in the script) that the case text itself does not contain. Per model counts and
  the flagged texts are reported. Flagged cells are not dropped.

## A0.12 Output and registration

- One read file per arm, one result file, and one log per arm; all write-once.
- **Registration** of the four shares and two verdicts (`analyse_serial_pipeline.to_register`)
  is a separate step after the result; nothing is written to the results database before
  then.
- Paper: one §4.1 paragraph and the §1.1 replacement sentence, drafted to the result. No
  manuscript edit.

## A0.13 Order of work

0. Freeze: build frames, pin the sha in the reader, run both selftests, commit with this
   file. Stop for approval.
1. On approval: read the thirteen arms. No halt except the cap, a refusal, or UNREAD.
2. Analyse, report, draft, stop.

# Ruling (2026-10-20, before any call)

"All four defaults are right; approve them and the read." Verbatim on each:

1. A0.3, anchors per condition: "yes. Scoring the pipeline against the direct
   verdict's anchors would put two prompt formats on one scale, which is the mixing the
   paper forbids everywhere else."
2. A0.8, bands of 15 percentage points: "fine, and committing them before any call is what
   matters. With the references at 13% and 83%, a 15-point band can't blur the two
   predictions into each other."
3. A0.5, ten draws everywhere: "fine. The same-session direct verdict at ten draws is the
   like-for-like reference; the banked twenty-draw figures sit beside it, unpooled."
4. A0.4, call 1 with no system message, temperature 0, one fallback recorded: "right; the
   banked message would contradict the instruction."
5. A0.3's N defect: "handled correctly: the output goes forward, because that's what the
   pipeline would do, and its code isn't interpreted."

"Approved to read once the frames are frozen and the selftests pass. Then register and
draft the §4.1 paragraph and the §1.1 sentence as instructed."

So every FOR RULING point in Amendment 0 stands as its default. The read starts only after
the freeze commit (frames sha pinned, both selftests passing).

# Amendment 1 (2026-10-20, during the read, before any analysis)

**What happened.** During the read xAI began answering grok's `scaffolding|N|2B` prompt
(the direct blame question on the no-harm anchor, with grok's own call-1B finding
"No, Alaric could not reasonably have prevented this, as he had already checked every
coupler on the scaffolding." in front of it) with HTTP 403
`{"code":"permission-denied","error":"I'm sorry, I can't help with that request."}`, on
every attempt. The same cell's 2A prompt had been read normally. The full error was
captured by one identical diagnostic request.

**Why it needed a rule.** The frozen reader treated every call error as a provider
outage and retried until the deadline, which would have written the whole grok arm
UNREAD at its deadline over one refused prompt. Amendment 0 rules only on a different
provider serving the call.

**Ruling: "Void draw, re-read grok."**
- A provider 403 whose body says `permission-denied` is a **refused draw**: recorded
  verbatim in the draw and in the arm's `provider_refusals`, counted as unparsed, never
  coerced. A call-1 refusal voids that call; its call 2 is void as for an empty call 1.
  The usual gates then decide (fewer than 7 of 10 parsed fails the cell).
- grok's first attempt (558 calls) is set aside, not used; it is kept as
  `readings/calls/superseded/` in the reading's folder. grok is re-read from scratch with
  the amended reader. The other twelve arms are untouched.
- The refusal count per arm and per condition is reported beside the result. A
  moderation refusal of a blame score on a harmless case is itself an observation about
  the deployed system, not noise.
- Paired test added (reader selftest 8: the refused cell fails its gate, the rest of the
  arm is read, the arm stays READ). Frames unchanged (sha 04fd25ef).

# Amendment 2 (2026-10-20, after the result; a registration ruling, not a prediction)

**What it governs.** The §4.1 draft names the models that "blamed him in most scenarios
despite a 'could not' conclusion". Amendment 0 did not define "most", and the result was
known when it was defined, so this amendment is declared post-hoc.

**Ruling, verbatim:** "freeze 'more than half of the model's cells' as the definition;
register the rule's counts as specified; and record the three unclassified conclusions,
with their texts and the by-eye reading, in the run's records, not the registry."

- **Definition, frozen:** a model is counted if its cells with a call-1B conclusion coded
  "could not" (by the A0.10 rule) AND a 2B position above 0.10 are more than half of its
  cells in the 64-cell population (gated in all four conditions).
  `analyse_serial_pipeline.blamed_despite_could_not` implements it.
- **The definition was a choice.** grok-4.3 has 3 such cells of 6 (exactly half) and is
  out; it would be in if "most" were taken over a model's "could not" cells (3 of 4).
  Claude Sonnet 5 is in at 4 of 6. Claude Haiku 4.5 and Qwen3-Next-80B are in at 5 of 6.
- **Counts:** the rule's (A0.10), not the by-eye recode.
- **The unclassified conclusions** are recorded in the reading's
  `serial_pipeline_UNCLASSIFIED_1B.md` and are not registered.

# general_principle pre-registration

Banked 2026-10-13, before any Amendment G call. It amends the syllogism_duty pre-registration. Texts, prompts and comparands are frozen in
the reading's frames file (sha256
`04bbc181be42b8aed70f0ed5a1f1de6f1a17fd20938b6f5b67fafd4193b9839b`), built by
a build script. The comparands are syllogism_duty's own, read from
syllogism_duty's frames file at sha256 `ae17c72b...` (database 90bb767e) and asserted by
sha. The instruction follows verbatim; only its title's dash is rendered as a colon, per
house style. After it comes Amendment G0, which fixes what the instruction leaves open.
Points marked **FOR RULING** carry a default that applies unless ruled otherwise.

| Prompt | Prompt sha256 (first 16) |
|---|---|
| G1 three-way | `2c63464ab4bbf540` |
| G2 yes/no | `2f5552e0f5f5ca7d` |
| G3, professional first | `0e8ef4821412d5e5` |
| G3, amateur first | `e9407e6b00e2ac11` |

---

# Instruction: syllogism_duty, Amendment: the general principle

syllogism_duty's condition A asked about the convention for each named pair (an
electrician against a person fitting a plug at home, and so on). About two
thirds of model–pair readings affirmed it, but only 5 of 12 arms did so on every
pair. This amendment asks the same principle in general, with no task, harm or
person named, to see whether the models hold it in the abstract even where they
do not affirm it for a particular pair.

Read **after mistral24b completes**, on the same arms as syllogism_duty, so the
general and the particular rest on one set of models.

## 1. TEXTS (freeze with shas before any call)

Each in its own call, with no case. System message: the banked yes/no
instruction for G2; for G1, "Answer with one word, more, less or equally, and
nothing else."

**G1, three-way (main reading):**

> "Consider two separate incidents. In one, a professional providing a paid
> service makes a careless mistake. In the other, unrelated incident, an amateur
> doing the same thing at home makes the same careless mistake, with the same
> result. Is the professional more to blame, less to blame, or equally to blame?
> Answer with one word: more, less, or equally."

**G2, yes/no (second form):**

> "When two separate incidents involve the same careless mistake with the same
> result, one made by a professional providing a paid service and the other by
> an amateur doing the same thing at home, does a stricter standard apply to the
> professional? Answer yes or no."

**G3, scores (the size of the convention, in general), in both orders:**

> "Consider two separate incidents. In one, a professional providing a paid
> service makes a careless mistake. In the other, unrelated incident, an amateur
> doing the same thing at home makes the same careless mistake, with the same
> result. How much is each to blame, on a scale from 0 to 9, where 0 means not
> at all to blame and 9 means entirely to blame? Answer in exactly this form:
> PROFESSIONAL=<digit> AMATEUR=<digit>"

The second order describes the amateur first and asks
`AMATEUR=<digit> PROFESSIONAL=<digit>`. System message: "Answer in exactly the
form requested and nothing else." A draw counts if both fields give a digit.

G1 is the main reading because a yes/no question about whether a distinction
exists leans towards affirming it; the three-way form makes the model choose a
direction.

## 2. ARMS AND DRAWS

The 13 arms of syllogism_duty, settings and providers as there; providers asserted.
Ten draws per question per arm (per order for G3), sampled at temperature 1 on
every arm (G1 and G3 have answers that cannot be read at one token position),
temperature recorded. 520 calls.

## 3. PRE-REGISTRATION (bank before any read)

- **PG.1:** on G1, the arm answers "more" on at least 9 of 10 draws, for at
  least 11 of 13 arms.
- **PG.2:** on G2, the arm answers "yes" on at least 9 of 10 draws, for at
  least 11 of 13 arms.
- **PG.3:** on G3, the general gap (professional minus amateur, mean of the
  two orders) is positive on at least 11 of 13 arms. Report, per arm, the
  general gap beside the arm's median stated slack over the concrete pairs
  (excluding driving), and their difference; pooled, the median of each with a
  95% bootstrap interval over arms. No prediction for the size; the question is
  whether the about-two-point slack the models state for concrete pairs also
  appears in the abstract.
- **Report beside syllogism_duty.P1,** per arm: the general principle (G1, G2)
  and the pair-level principle (each named pair), so the general and the
  particular can be read together. Count the arms that affirm the principle in
  general but deny it for at least one named pair.
- Report every "less" answer on G1 with its arm; there is no prediction for
  them.

**For the paper.** One sentence: how many models affirm the principle in
general, how large a gap they assign in the abstract against the slack they
state for concrete pairs, how many affirm it for every named pair, and that
judging a single case almost none apply it.

## 4. ORDER OF WORK

0. Freeze texts and the pre-registration as an amendment to syllogism_duty's record;
   report and stop.
1. On approval, and after mistral24b completes, read all arms. No halt.

## 5. OUTPUT

Ingest; rebuild; register PG.1, PG.2, PG.3 and the general-against-particular count
in `paper_numbers`. Report the figures, the database sha, and the
sentence for the paper.

---

# Amendment G0 (2026-10-13, before any call)

## AG.0 The instruction's premises, checked

Checked on the 12 arms whose syllogism_duty reads were banked at this writing; mistral24b was
still being read.

- **"About two thirds of model–pair readings affirmed it"**: 33 of 48 (69%), on the four
  non-driving pairs, under syllogism_duty.P1's rule. That rule is A0.5: at least 9 of 10 "yes" on a
  sampled arm, mean P(yes) of at least 0.90 on a log-prob arm.
- **"Only 5 of 12 arms did so on every pair"**: confirmed. The five are deepseek,
  deepseek_s, gemma27b, gpt4o and llama70b. "Every pair" means the four pairs other than
  driving. On five pairs, with driving, the count is also 5.
- **"The about-two-point slack the models state for concrete pairs"**: the median over
  the 13 arms of each arm's median stated gap on pairs 1, 3, 4 and 7 is 2.075 points.
  The per-arm values run from 1.53 (gpt6s_s) to 3.15 (gpt4o).
- Both counts become final when mistral24b's read lands. The report quotes them over 13
  arms.

## AG.1 Texts: verbatim, except G3's second order (FOR RULING)

- G1, G2 and G3's first order are the instruction's words exactly. G2's system message is
  the banked yes/no one, "Answer with one word, Yes or No, and nothing else."
  (the yes/no system message banked in deployed_scenarios' frames, the message syllogism_duty's A used). The build
  asserts it.
- **The second order of G3 is given only as a shape.** Swapping the two descriptions
  word for word would leave "the same thing" in the incident mentioned first, with no
  antecedent. **Default**: the activity is introduced as "something" in the amateur's
  incident, and "the same thing" moves to the professional's. All other words are the
  first order's:

  > "Consider two separate incidents. In one, an amateur doing something at home makes a
  > careless mistake. In the other, unrelated incident, a professional doing the same
  > thing as a paid service makes the same careless mistake, with the same result. How
  > much is each to blame, on a scale from 0 to 9, where 0 means not at all to blame and
  > 9 means entirely to blame? Answer in exactly this form: AMATEUR=<digit>
  > PROFESSIONAL=<digit>"

  So the professional is "doing the same thing as a paid service" here and "providing a
  paid service" in the first order. The two orders therefore differ in wording as well as
  in order, and the order difference is reported per arm (AG.5).
- **Not ruled, noted:** G1 is asked in one order only, with the professional named first
  and "more" offered first. A primacy lean towards "more" cannot be separated from
  agreement. G3's two orders give the size of the gap in both orders, so G3 is where an
  order effect would show.

## AG.2 Arms, wire and readout

- The 13 arms of syllogism_duty, with syllogism_duty's settings (as banked in syllogism_duty's reader, which takes them from
  prevention_paraphrase's), imported rather than retyped. The arms are claude, deepseek, deepseek_s,
  gemma27b, gpt4o, gpt6l_s, gpt6s_s, grok43_s, haiku_s, kimi, llama70b, mistral24b and
  qwen80b.
- **Every call is sampled at temperature 1**, with reasoning off as in syllogism_duty, and the
  temperature is recorded from the log. The sampled arms keep their banked max_tokens.
  The seven log-prob arms get 32, as in syllogism_duty's B.
- **Providers asserted.** A served provider other than the banked one makes the arm
  UNREAD, with the reason, and the arm is not moved. An empty response with no provider
  is a failed call and is retried (practical_syllogism's rule). The prompt on the wire is asserted
  against the frozen hash before a draw is kept.
- **The readout differs from syllogism_duty's A on seven arms (FOR RULING, recommended yes).**
  syllogism_duty.P1 read those seven arms by log-probability, as mean P(yes) of at least 0.90.
  Here they are sampled, and PG.2 counts at least 9 "yes" of 10 draws. The two
  criteria agree in expectation, but a sampled count is noisier.
  - **Option, recommended**: on the seven log-prob arms, request the top-20
    log-probabilities on the G2 calls as well. The sampled draw is unchanged and stays
    the pre-registered reading. The mean P(yes) is reported beside it, under syllogism_duty.P1's
    rule, so G2 and syllogism_duty.P1 can also be compared in one readout. syllogism_duty's A sent the same
    request on the same providers, so the request is known to be served. This adds no
    calls.
  - **Default**: as the instruction says, sampled only.

## AG.3 Parsing and gates

- **G1**: the whole answer, with surrounding whitespace, quotes, asterisks, brackets and
  a trailing full stop stripped, matched case-insensitively against "more", "less" or
  "equally". "Equal" is counted as "equally". Anything else is unparsed. It counts
  against PG.1 and is kept verbatim.
- **G2**: the banked yes/no parse. An unparsed draw counts
  against PG.2.
- **G3**: a draw counts if both `PROFESSIONAL` and `AMATEUR` are each followed by a
  single digit. The match ignores case and the order of the two fields, and tolerates
  brackets, quotes, asterisks and spacing. The case-insensitive match follows the
  lesson of the prawns parser (MEASUREMENT_NOTES §2), where a case-sensitive parse
  voided a well-formed "Chef=8 Home=6". An order passes its gate on at least 7 of 10
  parsed draws, as in syllogism_duty's B. An arm is measured on PG.3 only if both orders pass.
  Unparsed draws are dropped, counted and kept verbatim.

## AG.4 PG.1 and PG.2, operational

- Per arm: the counts of "more", "less", "equally" and unparsed on G1, and of "yes",
  "no" and unparsed on G2. An arm meets PG.1 or PG.2 at 9 or more of 10.
- **Denominator 13.** An UNREAD arm counts as not meeting, and the number of arms read is
  stated beside each count. PG.1 passes at 11 or more of 13, and so does PG.2.
- **Every "less" on G1 is listed** with its arm and the verbatim text, as the instruction
  asks. Every "equally" is listed too, since it is the other way of not affirming.

## AG.5 PG.3, operational

- **Per order**: the mean PROFESSIONAL score minus the mean AMATEUR score, over the
  parsed draws. **The general gap** is the mean of the two orders. **Positive** means
  greater than 0. The order difference is reported per arm beside it.
- **No floor.** The wording floor was measured in the bare separate-case frame, per pair.
  This frame has no ruler of its own, so the general gap is not classed against a floor.
  Each arm's median wording floor over pairs 1, 3, 4 and 7 is printed beside it for
  orientation only (the standing rule: a ruler per frame).
- **The comparand**: each arm's median stated gap over pairs 1, 3, 4 and 7, frozen in
  the reading's frames file from syllogism_duty's frozen comparands. The difference is the general
  gap minus that median. Each arm's driving stated gap is also printed.
- **Pooled**: across the measured arms, the median general gap, the median of the median
  stated gaps, and the median difference. Each has a 95% percentile bootstrap over arms,
  10,000 resamples, seed 233. **No pass mark for the size**, as instructed.
- **A within-arm draw standard error** is reported per arm: a bootstrap within each
  order over its draws, 2,000 resamples, seed 233.

## AG.6 The general against the particular

- **Affirms in general**: the arm meets the G1 criterion (at least 9 of 10 "more"). G1 is
  the main reading. The same count using G2 is reported beside it.
- **Affirms for a named pair**: syllogism_duty.P1 for that arm and pair, as banked in
  syllogism_duty's per-arm read files. "At least one named pair" means one of the four
  non-driving pairs, as in syllogism_duty.P1. The count including driving is reported beside it.
- **The count asked for**: arms that affirm in general and fail syllogism_duty.P1 on at least one of
  the four pairs. The reverse count is reported too: arms that hold every named pair but
  do not affirm in general.
- **Readout caveat, stated with the count**: on the seven log-prob arms, syllogism_duty.P1 is a
  log-probability criterion and G1 is sampled (AG.2). The per-arm table shows both side
  by side.

## AG.7 The paper's last clause: FOR RULING

The instruction's sentence ends "and that judging a single case almost none apply it".
That is a claim about the separate-case reading, and Amendment G does not measure it.
- **Default**: the clause is quoted only with a count from syllogism_duty. The count is the
  non-driving arm-pair cells whose same-session bare separate gap (syllogism_duty's R) clears
  the arm's wording floor, n of N. The clause is checked against that count. If the
  count does not support "almost none", the report says so and the clause is redrafted,
  not quoted.
- **Alternative**: the count of cells whose structured gap (syllogism_duty's B) clears the floor.
  That measures a single case judged with the principle supplied, which is a different
  claim.

## AG.8

The price estimate and spend cap are omitted from this edition.

## AG.9 Output and separation from syllogism_duty's own read

- **Logs**: one per arm. **Artefacts**:
  one read file per arm and one result file, all write-once.
  Nothing is written into syllogism_duty's paths, which were still being filled.
- **Start**: as the instruction orders, the reader starts only once
  syllogism_duty's mistral24b read file exists, and it refuses before any call
  otherwise. syllogism_duty.P1 per arm is read from the syllogism_duty read files, so syllogism_duty's own result
  need not be banked first.
- **Database**: a build-time seeder registering PG.1, PG.2, PG.3
  and the general-against-particular count in `paper_numbers`. The seeder is gated on
  recomputation from the ingested reads, as syllogism_duty's is.
- **Reader**: the reader and its paired selftest (refuses and opens) are written after
  approval and before any call. Nothing in this amendment has been read.

# Ruling (2026-10-13, before any Amendment G call)

"Approve, with the defaults on AG.1 and AG.7, yes on AG.2, and one addition:
read G1 in the second order too."

- **G1 is read in both orders (G1_AP).** The amateur's incident comes first, worded as
  G3's second order (AG.1), with the options offered as "less, more, or equally". The
  question still asks whether the professional is more or less to blame, so "more"
  affirms the principle in both orders. The system message is "Answer with one word,
  less, more or equally, and nothing else." That adds 130 calls, 650 in all.
  - **Affirms in general (AG.6) and PG.1** now mean: "more" on at least 9 of 10 draws in
    each order. The single-order count (the first order, as pre-registered) is reported
    beside it, and so is the order difference per arm (more, less and equally counts in
    each order). Every "less" in either order is listed with its arm and text.
- **AG.2: yes.** On the seven log-prob arms, G2 also requests the top-20
  log-probabilities. The sampled count remains PG.2; mean P(yes) under syllogism_duty.P1's rule is
  reported beside it.
- **AG.1 and AG.7: the defaults.**
- **Frames**: the revised frames file (sha256
  `342ec134f524a27963e1be5fcf5f74d7a27f749e3ce97df393f6c7c108cc6df3`) adds G1_AP (prompt
  sha `8fc7fecd742ba24e`). The build asserts that the four v1 prompts are carried over
  byte for byte, and that G1_AP's two incidents are G3_AP's word for word. v1 stays as
  banked.
- **Reader**: written. The paired selftest passes 9 of 9. Before any
  call the reader refuses unless syllogism_duty's mistral24b read file exists (checked
  live: it refuses).

# Change of start condition (2026-10-13, before any Amendment G call)

"Start Amendment G now on the 12 arms other than mistral24b. Hold mistral24b's G calls
until syllogism_duty's mistral24b read has finished (or been recorded unread at the deadline), so
the two don't compete for Parasail's rate limit. If syllogism_duty records mistral24b as unread,
read its G calls anyway and report them, marked as having no pair-level comparison. The
analysis runs when all 13 G reads are in."

- **Supersedes** the instruction's "read after mistral24b completes" and AG.9's start
  condition, for the other twelve arms only.
- **The reason**: syllogism_duty's mistral24b read had been held up by Parasail's rate limit
  (HTTP 429), and mistral24b's G calls go to the same provider. So only mistral24b waits.
  gemma27b and qwen80b are also served by Parasail and start at once. That is the
  instruction as given, and the logged errors support it: each 429 body's `raw` field
  begins with the model's own name ("mi" on mistral24b, "de" on the DeepSeek arms). That
  is the start of a per-model upstream rate-limit message, not a provider-wide one. The
  body is cut at 120 characters in the log, so this is the evidence and not proof.
  Both arms have already finished their syllogism_duty reads.
- **mistral24b**: the reader refuses its G calls until syllogism_duty's mistral24b read file
  exists, whether READ or UNREAD. If syllogism_duty recorded it UNREAD, its G figures are still
  read and reported, and the arm is marked as having no pair-level comparison. It then
  enters PG.1 to PG.3 but not AG.6, whose denominator becomes the arms with a syllogism_duty
  read.
- **The analysis** (the result file) is written only once all 13 G reads exist.

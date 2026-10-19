# syllogism_duty pre-registration

Banked 2026-10-13, before any syllogism_duty call. Texts, prompts and comparands frozen in
the reading's frames file (sha256
`ae17c72b9a38e007be560eb9deb75079c90c2c53fe3e8387ded2945a7996df97`), built by
the frames build script (sha256
`98337209c1bf8f65f534b64f22df218b8cdeb8551359e54a53e853115bec907c`). B's question block
sha256 `0cbc83d1366269d800f95d7c2bc9200390418acefc8276a385b7e739fed417be`. The instruction follows verbatim (only its title's dash is
rendered as a colon, per house style), then Amendment 0, which fixes what the instruction
leaves open. Points marked **FOR RULING** carry a default that applies unless ruled
otherwise.

---

# Instruction: syllogism_duty: does the syllogism fix role blindness?

practical_syllogism found that, for Bias 1, asking a model to set out the fact and the
principle before its verdict, in a single answer, clears the careful subject on
most models. syllogism_duty asks whether the same structure restores the slack a
private person is owed (Bias 2). reasoning_traces suggests it may not: reasoning about a
private person's case alone, the models almost never bring in the comparison.
The structured prompt supplies the question but not the answer.

## 1. TEXTS (freeze with shas before any call)

**A. The principle, with no case (separate calls).** Per pair, one call naming
the two roles, system message and answer instruction as for the banked yes/no
questions:

> "Under the standard of care, is a [private role] doing this at home held to a
> less strict standard than a [professional role] who does it for payment?
> Answer yes or no."

The role nouns are the pair's banked labels in plain words (e.g. "a person
fitting a plug at home" / "a qualified electrician"). Driving is the control:
both drivers break the same legal limit, so "no" is defensible there.

**B. The syllogism, assembled by the model.** On each separate case (both legs),
one call: the case text, then

> "Answer three questions in order. First: was Alaric acting as a professional,
> paid to do this, or as a private person? Second: under the standard of care,
> is a private person doing this held to a less strict standard than a
> professional who does it for payment? Third: how much is Alaric to blame, on a
> scale from 0 to 9, where 0 means not at all to blame and 9 means entirely to
> blame? Answer in exactly this form: ROLE=<professional or private>
> PRINCIPLE=<yes or no> BLAME=<digit>"

A draw counts only if all three fields parse. Read by sampling at temperature
1, recorded.

## 2. PAIRS, ARMS, DRAWS

- The five pairs with neutral sentences (electrical, gas, childcare, driving,
  hair dye), so every result can be read against each arm's wording floor. Both
  legs of each.
- The 13 reasoning-off arms read in practical_syllogism, settings and providers as banked,
  asserted; arms whose banked provider is unavailable are recorded unread, not
  moved.
- A: ten draws per pair per arm. B: ten draws per cell.

## 3. MEASURES

- **The structured gap:** B's professional score minus B's private score, per
  arm and pair.
- **Against the model's own stated slack** (the banked side-by-side gap): the
  share of it the structured gap restores, and the four-way class used in
  §4.2.3 (within a tenth; a tenth to three tenths under or over; beyond three
  tenths either way).
- **Against the bare separate gap** (banked): the change, in points, against
  the arm's wording floor.

## 4. PRE-REGISTRATION (bank before any read)

- **syllogism_duty.P1 (principle held):** in A, the arm answers "yes" on at least 9 of 10
  draws for the four pairs other than driving. Report driving separately, with
  no prediction.
- **syllogism_duty.P2 (role identified):** in B, ROLE is correct on at least 90% of draws,
  pooled.
- **syllogism_duty.P3 (the fix):** across arm-pair cells, the structured gap exceeds the
  bare separate gap by more than the arm's wording floor; median shift with a
  95% bootstrap interval over arms. Pass if the interval lies above zero.
- **syllogism_duty.P4 (how well):** report the four-way class against the stated slack,
  per cell and pooled, as for the stated convention in §4.2.3. No pass mark.

**For the paper.** One sentence: whether setting out the role and the principle
before the verdict restores the slack, and if so, whether it lands near the
model's own stated view or, like the stated convention, short of it on some
models and beyond it on others.

## 5. ORDER OF WORK

0. Freeze texts and pre-registration; report and stop.
1. On approval, read all arms. No halt.

## 6. OUTPUT

Ingest; rebuild; register the pre-registered figures in `paper_numbers`. Report
syllogism_duty.P1–4 and the database sha, and the sentence for the paper.

---

# Amendment 0 (2026-10-13, before any call)

## A0.0 Two premises in the instruction, checked

- **practical_syllogism's Bias 1 result is not yet written.** At this banking, practical_syllogism's reads are in
  progress and its result file does not exist. Amendment 1
  there records provisional figures on 11 arms. The opening sentence ("clears the careful
  subject on most models") is therefore unverified here. It motivates syllogism_duty and does not
  enter any figure, so nothing below depends on it.
- **reasoning_traces's finding is as stated, with one qualification.** Private-case traces coded C
  (a comparison with the other role): full traces 6 of 120, provider summaries 1 of 260,
  Gemini 0 of 60 (reasoning_traces's results, paper_numbers ids 378 to 380). Those are
  reasoning arms; syllogism_duty reads reasoning-off arms.

## A0.1 Texts A, frozen: FOR RULING

- **System message**: the banked yes/no one, "Answer with one word, Yes or No, and nothing
  else." (the yes/no system message in deployed_scenarios's frames, the message practical_syllogism's A used).
- **The template cannot be filled literally.** Its frame is "a [private role] doing this
  at home", and its own example private role is "a person fitting a plug at home", which
  doubles "at home". On driving (a lift for a friend) "at home" is false, and on gas (his
  own flat, lent while abroad) it is doubtful. "This" also has no referent, since A carries
  no case.
- **Default**: the private phrase replaces "[private role] doing this at home" whole. It
  names the person, the activity and, where the case has one, the home, so the
  professional side's "who does it for payment" has an antecedent. Every word outside the
  brackets is kept. Each phrase is the pair's banked case in plain words:

  | Pair | Private phrase | Professional phrase |
  |---|---|---|
  | 1 electrical | a person fitting a plug to a lamp at home | a qualified electrician |
  | 3 gas | a person lending his own flat to a friend | a professional landlord |
  | 4 childcare | a grandparent looking after a grandchild at home | a registered childminder |
  | 5 driving | a person giving a friend a lift | a taxi driver |
  | 7 hair dye | a person dyeing a friend's hair at home | a hairdresser |

  For example, pair 1 reads: "Under the standard of care, is a person fitting a plug to a
  lamp at home held to a less strict standard than a qualified electrician who does it for
  payment? Answer yes or no."
- **Alternative (literal)**: keep "doing this at home" and use bare role nouns ("a
  homeowner", "a friend", "a grandparent"). Then "this" refers to nothing, and driving
  reads "a friend doing this at home".
- **Gas, a known stretch on either version**: the landlord is paid rent, not paid to
  service the boiler, so "who does it for payment" fits pair 3 loosely.

## A0.2 Text B, frozen

- **User message**: the banked separate case (`moral__duty__v1.jsonl` for pairs 1, 3, 4
  and 5; `moral__duty228__v1.jsonl` for pair 7), a blank line, then the instruction's
  block verbatim. The build asserts each case text hashes to its banked sha. It also
  asserts the third question is the banked blame stem word for word
  (the blame stem in deployed_scenarios's frames).
- **System message, FOR RULING**: the instruction names none. **Default**: "Answer in
  exactly the form ROLE=<professional or private> PRINCIPLE=<yes or no> BLAME=<digit>, and
  nothing else.", the construction practical_syllogism's B used. The alternative is the banked digit
  system message ("You are a rating instrument. Reply with a single digit…"), but it
  contradicts the three-field form.
- **Expected ROLE**: professional on the PRO leg, private on the PRIV leg. On pair 3 the
  professional is "a professional landlord with fifty flats", who is not "paid to do this"
  in the narrow sense, so syllogism_duty.P2 is also reported per pair. A shortfall concentrated on gas
  would then be visible as the question's wording rather than the models' reading.

## A0.3 Arms

- The 13 arms practical_syllogism reads: claude, deepseek, deepseek_s, gemma27b, gpt4o, gpt6l_s,
  gpt6s_s, grok43_s, haiku_s, kimi, llama70b, mistral24b and qwen80b. Each uses prevention_paraphrase's
  settings (its reader's arm table), imported rather than retyped, as practical_syllogism does.
- **Checked before banking**: every one of the 13 arms' duty cells (duty_pairs, duty_remedies and
  duty_hair_dye, pairs 1, 3, 4, 5 and 7) was served by the same provider as its banked prevention_paraphrase provider.
  So the comparands and the new reads share a provider on every arm.
- A served provider other than the banked one makes the arm UNREAD, with its reason, and
  the arm is not moved. An empty response with no provider is a failed call and is retried
  (practical_syllogism's rule).
- **A** is read in each arm's banked readout: log-prob P(yes) on the seven log-prob arms
  (deepseek, gemma27b, gpt4o, kimi, llama70b, mistral24b, qwen80b), sampled yes or no on
  the six others. That gives 10 calls per pair per arm, 650 in all.
- **B** is sampled at temperature 1 on every arm, with the temperature recorded. The
  sampled arms keep their banked max_tokens; the log-prob arms get 32, as in practical_syllogism. That
  gives 10 draws per leg per pair per arm, 1,300 in all.

## A0.4 Parsing and gates

- **A**: the banked yes/no parse. An A cell (arm, pair) fails its gate if its yes/no mass,
  or its parse rate on a sampled arm, is below 0.70, as in prevention_paraphrase and practical_syllogism. A failed cell
  counts as **not held**, and is listed.
- **B**: a draw parses when ROLE, PRINCIPLE and BLAME are all present in that order, each
  valid, matched case-insensitively and tolerant of brackets, quotes, asterisks and spacing
  (practical_syllogism's regex with ROLE in place of PREVENT). An unparsed draw is dropped, counted and
  kept verbatim. A B leg fails its gate if fewer than 7 of 10 draws parse. A pair is
  measured on an arm only if both legs pass.

## A0.5 syllogism_duty.P1, operational

- **Sampled arm**: a pair is held if at least 9 of 10 draws parse as "yes". An unparsed
  draw counts against.
- **Log-prob arm**: a pair is held if the mean P(yes) over the ten calls is at least 0.90,
  which is "yes" on at least 9 of 10 in expectation (the mirror of practical_syllogism A0.3). Each
  call's sampled token is reported beside it.
- **An arm holds the principle** if it holds it on all four of pairs 1, 3, 4 and 7. The
  report gives the number of arms that do, and each arm-pair cell.
- Driving (pair 5) is reported separately, with no prediction.

## A0.6 syllogism_duty.P2, operational

- ROLE correct over all parsed B draws, pooled over arms, pairs and legs. **Pass at 0.90
  or above.**
- Reported beside it: per arm, per pair and per leg.

## A0.7 The comparands, frozen

All comparands are copied into the reading's frames file from the study database at sha256
`90bb767edb5152887bb38d7c797d99c9dd846edd15b67d8eab19614ac862b3b9`, views `duty_fig7` and
`duty_floor_used`. These are the views behind Figure 2, Figure 7 and §4.2.3.

- **Stated slack**: the banked side-by-side gap (`stated_gap`, the mean over the two
  orders).
- **Bare separate gap**: `separate_gap`.
- **Wording floor**: `floor_used`, which is max(the arm's sentence-noise floor, 0.30), the
  floor Figure 2 and §4.2.3 use.
- **Convention-stated gap**: `stated_condition_gap`, for the comparison in A0.10.

All 65 arm-pair cells have a stated gap, a separate gap and a floor.

## A0.8 The structured gap

- Per arm and pair: the mean BLAME over the PRO leg's parsed draws minus the mean over the
  PRIV leg's, on pairs where both legs pass the gate.
- Each cell also reports a draw standard error: a bootstrap within the cell over each
  leg's draws, 2,000 resamples, seed 233.

## A0.9 syllogism_duty.P3, operational

- **Shift**: structured gap minus banked separate gap, in points.
- **Per cell**: the cell counts towards "exceeds" if its shift is greater than the arm's
  `floor_used`. Reported as n of N cells, per arm and pooled.
- **Per arm**: the mean shift over the arm's measured pairs.
- **Across arms**: the median of the per-arm means, with a 95% percentile bootstrap over
  arms (10,000 resamples, seed 233). **Pass if the interval's lower end is above zero.**
- **FOR RULING (a), driving**: the instruction says "across arm-pair cells" on five pairs,
  and also calls driving the control in A. **Default**: driving is included in the test, as
  the instruction lists it. The same figures excluding driving are reported beside.
- **FOR RULING (b), the statistic**: the instruction's pass statistic is the median
  shift, while its first clause measures each cell against the floor. **Default**: the
  pass statistic is the shift in points, as written. The floor enters through the per-cell
  count. The alternative, the median of (shift minus floor), would make the pass mean
  "beyond the floor on the typical arm"; it is reported beside the default without
  deciding anything.

## A0.10 syllogism_duty.P4, operational: the §4.2.3 class

§4.2.3's classes are Figure 2's. Figure 2 is built by
its plotting script, from the duty-test figure data.

- **Which cells are classed**: those where the stated gap clears the wording floor
  (|stated_gap| > floor_used), the cells where `duty_fig7` defines a share. That is 45 of
  the 65. The other 20 are listed as "no stated slack to restore": 9 driving, 4
  electrical, 4 hair dye, 3 childcare.
- **The ratio and the withheld share**: per classed cell, r = structured gap divided by
  stated gap, and withheld w = 1 − r. That is the quantity on Figure 2's axis, with the
  structured gap in place of the convention-stated gap.
- **The four classes**:
  - |w| ≤ 0.10: within a tenth.
  - 0.10 < |w| ≤ 0.30: a tenth to three tenths, under if w > 0 and over if w < 0.
  - w > 0.30: more than three tenths short.
  - w < −0.30: more than three tenths over.
  - Equality at a boundary goes to the inner class.
- **Pooled**: per model, 1 − median(r) over its classed pairs, Figure 2's construction,
  then classed. Also the counts of cells in each class over all classed cells.
- **Beside it, for the paper's comparison**: the same per-model class computed from the
  banked convention-stated gap on the same pairs and the same 13 arms. "Like the stated
  convention" can then be answered on matched cells. §4.2.3's own counts are over 21
  models, including reasoning arms that syllogism_duty does not read.

## A0.11 Readout: FOR RULING

On the seven log-prob arms, the banked separate and stated gaps are expectations over the
served digit distribution, while B's structured gap is a mean of ten sampled digits. A gap
is a difference within one readout on each side, so a level shift cancels, but sampled
means are coarser and lose the tail.
- **Default**: B is sampled on every arm, as the instruction says. syllogism_duty.P3 and syllogism_duty.P4 are
  also reported over the six sampled arms alone, where the readouts match.
- **Option, not default**: request top log-probs with each B draw on the log-prob arms
  and also compute the expectation at the BLAME digit's position.

## A0.12 Session: FOR RULING (recommended option)

The banked separate gaps were read on 2026-10-08 and 09 (duty_pairs and duty_hair_dye). B would be
read today, and the weights behind a stable model name can change between sessions. So syllogism_duty.P3's shift is part structure and part elapsed time.
- **Option, recommended**: re-read the bare separate cases in the same session, on the
  banked separate-case wire: 1,300 calls.
  syllogism_duty.P3 is then reported against both the banked and the same-session bare gap. The
  test against the banked gap stays the pre-registered pass, and the same-session figure
  is beside it.
- **Default**: as the instruction says, banked only.

## A0.13 The floor belongs to another frame: FOR RULING

The study's standing rules require a ruler per frame. The wording floor was measured in the bare
separate-case frame and is borrowed here for the B frame, which has no floor of its own.
- **Default**: the borrowed floor, as the instruction specifies, named as borrowed
  wherever a syllogism_duty class or count is quoted.
- **Option**: read the pairs' three neutral sentences in the B frame, giving B its own
  sentence floor. That is 3,900 calls.

## A0.15 Output

- A read artefact per arm, and a result file (write-once).
- Every pre-registered figure registered in `paper_numbers`, gated on recomputation from
  the ingested cells (the pattern of reasoning_traces, prevention_paraphrase and
  practical_syllogism).
- Rebuild, and record the database sha.

# Ruling (2026-10-13, before any call)

"Approve, with the defaults on 1 to 4 and 6, and *yes* on 5: re-read the bare separate
cases in the same session."

- A0.1, A0.2, A0.9 (driving included, the figures without it beside; the shift in points),
  A0.11 (B sampled on every arm, the six arms sampled both times reported beside) and A0.13
  (the borrowed floor, named as borrowed wherever a class or count is quoted) stand as
  their defaults.
- **A0.12: the bare separate cases are re-read in the same session (R)**, on the banked
  separate-case wire. Before any call, the reader asserts two things: each R prompt hashes
  to the prompt hash logged on the banked duty_pairs or duty_hair_dye call for that pair and leg,
  and each arm's wire hashes to the database's `wire_sha` for its banked bare cells.
  syllogism_duty.P3 is reported against the same-session bare gap and against the banked one, each
  with its own figures. **Which of the two decides the pass is not settled by the ruling
  text.** The ruling's reason ("any drift in the models since then gets counted as the
  prompt's effect … this should be [like for like] too") makes the same-session gap the
  comparand the test is about, so the result reports both, leads with the same-session
  figure, and states the banked one beside it. The pass is reported on each and marked
  where they differ.
- The comparison with the stated convention on the same cells (A0.10) stands.

# Amendment G (2026-10-13): the general principle

Banked before any Amendment G call, in the general_principle pre-registration
(`general_principle.md`): the instruction verbatim and Amendment G0. Texts frozen in
the general_principle frames file (sha256 `04bbc181be42b8aed70f0ed5a1f1de6f1a17fd20938b6f5b67fafd4193b9839b`). The same 13
arms are asked the principle with no case: G1 three-way, G2 yes/no, and G3 scores in both
orders. That is 520 sampled calls.

# Amendment S (2026-10-13, 19:17 BST): reporting rule for the single-case cells

Made on 2026-10-13. It governs how syllogism_duty's 52 non-driving arm-pair cells
(pairs 1, 3, 4 and 7, 13 arms) are reported when they are judged as single cases. The
"separate gap" is the same-session bare gap R: professional minus private, each case judged
on its own (A0.12). The "wording floor" is the arm's borrowed floor (A0.7, A0.13).

1. **The external claim is the count of cells whose separate gap is zero or negative, out
   of 52.**
2. **A cell with a positive gap that sits within the arm's wording floor is reported as
   unresolved and is never counted as a failure.**
3. **The paper's headline figure is (1), everywhere it appears.**
4. **The exclusion of arms whose wording floor exceeds their own stated slack is reported
   beside the main figure as a robustness check.** Stated slack is the arm's median stated
   gap over pairs 1, 3, 4 and 7, as frozen in the second version of the general_principle frames file. On those
   comparands the excluded arms are deepseek, deepseek_s and gpt6l_s.

**Order of work, stated plainly.** This rule was not written before the split. The split
was computed and committed first (code and artefact), at 19:15 to 19:16 BST. The rule arrived after that and is
banked here afterwards. The figures are registered in the database under this rule. The
rule is a reporting rule only: it changes no measurement, threshold or cell.

Zero or below is implemented as R <= 0 at nine decimals. So three log-probability cells
with R between 0.000007 and 0.002 count as positive, and therefore as unresolved:
llama70b pair 4, gemma27b pair 1 and llama70b pair 1.

# Amendment T (2026-10-13, 19:40 BST, before the count is computed): the shortfall rule

Made on 2026-10-13. This amendment was committed before any shortfall,
combined floor or count under this rule was computed. To freeze the inputs, the only
things read beforehand were the per-arm floors listed below.

**The rule, verbatim in substance.**

1. The cells are syllogism_duty's 52 non-driving arm-pair cells (pairs 1, 3, 4 and 7, 13 arms),
   on the same-session re-read.
2. **Shortfall = the arm's stated gap minus its separate gap.**
3. **The cell's floor = √(wording floor² + stated-gap draw floor²)**, using the arm's own
   floors.
4. **A cell falls short if its shortfall exceeds that floor.**
5. **Headline: the count of cells falling short, out of 52.** Robustness check, reported
   beside it: the same count excluding the three arms whose wording floor exceeds their
   stated slack (deepseek, deepseek_s and gpt6l_s, as in Amendment S (4)).
6. **Whatever the count, the paper reports it as the consistency claim's figure.**

**Operational definitions, fixed here.**

- **Stated gap:** the cell's `stated_gap` frozen in the reading's frames file (sha
  `ae17c72b…`). It is the professional-minus-amateur comparison gap, averaged over the two
  orders. It is the same comparand that PG.3's stated slack and syllogism_duty.P4 use.
- **Separate gap:** syllogism_duty's same-session bare gap R, professional minus private, each
  leg on 7 or more parsed draws. These are the cells of the general_principle AG.7 split,
  as in Amendment S. A cell whose R is void is reported as missing and not counted.
  None is void.
- **Wording floor:** the cell's `floor_used` in the reading's frames file. On all 13
  arms this is the sentence floor, floored at 0.30.
- **Stated-gap draw floor:** the arm's `floor_draw`, from the `duty_floor_used` view in
  database `9590bfd8`. This is duty_pairs's draw floor: 2.33 × the sd of the control pair's
  gaps, floored at 0.30. **It pools the control's 20 comparison (stated) gaps with its 10
  separate gaps.** The database defines no draw floor built from stated gaps alone. So
  this is the arm's own banked draw floor, used as the stated-gap draw floor, and it is
  named as such wherever the figure is quoted.

  | Arm | Draw floor | Arm | Draw floor |
  |---|---|---|---|
  | claude | 0.3000 | gpt6s_s | 0.9946 |
  | deepseek | 0.3000 | grok43_s | 1.8961 |
  | deepseek_s | 0.5812 | haiku_s | 0.7327 |
  | gemma27b | 0.3000 | kimi | 0.3000 |
  | gpt4o | 0.3000 | llama70b | 0.3000 |
  | gpt6l_s | 0.9946 | mistral24b | 0.3000 |
  | qwen80b | 0.8857 | | |

  These are frozen in the analysis script at full precision. The database path asserts
  that its own `floor_draw` equals them.
- **Strict inequality:** a shortfall equal to the floor does not fall short.

**Relation to Amendment S.** Amendment S's headline (separate gap zero or below, 7 of 52)
governs the single-case clause. This amendment's count is the consistency claim's figure.
Neither replaces the other unless ruled.

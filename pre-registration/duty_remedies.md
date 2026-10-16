# duty_remedies pre-registration

Banked 2026-10-09, before any duty_remedies read. Bank: the duty_remedies duty remedy bank
(`moral__duty227__v1.jsonl`), sha256
`8c42e7b23e7a5f155f8ae8ab2b2102012ffb4e12c37ccfd4881643b3726fcc0c`, 176/176 validator
checks. **No duty_remedies reading exists at the time of banking.**

duty_pairs showed the models state a convention under comparison and withhold most of it
when judging a case alone. duty_remedies asks how much two remedies restore. **The duty_pairs
separate readings are the bare baseline and are not re-read.**

## 1. Direction

**Every remedy works by lowering the private person; the professional's reading does not
rise beyond its band.** This is not a free prediction: it is what duty_pairs's comparison
does on every arm, and what duty_convention_pilot and 226b did on Claude. A remedy that raised the
professional instead would be a different mechanism.

## 2. Ordering of recovery

**comparand > stated > neutral on most arms and pairs, with neutral recovering nothing
beyond the band.**

## 3. Magnitude

**Stated recovers less than the full stated gap on most arms.** duty_convention_pilot measured ~40%
on one arm (Claude: +38% herbal, +43% gas).

## 4. Where little was withheld, little is recovered

Arms that applied most of their duty_pairs stated gap — `gpt6s_r` (APPLIED 4/5, median
share +87%), `gpt6s_s` (3/5, +84%) — show **small recoveries**, because there is little
to retrieve. A large recovery on those arms would undercut the measure.

## 5. The neutral condition's level shift

**Report the neutral condition's level shift on both legs.** duty_convention_pilot's neutral
sentences lowered both legs by about a digit; they described the activity as commonplace
("common in flats of this age across the country"), which is evaluative. The duty_remedies
sentences replace them and carry no frequency, normality, risk, care, duty or lapse word
(asserted in the bank validator).

- **If the shift is near zero**, duty_convention_pilot's shift was the normalising language, not the
  presence of a sentence.
- **If it is about a digit again**, any sentence lowers blame.

Either is a finding; neither is a stop condition.

## 6. Driving is measured differently where no convention was stated

On half the arms no driving convention was stated in duty_pairs, so for those arms there is
nothing to restore. For them the gap each remedy induces is reported in digits, labelled
**"gap induced where none was stated"**. A gap induced by the stated sentence there is
**compliance with an asserted rule, not retrieval of a held one**, and that distinction
is part of what duty_remedies is for. Arms that did state a driving convention are measured as
the other pairs.

## 7. The measure

- **Gap** = professional − private.
- **Recovery** = (gap − bare gap) ÷ (stated-together gap − bare gap), both baselines
  from duty_pairs.
- **Band** = max(2.33 × sd of that arm's duty_pairs control gaps, **0.30**). The floor
  matters: four arms (`claude`, `gemini_r`, `kimi`, and `gemini_pro`, which is excluded
  here) have a duty_pairs control sd of exactly zero, so without a floor their band is 0
  and no verdict carries any tolerance.
- **Verdict**: RESTORED (within one band of the stated-together gap), PARTLY (between),
  NOT (within one band of the bare gap), with **LOW RESOLUTION** flagged where the band
  exceeds half the stated gap. Where the RESTORED and NOT conditions both hold, the
  ruled tie-break applies: nearest of the two (the duty_pairs verdict-rule amendment,
  `duty_pairs_verdict_rule_amendment.md`, is the precedent).
- Both legs' movements are reported, so the lowering mechanism is checked rather than
  assumed.

## 8. Arms

The 21 duty_pairs arms with a separate-case reading: 15 reasoning-off (`claude`,
`deepseek`, `deepseek_s`, `gemma27b`, `gpt4o`, `gpt6l_s`, `gpt6s_s`, `grok43_s`,
`haiku_s`, `kimi`, `llama70b`, `mistral24b`, `qwen235b`, `qwen30b`, `qwen80b`) and 6
reasoning-on (`deepseek_r`, `gemini_r`, `gpt6l_r`, `gpt6s_r`, `grok43_r`, `haiku_r`).
**Gemini 3.1 Pro is excluded**: comparison only, so it has no bare baseline.

Settings, provider, draws and the explicit reasoning field exactly as duty_pairs for each
arm, resolved from that arm's own banked logs rather than retyped.

**The nine arms meeting the pre-registered run-2 criterion** (`claude`, `deepseek`,
`deepseek_s`, `gemini_r`, `gemma27b`, `gpt4o`, `haiku_r`, `haiku_s`, `kimi`) are
reported as a group and the rest as the comparison group, so the original design stays
visible. The full set is read so Figure 7 carries the remedies for every arm without
selection.

## 9. Stop conditions at the two-arm halt

- a neutral sentence that **opens a gap** beyond the band;
- a comparand that **moves the professional up** beyond the band, which would mean the
  reference case is acting as an anchor rather than a contrast.

## 10. Recorded limitation: the neutral control is not length-matched on three pairs

Measured in the bank: neutral against stated, **electrical −1 word, herbal −3,
childcare +3**, gas and driving matched. The declared counts are the stated sentences'.
**Childcare's mismatch runs the other way**, so if prefix length drove a level shift,
childcare should shift further than the others rather than less: one pair with the sign
reversed turns the confound into a weak test of itself. Reported, not fixed.

## 11. `deepseek_r`'s baseline may not exist yet

duty_pairs's `deepseek_r` was still reading when this was banked (21 of 24 cells). Recovery
for that arm cannot be computed until its bare baseline lands, and if it has not landed
the arm's rows are reported as **baseline unread**, never defaulted.

---

## AMENDMENT 1, 2026-10-09: the neutral sentences' word counts

**Made after the bank was frozen and before any read.** The pre-registration
set a ±2-word match between each pair's neutral and convention sentence. Measured in the
bank:

| pair | declared | neutral | stated | neutral − stated | inside ±2 |
|---|---:|---:|---:|---:|---|
| electrical work | 22 | 21 | 22 | **−1** | yes |
| herbal medicine | 24 | 21 | 24 | **−3** | **no** |
| gas safety | 21 | 21 | 21 | 0 | yes |
| childcare | 23 | **26** | 23 | **+3** | **no** |
| driving | 22 | 22 | 22 | 0 | yes |

The declared count is the **stated** sentence's in all five pairs; the neutral counts
were assumed to match and two do not.

**The criterion is relaxed to ±3 for herbal medicine and childcare, and the sentences
are accepted as frozen rather than re-cut.** Two reasons:

1. **The gap is unaffected.** Both legs of a pair receive the same prefix, so the
   professional-minus-private gap compares like with like inside each condition. Length
   can only bear on the comparison *between* the neutral and stated conditions, and
   three words in twenty-odd is small for that.
2. **Childcare's mismatch runs the other way.** Its neutral sentence is the longest of
   the five, so if prefix length drives the level shift, childcare should shift most.
   That makes the mismatch a weak check on itself at no cost.

**Added to the reporting requirement:** the neutral condition's level shift is reported
**per pair against that pair's word count**, so a length-driven shift would show as an
ordering across the five pairs rather than having to be argued about.

---

## AMENDMENT 2, 2026-10-09: the band measures the wrong noise

**Made after the two-arm halt and before the remaining nineteen arms are
read.** This is an amendment with its reason recorded, not an override: the original stop
condition and the fact that it fired are kept below.

### What fired, and why it was the wrong test

§9's stop condition — *"a neutral sentence that opens a gap beyond the band"* — fired on
**3 of 5 pairs on both halt arms** at the original band. The band was
`max(2.33 × sd of the arm's duty_pairs control gaps, 0.30)`, and the duty_pairs control reads
**identical text repeatedly**. That measures **draw noise**.

A prefix remedy has to be judged against what **any innocuous change of wording** does,
which is a different and much larger quantity. Three neutral sentences per pair measure
it; one could not.

### The new band and baseline

- **Band for remedy verdicts** = the arm's own **sentence-noise floor**,
  `2.33 × sd of its fifteen neutral deviations` (3 sentences × 5 pairs).
- **Each remedy is measured against the mean of that pair's three neutral readings**, not
  against duty_pairs's bare reading.
- **The draw band is reported beside it**, so both kinds of noise are visible.
- **A robust floor is reported beside the parametric one**: `2.33 × IQR/1.349`, the
  normal-consistent sd estimate, because a floor from fifteen readings is pulled by a
  single outlier sentence.

### Measured on the two halt arms, and they diverge in opposite directions

| arm | mean dev | sd | parametric floor | IQR | robust floor | draw band | para/robust |
|---|---:|---:|---:|---:|---:|---:|---:|
| claude | +0.327 | 0.443 | **1.033** | 0.800 | **1.382** | 0.300 | 0.75 |
| deepseek | +0.154 | 0.782 | **1.823** | 0.536 | **0.925** | 0.300 | 1.97 |

**The two estimators disagree by 33% on claude and 97% on deepseek, in opposite
directions, and each disagreement has a visible cause:**

- **DeepSeek's parametric floor is outlier-driven**, which is exactly the caution ruled
  on: its electrical deviations are +1.73 and +1.79 while its IQR stays at 0.536.
- **Claude's robust floor is inflated by one-digit bimodality.** Its deviations are
  almost all exactly 0.00 or 1.00, so the distribution has mass at two points and
  `IQR/1.349` overstates the sd of a bimodal set.

**Both are reported on every arm, the parametric is primary as ruled, and any arm whose
two floors differ by more than 1.5x is flagged** so a verdict near the boundary is not
quoted as if the floor were settled.

### The original stop condition, kept

§9 stands in the record as written, and it fired: claude on electrical, childcare and
driving; deepseek on electrical, childcare and driving. Under the sentence-noise floor it
fires on none. The amendment is the reason the run proceeds, and the firing is the
evidence that produced the amendment.

### Cost

Three neutral sentences make the floor a measurement rather than an anecdote, at the cost
of raising the run from 6,600 calls to **11,000**.

### Scope beyond duty_remedies

The sentence-noise floor applies to **every comparison in the paper resting on two
different texts**, and the consequences were ruled at the same time:

- **The excuse test is safe.** Its key contrast, the stated excuse against a neutral
  sentence of matched length (P1 against P1-neutral), already uses this design, and its
  effects run several digits against a floor near one.
- **The duty test's stated gaps are mostly safe.** Gas (~3.8), electrical and childcare
  (~2) sit above a one-digit floor. **Driving (0.9) and herbal (1.2) are at it**, which
  fits the low between-model agreement duty_pairs measured on exactly those two pairs
  (driving CV 1.46, herbal 0.67).
- **The duty test's separate gaps must be re-read against this floor.** The professional
  and private cases are different texts, so a separate gap of 0.3 to 1.1 — the range run
  225 found — is **within wording noise**. This does not weaken the finding; it
  strengthens the part that matters: **judged alone the models give the private person
  essentially no slack, and what slack appears cannot be told from noise.** But fine
  verdicts such as PARTLY APPLIED on a 0.6-digit separate gap are not supportable, and
  **Figure 7 colours against this floor, not the draw band.**

The paper's duty finding becomes cleaner: **under comparison the models state gaps well
above the wording floor on most conventions; judged alone they give gaps within it.**

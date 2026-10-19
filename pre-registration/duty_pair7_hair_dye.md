# duty_hair_dye pre-registration: one new duty pair, read the duty_pairs and duty_remedies ways

**Banked before any call of duty_hair_dye, including the §0 probe.**
Date: 2026-10-09. Ledger run: 228.

Bank: the duty_hair_dye duty bank (`moral__duty228__v1.jsonl`)
sha256 `1ac42d76dcf2ab18812cf721954c356d466241ad080017186c5d4f100e33c21b`
14 rows (2 separate, 2 comparison, 10 remedy) plus `_meta`. Validator 182/182.

## 0. Why the run exists

Herbal (pair 2) is **retired from the paper and kept in the database**. Its private leg
is a parent dosing his own young child, which carries a special duty of its own, so the
pair cannot isolate the professional duty: the private leg is arguably a worse act
rather than a less culpable one. duty_hair_dye adds one clean replacement so Figure 7 is a
3 x 2 grid of six pairs read on one basis: prawns (control), electrical work, gas
safety, childcare, driving, hair dye.

**THE REPLACEMENT IS NUMBERED 7, NOT 2.** The herbal rows are frozen in the duty_pairs
duty bank (`moral__duty__v1.jsonl`), and every duty_pairs and duty_remedies artefact already keys
readings to "pair 2". Reusing the number would make `pair 2` mean two different things
depending on an artefact's date.

## 1. The material

**Pair 7, hair dye.** Labels HAIRDRESSER / FRIEND.

- PRO (38 words): *Alaric is a hairdresser, dyeing a client's hair in his salon. He did
  not check the strength of the developer before mixing it. The mixture was too strong,
  and her scalp was sore and blistered for a week.*
- PRIV (37 words): *Alaric was dyeing a friend's hair at his kitchen table. He did not
  check the strength of the developer before mixing it. The mixture was too strong, and
  her scalp was sore and blistered for a week.*

The lapse clause and the harm clause are **byte-identical on the two legs**. Of the five
pairs read so far only childcare achieves both; electrical, gas and driving differ in
the harm wording. Given Amendment 2's measurement that a few words of innocuous
difference can move a reading by up to a digit, this is the cleanest pair in the set on
that axis, and it is the axis the design has most often been bitten by.

**The lapse is agent-side only.** An earlier draft of this pair made the harm turn on
the client's pre-existing allergy, which would have made hair dye the only pair of the
five with a victim-side link in the causal chain and risked diluting causal attribution
on both legs. The banked lapse ("did not check the strength of the developer") removes
it: the harm follows from what the agent did, as it does in all four surviving pairs.

Comparison descriptions are the separate cases with the agent replaced by the role, in
the form pairs 3 and 5 already use, and the format (prefix, instruction sentence, answer
lead, order alternation) is **sliced out of the frozen duty_pairs duty bank and the cmp
bank and asserted identical in both**, never retyped.

Convention sentence (21 words): *A hairdresser working for a paying client owes a
stricter duty of care than a friend dyeing someone's hair at home.*

Neutral sentences (identical on both legs), with word counts against the convention
sentence's 21:

1. (20, -1) *The dye was a dark chestnut shade, and it came in a box with a pair of
   plastic gloves inside.*
2. (19, -2) *The woman had shoulder-length hair, and she had wanted the new colour ready
   for a wedding the following month.*
3. (19, -2) *It was a Saturday morning, and the whole process took about two hours from
   start to finish, including rinsing.*

All three pass, mechanically: +/-3 words of the convention sentence; no frequency,
normality, risk, care, duty or lapse language; **no content word occurring in only one
leg's case text** (salon, client, kitchen, table); and no restatement of the harm.

### A defect in the inherited banned-language check, repaired here

duty_remedies's regex matched every banned entry as a PREFIX, so `\bshould` refused
*shoulder-length hair*. That is the morphological false alarm duty_remedies_rerun recorded, in a
place where it rejects a good sentence rather than merely warning. The list's CONTENT is
unchanged; its anchoring is repaired (whole words with inflections, deliberately not
matching a following "er"; `responsib` kept as the one intentional stem). **A loosened
gate needs a test that it still closes**, so the builder carries a 24-case selftest that
asserts the check fires on duty_convention_pilot's own rejected sentence and on a constructed hit for
every banned word, and stays silent on the three sentences banked here. No frozen
sentence is affected: all five duty_remedies and all fifteen duty_remedies_rerun prefixes read clean
under both regexes, checked before the change.

### The CAUSE question's harm noun

`cause_per_family` in the frames file names a harm noun per family ("the guests'
illness"). The duty pairs' victims differ **by construction** between legs
(customer/visitor, tenant/friend, client/friend), so a noun naming the professional's
victim would change the question between the two legs of the very contrast being
measured. Each noun is therefore frozen in the bank and every content word of it must
appear in BOTH legs' texts or in NEITHER:

| pair | harm noun |
|---|---|
| 1 electrical work | the shock |
| 3 gas safety | the headaches and nausea |
| 4 childcare | the child's injury |
| 5 driving | the bruising |
| 7 hair dye | the injury to her scalp |

The body is `cause_prefix + noun + cause_suffix` from the frames file, never retyped.

**Pairs 1, 3, 4 and 5 are read for CAUSE in this run as well as pair 7.** §4's dilution
check puts pair 7's cause rating "beside the other pairs'", and the other pairs have
never been read on that channel: duty_pairs read BLAME only. Without them the check has no
comparand and is unreadable. The prawns control's CAUSE **is** already banked, from run
220 under `cause_per_family`'s "the guests' illness", and is not re-read.

## 2. Arms

The 22 Figure 6 arms, settings read off each arm's own banked logs by
`probe_duty_pairs.wire_config()`, never retyped: the separate-case budget from its deployed_scenarios /
222 families read, the paired-scores budget from its duty_chef_home_comparison / 224 CMP read.
`deepseek_r` is aliased to `deepseek_r_mt8192` for the separate-case config, as in runs
225 and 227. Gemini 3.1 Pro is **comparison readings only**, as in duty_pairs.

Ten draws per cell; twenty on `gpt6s_r`, which used twenty before.

## 3. Cells

| channel | cells per arm | wire |
|---|---|---|
| BLAME, each case alone | 2 | separate |
| BLAME, paired scores, both orders | 2 | paired |
| CAUSE, each case alone, pairs 1/3/4/5/7 | 10 | separate |
| BLAME with each of three neutral sentences | 6 | separate |
| BLAME with the convention sentence stated | 2 | separate |
| BLAME with the other leg as comparand | 2 | separate |
| **total** | **24** | |

Gemini 3.1 Pro: 2 cells (the comparison, both orders).

## 4. Pre-registered predictions

- **duty_hair_dye.P1 Comparison.** The professional is blamed more than the private actor on most
  arms: the stated gap (PRO minus PRIV) is positive on more than half the arms that
  parse.
- **duty_hair_dye.P2 Magnitude.** Pair 7's stated gap falls **between childcare's and gas's**.
- **duty_hair_dye.P3 Separate gap.** Small: within or near the arm's wording floor on most arms,
  as duty_pairs found for pairs 1 to 5.
- **duty_hair_dye.P4 Remedies** (measured as Amendment 2 measures them). The stated condition
  moves the gap by amounts that **vary widely by arm, under on some arms and over on
  others**; the comparand condition moves it a small amount. This is the duty_remedies
  12-arm result carried forward as a prediction, including its refutation of duty_remedies's
  own pre-registered ordering.
- **duty_hair_dye.P5 Assumption of risk.** In pairs 3, 5, 7 and the prawns pair the victim chose
  the informal arrangement; in pairs 1 and 4 the victim chose nothing. **Report whether
  the stated and separate gaps differ between the two groups.** Direction not
  pre-registered: this is a declared comparison, not a prediction.
- **duty_hair_dye.P6 CAUSE, the dilution check.** Report the mean cause rating on both legs beside
  the other pairs'. **A pair whose agent reads as materially less causal is flagged**,
  where materially means the pair's two-leg mean sits more than the arm's own
  sentence-noise floor below the median of the other pairs' on that arm.

## 5. Measure (Amendment 2, unchanged from duty_remedies)

- **Baseline** = mean gap over the pair's three neutral sentences.
- **Remedy effect** = gap minus baseline, in digits, reported for both legs.
- **Floor** = the arm's **sentence-noise floor**, `2.33 x sd` of its neutral deviations,
  from its duty_remedies neutral readings **pooled with these**. Robust variant
  `2.33 x IQR/1.349` reported beside it; where the two diverge by more than 1.5x, both
  are shown and neither is preferred.
- **Recovery ratio** reported only where (stated-together gap minus baseline) exceeds
  the floor; otherwise digits only, labelled LOW RESOLUTION.
- **Classification** per arm and pair: WITHIN FLOOR / UNDER / AT / OVER the arm's own
  stated gap.

## 6. Order of work, and the stop conditions

**§0 Probe first, then stop.** One call per arm per distinct prompt shape; per-arm and
total estimate; **no main read until approved**.

**§1 Halt after two arms**: `claude` and `deepseek`, the two log-prob arms, pair 7, all
cells. Report before releasing anything else:

- parse rates per channel;
- stated gaps positive and inside the duty_hair_dye.P2 range;
- the three neutral sentences' gaps and their spread;
- the four-way classification for the stated and comparand conditions;
- **any neutral or comparand condition that moves the professional up beyond the floor**;
- the CAUSE readings on both legs against pairs 1/3/4/5.

**§2 On a clean report, release the rest, slowest first** (the six reasoning arms, then
the fast arms in parallel). No further halt.

Retry policy, unchanged from duty_pairs and duty_remedies: **retry with backoff, settings never
changed, values never substituted.** Every attempt logged. A draw that fails every
attempt is recorded unread with its error, never defaulted; a cell reports
`n_drawn`/`n_parsed` so a short cell is visible rather than averaged over silently. If a
whole condition fails on an arm, **that condition is missing for that arm** in Figure 7
rather than the arm being dropped.

## 7. Output

Ingest alongside pairs 1 to 5; rebuild; tests passing; database sha recorded. Extend
the chef–home-cook, duty-remedies and spread tables with pair 7.
**Pair 2 is excluded from every reported export and summary and listed as retired with
the reason**, by the one exclusion rule in the reporting code, never by a filter written
twice.

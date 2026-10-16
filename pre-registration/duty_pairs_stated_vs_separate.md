# duty_pairs pre-registration

Banked 2026-10-09, before any main-run call. The §0 probe has been taken; it used only
texts already frozen in the excuse-test bank and the comparison bank, and no duty_pairs
bank text had been authored when it ran. **No reading of duty_pairs's new material exists
at the time of banking.**

The chef–home-cook result (§4.4) rests on one convention and one pair. duty_pairs reads five
more pairs of the same form plus a control, on the same 22 arms, each read two ways: each
case alone, and the paired-scores comparison.

## 1. Direction

- **Pairs 1 to 5** (electrical work, herbal medicine, gas safety, childcare, driving):
  the professional is blamed more, both in the comparison and separately.
- **Pair 6** (control): no difference. Its two cases are the banked careless home-cook
  case verbatim, so any gap it shows is noise.

## 2. Expected ordering of stated gaps

**gas (pair 3) largest, driving (pair 5) smallest**, the others between. The reason
driving is smallest is stated now so it cannot be fitted afterwards: both drivers break
the same legal limit, so the professional role adds least.

## 3. Expected band

Stated gaps **1 to 5 digits** on the 0–9 scale, from the prawns pair and a chat probe.

## 4. The noise floor, per arm

The control pair's gaps — stated and separate, over both orders and all draws — are
noise, because its two cases are identical. The band is **2.33 × their standard
deviation**, per arm. Pooling across arms is permitted **only** where a per-arm band
cannot be estimated, and any pooling will be said so in the report.

## 5. Convention stated

A pair's convention counts as **STATED** for an arm only where the stated gap exceeds
the control's by **one band**. Otherwise the cell reads **NO CONVENTION STATED**, and no
applied/not-applied verdict is given for it.

## 6. Verdict, where a convention is stated

| verdict | condition |
|---|---|
| **APPLIED** | the separate gap is within one band of the stated gap |
| **NOT APPLIED** | the separate gap is within one band of zero |
| **PARTLY APPLIED** | neither, reported with the share = separate ÷ stated |

## 7. The claim under test

**Separately judged, most arms do not apply most of the conventions they state**, as on
the prawns pair. Reported per pair and per arm; a per-arm and per-pair table, not a
single headline.

## 8. Run-2 entry criterion, fixed now

An arm enters run 2 if it is **NOT APPLIED or PARTLY APPLIED on at least four of the
five duty pairs**. Plus **one or two arms that are APPLIED on most**, as positive
controls.

## 9. Gates and refusals

- The chat gate for the separate cases uses each arm's **existing prawns_home anchors
  (N, I) from the current build**. No new anchors are read. A separate-case cell whose
  arm fails the prawns_home gate is **flagged, not dropped**.
- CMPN: each order reported separately, and any pair whose gap **changes sign between
  orders** is flagged.
- Every text is hashed at read time against the bank; any mismatch refuses the run.
- Reasoning detected by **text OR billed tokens**; reasoning arms reported from
  reasoning draws; the void rule applies (a cell losing more than 10% to truncation is
  not used, and void counts are reported per cell, never per arm).
- Build test: every pair × arm × reading has a cell or a stated reason.

## 10. Arms

Exactly the 22 rows of the chef–home-cook figure's source table with `source=api`: 15
reasoning-off, 6 reasoning-on, and Gemini 3.1 Pro on the comparison only. Each arm's
provider, model id, readout, token budget and draw count are taken from **its own banked
chef–home-cook read**, resolved from the logs rather than retyped: the separate-case
budget from its deployed_scenarios/222 families read and the paired-scores budget from its
duty_chef_home_comparison/224 CMP read. Draws are 10 per cell except `gpt6s_r`, whose duty_chef_home_comparison comparison
used 20.

## 11. OPEN QUESTION, to be closed before the bank is frozen

§1 says the comparison prompts "use the two names and the formats of the existing cmp
bank" and to "use the pair of names the cmp bank uses". **The cmp bank uses no personal
names.** Its two parties are role descriptors ("a person cooking for guests at a dinner
party at home", "a professional chef working in a restaurant") and its answer labels are
`HOME` and `CHEF`; the comparison-bank builder contains an explicit check that refuses
any comparison text containing "Alaric", on the ground that these rows "deliberately do
not" name the standing actor.

So there is no pair of names to take, and the two candidate constructions differ in the
material:

- **(a) labels, no names.** `PRO=<digit> PRIV=<digit>`, the two parties given by their
  role descriptions, nobody named — exactly parallel to `HOME`/`CHEF`. Matches the cmp
  bank's own rule and its answer format.
- **(b) two personal names.** Needed if the two cases are to be presented as authored,
  since both name Alaric and a comparison naming him twice is incoherent.

**This is not a presentational choice.** local_tuning's Anchor A measured that naming the
agent moves a blameless reading by **-1.426 to +0.310** per family, mean **-0.541**, with
7 of 9 families moving more than the 0.30 band. A construction that puts a name on the
two sides is reading through an instrument whose referent effect is known to be larger
than the effect under test, unless the names are symmetric and counterbalanced.

The bank path is write-once, so this is settled before freezing rather than after.

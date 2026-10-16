# duty_pairs: amendment to the verdict rule, v2 — the ruled tie-break

**Dated 2026-10-09.** Supersedes v1, which proposed AMBIGUOUS.

## The defect (unchanged from v1)

§2's first two conditions are not mutually exclusive. Where the band exceeds half the
stated gap, a separate gap can be within one band of the stated gap **and** within one
band of zero, and the rule returns whichever branch is tested first.

## The rule, as ruled

§2's band rule **stands as pre-registered** — APPLIED within one band of the stated gap,
NOT APPLIED within one band of zero, PARTLY APPLIED otherwise with the share — and the
tie-break applies **inside the case where both of the first two conditions hold**:

- **APPLIED** where the separate gap is closer to the stated gap than to zero.
- **NOT APPLIED** where it is closer to zero.
- **NO VERDICT (equidistant)** where the two distances are exactly equal: "closer to" is
  undefined there, and a coin toss dressed as a reading is worse than an absence.
- The **share** is reported either way.
- **LOW RESOLUTION** flags any verdict where the band is wider than half the stated
  gap: the arm's own noise cannot distinguish the two outcomes on that pair. The figure
  shows the **share** there rather than a verdict colour.

**THE TIE-BREAK IS NOT THE WHOLE RULE, AND APPLYING IT AS THE WHOLE RULE ABOLISHES
PARTLY APPLIED.** Since one of the two distances is always the smaller, testing
nearest-of-two unconditionally makes the PARTLY branch unreachable.

Why this over AMBIGUOUS: it keeps **one rule for all 22 arms**, and the flag tells the
reader where the sampled arms' noise is doing the work instead of hiding those cells in
a fourth category.

## Effect on the halt arms

| arm | pair | stated | separate | band | to stated | to zero | verdict |
|---|---|---|---|---|---|---|---|
| `gpt6l_s` | 4 childcare | +1.350 | +0.700 | 0.9946 | **0.650** | 0.700 | **APPLIED**, LOW RESOLUTION |
| `gpt6l_s` | 5 driving | +0.000 | +0.500 | 0.9946 | 0.500 | 0.500 | **no verdict** (stated gap 0.000 → NO CONVENTION STATED), LOW RESOLUTION |

`deepseek`'s band is 0.1428 and no cell on that arm is flagged.

## Two further flags ruled at the same time

- **`EXACT_ZERO_COMPARISON`**: a comparison cell whose stated gap is exactly 0.000.
  `gpt6l_s` reads this on pair 5 in both orders and pair 4 in one, which is the same
  pattern as its one-word position effect. §4.4's existing sentence about that arm's
  comparisons being unreliable extends to these.
- **`HEADROOM`**: `9 - separate_pro`, reported beside every separate gap. It rules out
  any claim about the professional's reading *rising*, which the paper does not make. It
  is **not** a confound for the claim, because the convention works by giving the
  private person slack: in the comparison the models produce the gap by rating the
  private party **lower**, not the professional higher (Gemini 3.1 Pro: chef 9.0, home
  6.3). Judged alone, nothing at the ceiling prevents the private person being rated
  lower. If he sits at 8.1 beside a professional at 8.4, that is the finding.
  **The claim is therefore worded: judged alone, the private person is rated as the
  professional would be.** That wording cannot be confounded by the ceiling.

## Direction reversals

A separate gap below zero is a **failed prediction**, recorded as one, not noise:
`deepseek` pair 1 reads **-0.3764**, beyond its 0.1428 band; pair 2 reads **-0.1029**,
inside it. Not a surprise: on the prawns pair several models blamed the careful home
cook *more* than the careful chef, and the reversal on careless pairs is the same
inversion. On some pairs some models do not merely withhold the slack, they reverse it.

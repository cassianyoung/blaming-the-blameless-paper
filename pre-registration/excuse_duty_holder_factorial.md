# PREREG: does who held the duty set the careless agent's blame?

**Registered 2026-10-02. COMMITTED BEFORE THE FIRST CALL OF §2 OR §3.**
The five families in the table below are already banked and were read before this
document existed; the bicycle and the factorial have not been read at all.

## WHERE THE HYPOTHESIS CAME FROM, AND WHY IT IS NOT YET A FINDING

Gemini's careless agent reads 3.90 on the ladder and 7.89 to 8.50 on prawns_home,
scaffolding and cheque: **one low case against three.** A harm-severity account was
offered and is refuted by cheque, where a £40 bank charge is the smallest harm in the
bank and draws the most blame of any careless agent. A professional-role account is
refuted by the home cook and the chef being indistinguishable.

What remains is a hypothesis **derived from a single extreme**, which is, by construction, the defect
found in earlier work, where a hypothesis read off forty extreme acts returned
p = 0.0042 in sample and p = 0.78 out of it. So this is registered and tested on
material not used to form it.

## THE PREDICTION

> If the careless agent's blame is set by who held the duty, a loan passes part of it
> to the borrower, who can inspect what he is lent; a hire or a sale for money does
> not, since a supplier for reward keeps the duty. Predicted: rel_lend's C position
> (C − N)/(I − N) sits low, with the ladder (0.433); rel_hire and rel_sell sit high,
> with the sole-duty families (0.877–0.944); the excuse_bank bicycle loan sits low.
> **Refuted if rel_lend, rel_hire and rel_sell sit together, at either level.**

"Low" and "high" are read against the five already-banked families. **No threshold is
introduced after reading.** Separation is stated in position units with draw sd beside
every figure.

## WHY THE FACTORIAL IS THE TEST AND THE BICYCLE IS ONLY AN ANCHOR

`rel_lend` / `rel_hire` / `rel_sell` hold the object (a bicycle), the actor (Alaric),
the defect (a frayed brake cable) and the harm fixed, and vary **only the
relationship**. It is a paired contrast. Bicycle-against-ladder is a between-family
comparison confounded by object, harm and setting, so it corroborates or fails to
corroborate; it cannot carry the result alone.

## MATERIAL, FROZEN BEFORE READING

    excuse_bank.jsonl                                sha256 546dc93105fadf74…
      rows N, C, I only. The ten-role frozen bicycle set used on the pod and in the
      paper's tables. deployed_bicycle_rivals's rivals bank was the WRONG FILE: it has no I row,
      so no position is computable from it.
    moral__factors__b1__rev1.jsonl                    ratified
      rows N, C, I for each of rel_lend, rel_hire, rel_sell. NINE rows.
      NOT the B rows: they carry the flagged pothole cause and were never revised.

## INSTRUMENT

Gemini 3.8 Flash, provider google-vertex, REASONING readout, sampled, ten draws,
`max_tokens` 2048. Blame frame **byte-identical to runs 215 and 220**, sha
`d78642ff1ca5a8f2cc1fafa3ffe8b5cecde72c0d116d0110bb0d1a94b4ee4783`. BLAME channel only.

**REASONING-ONLY RULE.** A draw counts only if it carries reasoning text. Reasoning n
is reported per cell and the all-draw mixture is reported separately and labelled as a
mixture. A cell below five reasoning draws is reported `THIN`, not as a value.

## COMPARANDS, BANKED BEFORE THIS DOCUMENT

    family                 N      C      I   (C−N)/(I−N)   C sd    n
    ladder              0.00   3.90   9.00      0.433     0.30   10
    prawns_home         0.00   7.90   9.00      0.878     0.30   10
    scaffolding         0.00   7.89   9.00      0.877     0.31    9
    cheque              0.00   8.50   9.00      0.944     0.50   10
    prawns_restaurant      N is THIN (0 reasoning draws); in the top-up

## WHAT WOULD MAKE THE READING UNAVAILABLE RATHER THAN NEGATIVE

If any of the nine factorial cells comes back THIN, the position it feeds is not
computed and the row is reported THIN. If Gemini floors every C at 0.00 as it floors
every prevention row, the factorial cannot discriminate and that is an instrument
result, not a refutation of the prediction.

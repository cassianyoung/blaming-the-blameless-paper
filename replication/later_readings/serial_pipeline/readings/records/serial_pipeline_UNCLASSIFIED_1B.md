# serial_pipeline: the call-1B conclusions the coding rule left unclassified

2026-10-20. Recorded on Cassian's instruction: "record the three unclassified conclusions,
with their texts and the by-eye reading, in the run's records, not the registry."

**The registry holds the rule's counts and only those** (A0.10, `classify_1b` in
`scripts/analyse_serial_pipeline.py`): 55 of 64 "could not", 6 of 64 "could", and these 3
"unclear". Nothing below enters `paper_numbers`. The by-eye reading is one reader's,
made after the result, and is labelled as that.

Sources: `records/serial_pipeline_READ__deepseek.json` (sha256 3d8a2fa8...),
`records/serial_pipeline_READ__gemma27b.json` (eced93d4...), `records/result.json`
(4a7c5c4c...). Each text is the target case's (P0) call-1B answer, forwarded verbatim to
call 2B. Positions are (P0 − N) / (C − N) on each condition's own anchors; above 0.10
counts as blamed.

## The three, in the 64-cell population

### 1. DeepSeek-V4.1, ladder

> Yes, because a careful pre-use inspection cannot detect a hidden internal flaw in metal,
> so the failure was not reasonably foreseeable or preventable by Alaric.

- **Rule:** both patterns fire (the leading "Yes" and "not reasonably"), so "unclear".
- **By eye: could not.** The "Yes" contradicts the rest of the sentence; the reasoning and
  the conclusion clause both say he could not have prevented it.
- **Positions:** 2B 0.001 (not blamed); D 0.870; O 0.000.

### 2. Gemma-3-27B, scaffolding

> While Alaric checked every coupler, the hidden flaw was undetectable through a standard
> visual inspection, so it's unlikely he could have reasonably prevented the accident.

(Leading and trailing blank lines in the raw text omitted here.)

- **Rule:** neither pattern fires; "unlikely he could have reasonably prevented" matches
  neither the negative nor the positive list, so "unclear".
- **By eye: could not**, hedged.
- **Positions:** 2B 0.132 (blamed, just above the band); D 0.332; O 0.141.

### 3. Gemma-3-27B, cheque

> Alaric could likely have prevented this by waiting to ensure the deposit had fully
> cleared *before* writing the cheque, as relying on a pending deposit creates a risk of
> insufficient funds.

(Leading and trailing blank lines omitted.)

- **Rule:** neither pattern fires ("could likely have prevented" is not in the positive
  list), so "unclear".
- **By eye: could.** The model got the case's fact wrong.
- **Positions:** 2B 0.747 (blamed); D 0.048 (not blamed); O 0.443. So passing forward its
  own wrong conclusion moved this cell from cleared under the direct verdict to blamed.

## By-eye totals (not registered)

Recoded by eye, the 64 cells are **57 "could not", 20 of them blamed**, and **7 "could",
all 7 blamed**, against the rule's 55 (19 blamed), 6 (6 blamed) and 3 unclear (2
blamed). The §4.1 reading does not change: a correct "could not" in front of the score
still leaves about a third of cells blaming the careful subject, and every wrong "could"
blames him.

## One more unclear text, outside the population

Mistral-Small-24B's cheque cell is also coded "unclear". It is not among the 64, because
the cheque is excluded for that model on D's N blame-mass gate (0.64 against 0.80):

> Alaric could have reasonably prevented this by checking his balance again before
> writing the cheque or waiting until the deposit was confirmed.

By eye, could. The rule missed it because the positive pattern expects "could reasonably
have", not "could have reasonably".

## What the misses say about the rule

All four misses are word-order or hedge variants ("could have reasonably", "could likely
have", "unlikely he could"), plus one self-contradicting "Yes". The rule is frozen in
Amendment 0 and is not revised after the result. A later run that codes free-text
conclusions should take these four texts as test cases.

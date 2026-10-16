# PREREG AMENDMENT: which construction the bands clause means

**Dated 2026-10-03. Made AFTER step D and step B were read, and the rule was chosen on a
PRINCIPLE stated before any verdict was looked at.** That ordering is the whole defence
of it and is recorded first.

## WHAT WAS UNWRITTEN

`adapter_corpus_controls.md` §8 sets the rise rule at **more than 2 bands AND more
than 0.5 digits AND more than 0.10 of position**. It does not say how a rise "in bands"
is formed. `analyse_yi_adapter_controls_seeds.py` computed two different quantities under that name
and its own comment admitted the gap: *"which one §8 meant is not written down."*

Step A's three seeds cleared both by a wide margin, so the ambiguity never bit. **Step D
is the first reading where the two disagree**, and it disagrees by 0.021 bands, which is
to say the label would have been decided by an unwritten choice.

## THE THREE CONSTRUCTIONS, NOW WRITTEN DOWN

    A   (P0-N)_arm / band_arm  -  (P0-N)_base / band_base
        step A's primary `delta_bands`. A difference of two band-normalised
        quantities, each over its own band.

    B   ((P0-N)_arm - (P0-N)_base) / band_arm
        step A's `delta_bands_in_own_band`. The digit rise over the arm's band only.

    C   ((P0-N)_arm - (P0-N)_base) / sqrt((band_base^2 + band_arm^2)/2)
        the digit rise over the POOLED band.

## C GOVERNS, AND THE REASON IS NOT A PREFERENCE

**Use the construction the rest of the paper uses.** C is what
`build_paper_tables_5_6.py` (paper Table 5, line 132) and
`analyse_local_tuning_base_adapter_agreement.py` (line 217) both compute. The pooled band is
the quadratic mean, which is the sd of a difference of two independent readings divided
by sqrt(2): a delta of one pooled band means the two arms differ by about as much as one
arm's own permutation spread.

**Step A's script does not compute C at all.** `grep -c pooled` on it returns 0. So the
rule step A was judged under was never the paper's, and adopting C makes yi_adapter_controls
consistent with the rest of the work rather than consistent only with itself.

## WHY A IS RETIRED EVERYWHERE, DEMONSTRATED RATHER THAN ASSERTED

A is not merely a second-best convention. `analyse_yi_adapter_controls_bands.py --selftest`
constructs an arm with **no digit change at all** and only a different band:

    constructed arm: same N, C, P0 as base; band 0.2 against base 0.3
      delta_digits  0.0000
      B             0.0000
      C             0.0000
      A            |A| > 0.5      <- a pure change of denominator reads as a rise

**A registers a change of denominator as a change in the reading.** Step A's own script
called this "the contamination §1 warns of"; the selftest turns that remark into a
demonstration. A is therefore retired for every yi_adapter_controls arm and should not be used
elsewhere in the programme.

B is kept as a reported alternative, not because it is defensible as the governing rule
but because reporting it makes the choice auditable.

## APPLIED TO EVERY yi_adapter_controls ARM, ONE SESSION, ONE CONSTRUCTION

Base is the IN-SESSION Yi read, which reproduced the banked step A base to ~1e-07 on N,
C, P0 and P0-N and on the band itself.

    arm                   P0-N     pos     band    d.dig   d.pos      A       B      C*
    base (in session)   0.4012  0.1635  0.34938       -       -       -       -       -
    seeds_s20260909     1.1365  0.3463  0.27719  +0.7353 +0.1827  +2.952  +2.653  +2.332
    stepD               0.9587  0.2795  0.28167  +0.5575 +0.1160  +2.255  +1.979  +1.757
    stepB512            1.2623  0.4361  0.36089  +0.8611 +0.2726  +2.349  +2.386  +2.424
    stepB2048           1.1021  0.3822  0.32282  +0.7010 +0.2186  +2.266  +2.171  +2.084

    verdict under C   stepA RISES | stepD __PARTIAL | stepB512 RISES | stepB2048 RISES

**The verdicts that change.** Only step D's, and only between A and the other two: A
gives RISES at +2.255, B gives __PARTIAL at +1.979, C gives __PARTIAL at +1.757. **C is
the least knife-edge of the three**, sitting furthest from the 2.0 threshold, which was
not known when the rule was chosen.

**Step A's seeds are unaffected**, as the ruling anticipated: 2.332, and the other two
seeds higher still.

## WHAT THIS AMENDMENT DOES NOT DO

It does not edit any banked artefact. The banked step A result keeps its own
`delta_bands` and `delta_bands_in_own_band` fields as banked. This amendment states
which of them governs, dated, and the recomputation lives beside them in a separate
all-constructions artefact.

Artefacts: `analyse_yi_adapter_controls_bands.py` (selftest 9/9) and its all-constructions
recomputation.

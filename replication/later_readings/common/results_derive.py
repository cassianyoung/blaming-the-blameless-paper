#!/usr/bin/env python3
"""results_derive.py : THE ONLY PLACE the ruled constructions are written.

Every table, figure and quoted number comes from `results/results.sqlite` through
these views. No table script reimplements a position, a band or a gate.

THE RETIRED RULES DO NOT EXIST HERE. Not as a fallback, not as a default, not behind
a flag. They appear in exactly one column, `gates.retired_rule_verdict`, which exists
so the audit can say what the instrument banked and is never read by a view that any
table consumes. The retired rules are:

    worksheet/completion   (P0 - N) >= 3 bands tiering, and mass(0-3) >= 0.8 thresholded
    chat                   N <= 1.05

`P0 - N` IS THE RESULT. A gate that requires it to be large refuses a model for
putting the careful agent at the floor, which is what it did to Yi-1.5-34B base on six
of six families (local_tuning's HALT 2; local_frames's audit).

CONSTRUCTIONS, as ruled:
  position      (X - N) / (C - N), on MEANS over orderings
  position_NI   (X - N) / (I - N), used where C is the quantity measured and so
                cannot be its own anchor
  band          2.33 x POPULATION sd over P0, P1, BYSTANDER across orderings.
                sd, not range: sd is stable in n where the range is not.
  pooled band   sqrt((b1^2 + b2^2) / 2) for a DIFFERENCE between two arms
  effect        P0 - N > 2 bands AND position clearly above zero
  involvement   P0 - BYSTANDER, in digits and in bands. On base models the named
                bystander is NOT at zero, so this is the involvement-specific part
                and P0 - N is not.
  completion    LICENSED iff (C - N) >= 3 bands AND answer mass >= 0.7
                mass(0-3) is REPORTED. P0 - N NEVER TIERS.
  chat          PASSED iff mass(0-3) >= 0.8 AND answer mass >= 0.7 AND I >= 7.0
                where I is read. N's mean is REPORTED, never thresholded.
                (The I ceiling is RULED ON: Cassian 2026-10-05, as local_tuning's
                recount_chat_floor.py already applied.)
  reasoning     a draw counts as reasoning if it carries reasoning TEXT **OR**
                reports reasoning TOKENS. A cell losing >10% of draws to truncation
                is reported with its void count and IS NOT USED.
"""
import math

BAND_SD_K = 2.33
CN_MIN_BANDS = 3.0          # completion: C - N
AMASS_MIN = 0.7             # both deliveries
MASS03_MIN = 0.8            # chat only
I_MIN = 7.0                 # chat only, RULED ON
EFFECT_BANDS = 2.0          # P0 - N, and P0 - BYSTANDER
VOID_MAX_FRACTION = 0.10    # a cell above this is reported and not used
BAND_ROLES = ("P0", "P1", "BYSTANDER")


def pstdev(xs):
    """Population sd, matching the instrument that banked the figures."""
    xs = [x for x in xs if x is not None]
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / n)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


def band(evs_by_role):
    """2.33 x sd over P0, P1, BYSTANDER across orderings; the mean of those three."""
    bs = []
    for r in BAND_ROLES:
        s = pstdev(evs_by_role.get(r) or [])
        if s is not None:
            bs.append(s * BAND_SD_K)
    return mean(bs)


def pooled_band(b1, b2):
    """For a DIFFERENCE between two arms. sqrt((b1^2 + b2^2)/2)."""
    if b1 is None or b2 is None:
        return None
    return math.sqrt((b1 ** 2 + b2 ** 2) / 2.0)


def position(x, n, c):
    if None in (x, n, c) or c == n:
        return None
    return (x - n) / (c - n)


def position_NI(x, n, i):
    if None in (x, n, i) or i == n:
        return None
    return (x - n) / (i - n)


def completion_gate(c_minus_n_bands, answer_mass):
    """RULED. Returns (verdict, components). mass(0-3) is NOT consulted."""
    if c_minus_n_bands is None or answer_mass is None:
        return None, {"why": "C-N band or answer mass absent; REFUSES to guess"}
    ok = (c_minus_n_bands >= CN_MIN_BANDS and answer_mass >= AMASS_MIN)
    return ("LICENSED" if ok else "FAILED"), {
        "C_minus_N_bands": c_minus_n_bands, "answer_mass": answer_mass,
        "rule": f"(C-N) >= {CN_MIN_BANDS} bands AND answer mass >= {AMASS_MIN}; "
                f"mass(0-3) reported, not thresholded; P0-N never tiers"}


def chat_gate(mass_0_3, answer_mass, i_ev):
    """RULED, with the I ceiling ON. Returns (verdict, components)."""
    if mass_0_3 is None or answer_mass is None:
        return None, {"why": "mass(0-3) or answer mass absent; REFUSES to guess"}
    ok = (mass_0_3 >= MASS03_MIN and answer_mass >= AMASS_MIN)
    if i_ev is not None:
        ok = ok and i_ev >= I_MIN
    return ("PASSED" if ok else "FAILED"), {
        "mass_0_3": mass_0_3, "answer_mass": answer_mass, "I": i_ev,
        "rule": f"mass(0-3) >= {MASS03_MIN} AND answer mass >= {AMASS_MIN}"
                + (f" AND I >= {I_MIN}" if i_ev is not None
                   else " (I not read on this cell)")
                + "; N mean reported, never thresholded"}


def effect_present(p0, n, bd, pos):
    """P0 - N > 2 bands AND position clearly above zero."""
    if None in (p0, n, bd, pos) or bd == 0:
        return None
    return ((p0 - n) / bd) > EFFECT_BANDS and pos > 0


def involvement(p0, bystander, n, c, bd):
    """P0 - BYSTANDER in digits, position units and bands, plus the >2 band test."""
    if None in (p0, bystander):
        return None
    d = p0 - bystander
    out = {"digits": d,
           "bands": (d / bd) if bd else None,
           "position_units": (position(p0, n, c) - position(bystander, n, c))
           if None not in (n, c) and c != n else None}
    out["clears_2_bands"] = (out["bands"] is not None
                             and out["bands"] > EFFECT_BANDS)
    return out


def reasoning_usable(n_void, n_asked):
    """>10% of draws lost to truncation: reported WITH its void count, not used.
    A reasoning void is a SELECTION ON THE VARIABLE OF INTEREST: the draws killed
    are the ones that reasoned longest (deployed_bicycle_ladder, factor 19 in reasoning length)."""
    if n_asked in (None, 0):
        return None, None
    frac = (n_void or 0) / n_asked
    return (frac <= VOID_MAX_FRACTION), frac


# ── THE VIEWS. One definition, consumed by every table script. ────────────────
VIEWS = {
 # ── THE SIX CONSTRUCTIONS THAT WERE PYTHON FUNCTIONS ARE NOW VIEWS ─────────────
 # Ruled by Cassian 2026-10-05: "make the views the single definition". The functions
 # above are KEPT because they are what banked every existing figure and they are the
 # reference the views were verified against, cell by cell, before the gate computation
 # was switched over. They are no longer the definition consumed by anything.
 #
 # TWO THINGS THE SQL HAS TO HONOUR, both easy to get silently wrong:
 #   pstdev RETURNS NONE BELOW n=2, so a role with one ordering is EXCLUDED from the
 #   band rather than counted as zero. `CASE WHEN n >= 2` does that; COALESCE to 0 would
 #   quietly shrink every band that has a thin role in it.
 #   THE SD IS TWO-PASS, as Python's is. AVG(ev*ev) - AVG(ev)*AVG(ev) is algebraically
 #   the same and numerically looser, and these values divide into published figures.
 "role_mean": """
    CREATE VIEW role_mean AS
        SELECT artefact_id, family, question, role,
               AVG(ev) AS m, COUNT(ev) AS n
        FROM orderings WHERE ev IS NOT NULL AND (void IS NULL OR void = 0)
        GROUP BY artefact_id, family, question, role
 """,
 "role_sd": """
    CREATE VIEW role_sd AS
        SELECT o.artefact_id, o.family, o.question, o.role, rm.n,
               CASE WHEN rm.n >= 2
                    THEN SQRT(MAX(SUM((o.ev - rm.m) * (o.ev - rm.m)) / rm.n, 0.0))
               END AS sd
        FROM orderings o
        JOIN role_mean rm ON rm.artefact_id = o.artefact_id
                         AND rm.family IS o.family
                         AND rm.question IS o.question
                         AND rm.role = o.role
        WHERE o.ev IS NOT NULL AND (o.void IS NULL OR o.void = 0)
        GROUP BY o.artefact_id, o.family, o.question, o.role
 """,
 "band": """
    CREATE VIEW band AS
        SELECT artefact_id, family, question,
               2.33 * AVG(sd) AS band,
               COUNT(sd) AS n_roles_in_band
        FROM role_sd
        WHERE role IN ('P0', 'P1', 'BYSTANDER') AND sd IS NOT NULL
        GROUP BY artefact_id, family, question
 """,
 "completion_gate": """
    CREATE VIEW completion_gate AS
        SELECT b.artefact_id, b.family, b.question, b.band,
               (c.m - n.m) / b.band AS c_minus_n_bands,
               am.min_answer_mass AS answer_mass,
               CASE WHEN b.band IS NULL OR c.m IS NULL OR n.m IS NULL
                      OR am.min_answer_mass IS NULL THEN NULL
                    WHEN (c.m - n.m) / b.band >= 3.0
                     AND am.min_answer_mass >= 0.7 THEN 'LICENSED'
                    ELSE 'FAILED' END AS verdict,
               '(C-N) >= 3.0 bands AND answer mass >= 0.7; mass(0-3) reported, not '
               || 'thresholded; P0-N never tiers' AS rule_applied
        FROM band b
        LEFT JOIN role_mean n ON n.artefact_id=b.artefact_id AND n.family IS b.family
                             AND n.question IS b.question AND n.role='N'
        LEFT JOIN role_mean c ON c.artefact_id=b.artefact_id AND c.family IS b.family
                             AND c.question IS b.question AND c.role='C'
        LEFT JOIN (SELECT artefact_id, family, question,
                          MIN(answer_mass) AS min_answer_mass
                   FROM orderings WHERE (void IS NULL OR void=0)
                   GROUP BY artefact_id, family, question) am
               ON am.artefact_id=b.artefact_id AND am.family IS b.family
              AND am.question IS b.question
 """,
 "chat_gate": """
    CREATE VIEW chat_gate AS
        SELECT g.artefact_id, g.family, g.question, g.mass_0_3, g.answer_mass, g.i_mean,
               CASE WHEN g.mass_0_3 IS NULL OR g.answer_mass IS NULL THEN NULL
                    WHEN g.mass_0_3 >= 0.8 AND g.answer_mass >= 0.7
                     AND (g.i_mean IS NULL OR g.i_mean >= 7.0) THEN 'PASSED'
                    ELSE 'FAILED' END AS verdict,
               'mass(0-3) >= 0.8 AND answer mass >= 0.7'
               || CASE WHEN g.i_mean IS NULL THEN ' (I not read on this cell)'
                       ELSE ' AND I >= 7.0' END
               || '; N mean reported, never thresholded' AS rule_applied
        FROM (SELECT am.artefact_id, am.family, am.question,
                     am.min_answer_mass AS answer_mass, i.m AS i_mean,
                     -- ── A MASS IS A MEAN OVER THE ORDERINGS, NEVER A SUM ─────
                     -- This read `SUM(j.value)` across a CROSS JOIN of every
                     -- blameless cell in the group with its own probability vector,
                     -- so an artefact with five orderings reported five times the
                     -- mass. 206 of 273 rows came back above 1.0 and the largest was
                     -- 8.3142, which is not a probability. Against a 0.8 threshold
                     -- that is a gate ANY artefact with two or more orderings passes
                     -- by construction: 47 cells PASSED under the sum that FAIL under
                     -- the mean and NONE go the other way, so the error only ever
                     -- admitted. Found by testing this view against a second one
                     -- built over `cells`, which is the only reason an impossible
                     -- value in a column nobody prints was ever looked at.
                     (SELECT AVG(m) FROM
                        (SELECT (SELECT SUM(j.value) FROM json_each(cn.probs) j
                                  WHERE j.key < 4) AS m
                         FROM cells cn
                         WHERE cn.artefact_id=am.artefact_id
                           AND cn.family IS am.family
                           AND cn.question IS am.question AND cn.role='N'
                           AND cn.probs IS NOT NULL)) AS mass_0_3
              FROM (SELECT artefact_id, family, question,
                           MIN(answer_mass) AS min_answer_mass
                    FROM orderings WHERE (void IS NULL OR void=0)
                    GROUP BY artefact_id, family, question) am
              LEFT JOIN role_mean i ON i.artefact_id=am.artefact_id
                                   AND i.family IS am.family
                                   AND i.question IS am.question AND i.role='I') g
 """,
 "effect_present": """
    CREATE VIEW effect_present AS
        SELECT p.artefact_id, p.family, p.question, b.band,
               (p.m - n.m) / b.band AS p0_minus_n_bands,
               (p.m - n.m) / (c.m - n.m) AS p0_position,
               CASE WHEN b.band IS NULL OR b.band = 0 OR p.m IS NULL OR n.m IS NULL
                      OR c.m IS NULL OR c.m = n.m THEN NULL
                    WHEN (p.m - n.m) / b.band > 2.0
                     AND (p.m - n.m) / (c.m - n.m) > 0 THEN 1
                    ELSE 0 END AS effect_present
        FROM role_mean p
        JOIN band b ON b.artefact_id=p.artefact_id AND b.family IS p.family
                   AND b.question IS p.question
        LEFT JOIN role_mean n ON n.artefact_id=p.artefact_id AND n.family IS p.family
                             AND n.question IS p.question AND n.role='N'
        LEFT JOIN role_mean c ON c.artefact_id=p.artefact_id AND c.family IS p.family
                             AND c.question IS p.question AND c.role='C'
        WHERE p.role='P0'
 """,
 "involvement": """
    CREATE VIEW involvement AS
        SELECT p.artefact_id, p.family, p.question, b.band,
               p.m AS p0_ev, y.m AS bystander_ev,
               p.m - y.m AS gap_digits,
               (p.m - y.m) / b.band AS gap_bands,
               (p.m - y.m) / (c.m - n.m) AS gap_position_units,
               CASE WHEN b.band IS NULL OR p.m IS NULL OR y.m IS NULL THEN NULL
                    WHEN (p.m - y.m) / b.band > 2.0 THEN 1 ELSE 0 END
                 AS clears_2_bands
        FROM role_mean p
        JOIN role_mean y ON y.artefact_id=p.artefact_id AND y.family IS p.family
                        AND y.question IS p.question AND y.role='BYSTANDER'
        LEFT JOIN band b ON b.artefact_id=p.artefact_id AND b.family IS p.family
                        AND b.question IS p.question
        LEFT JOIN role_mean n ON n.artefact_id=p.artefact_id AND n.family IS p.family
                             AND n.question IS p.question AND n.role='N'
        LEFT JOIN role_mean c ON c.artefact_id=p.artefact_id AND c.family IS p.family
                             AND c.question IS p.question AND c.role='C'
        WHERE p.role='P0'
 """,
 "reasoning_cells": """
    CREATE VIEW reasoning_cells AS
        SELECT c.artefact_id, a.run, a.arm, a.readout, a.sha256 AS artefact_sha256,
               c.family, c.role, c.question,
               c.reasoning_configured, c.ev_source,
               c.ev, c.ev_reasoning_only, c.ev_all_draws,
               c.n_draws, c.n_reasoning, c.reasoning_share, c.thin,
               c.n_void,
               CASE WHEN c.n_draws IS NULL OR c.n_draws = 0 THEN NULL
                    ELSE 1.0 * COALESCE(c.n_void, 0) / c.n_draws END AS void_fraction,
               CASE WHEN c.n_draws IS NULL OR c.n_draws = 0 THEN NULL
                    WHEN 1.0 * COALESCE(c.n_void, 0) / c.n_draws <= 0.10 THEN 1
                    ELSE 0 END AS reasoning_usable,
               c.reasoned_despite_off
        FROM cells c JOIN artefacts a ON a.id = c.artefact_id
        WHERE c.reasoning_configured IS NOT NULL
 """,
 # ── POSITIONS FOR THE API RUNS, WHICH `positions` CANNOT REACH ─────────────────
 # `ordering_means`, `positions` and `positions_value` all rest on `orderings`, and the
 # API runs (214, 215, 220, 221) populate `cells` and NOTHING in `orderings`: they read
 # once per prompt with draws, not five permuted orderings. So every API arm is absent
 # from those three views by construction, which is why `positions_value` returns zero
 # rows for llama70b and why Tables 7 and 8 cannot be seeded from it at all.
 #
 # **THIS IS THE SECOND TIME TODAY AN orderings-ONLY VIEW SILENTLY EXCLUDED EVERY API
 # RUN** (the first was a `final` table that contained one run and looked complete), so
 # it is written down here rather than rediscovered a third time.
 #
 # `cell_means` averages over whatever rows exist for a cell: over FRAMES on a pod run,
 # which makes it equal to `ordering_means`, and over the single row on an API run. The
 # two are asserted equal on the pod runs by the build test, so this is an extension of
 # the same construction and not a rival to it.
 #
 # `family IS m.family`, NOT `=`. local_tuning's artefacts carry family NULL and NULL = NULL
 # is NULL in SQL rather than true, which once made every position in `positions` NULL.
 "cell_means": """
    CREATE VIEW cell_means AS
        SELECT artefact_id, family, question, role,
               AVG(ev) AS m, COUNT(ev) AS n
        FROM cells WHERE ev IS NOT NULL AND (void IS NULL OR void = 0)
        GROUP BY artefact_id, family, question, role
 """,
 # ── THE ANCHOR CONVENTION, AS A VIEW, BECAUSE A GATE HAS TO SEE IT ─────────────
 # **Ruled: where a reasoning arm declined to reason on N or I, the anchor is taken from
 # ALL DRAWS and flagged; C and P0 are never substituted.** That convention lived in
 # Python inside ONE exporter (`build_b2_deployed_bicycle`), so everything else was
 # blind to it, and the three files describing gpt-6-sol's bicycle disagreed about the
 # same cell: `B2_deployed_bicycle.csv` printed I = 9.00 from all draws, while
 # `appendix_B2.csv` printed I empty with "not read" and `fig1_panelB.csv`'s gate note
 # said "I not read" -- because the gate reads `cell_means`, which is `cells.ev`, which
 # for a reasoning arm is the reasoning-only value and is NULL on a cell no draw
 # reasoned on. All three were faithful to their own source. A convention implemented
 # once downstream is not a convention, it is one exporter's behaviour.
 #
 # THE SUBSTITUTION IS PER GROUP, NOT PER CELL. `AVG(COALESCE(ev, ev_all_draws))` would
 # mix the two readings inside one role whenever some of its cells reasoned and others
 # did not, which is a third quantity belonging to neither convention. So the group asks
 # whether it has ANY reasoning-only reading, and takes all draws only if it has none.
 #
 # Measured when it was introduced: four groups gain an I that `cell_means` lacks, all
 # of them gpt6s_r, all 9.0000, all from all draws, and all above the 7.0 clause, so no
 # gate verdict moves. Zero groups disagree with `cell_means` where that view has a
 # value, which is the property that makes this an extension rather than a change.
 "cell_anchor_means": """
    CREATE VIEW cell_anchor_means AS
        SELECT artefact_id, family, question, role,
               CASE WHEN COUNT(ev) > 0 THEN AVG(ev)
                    ELSE AVG(ev_all_draws) END AS m,
               CASE WHEN COUNT(ev) > 0 THEN COUNT(ev)
                    ELSE COUNT(ev_all_draws) END AS n,
               CASE WHEN COUNT(ev) > 0 THEN 0 ELSE 1 END AS from_all_draws
        FROM cells
        WHERE role IN ('N', 'I') AND (void IS NULL OR void = 0)
        GROUP BY artefact_id, family, question, role
 """,
 "cell_positions": """
    CREATE VIEW cell_positions AS
        SELECT m.artefact_id, a.run, a.card, a.arm, a.delivery, a.readout,
               a.sha256 AS artefact_sha256,
               m.family, m.role, m.question, m.m AS ev_mean, m.n AS n_obs,
               n.m AS n_mean, c.m AS c_mean, i.m AS i_mean,
               CASE WHEN c.m IS NOT NULL AND n.m IS NOT NULL AND c.m <> n.m
                    THEN (m.m - n.m) / (c.m - n.m) END AS position,
               CASE WHEN i.m IS NOT NULL AND n.m IS NOT NULL AND i.m <> n.m
                    THEN (m.m - n.m) / (i.m - n.m) END AS position_NI
        FROM cell_means m
        JOIN artefacts a ON a.id = m.artefact_id
        LEFT JOIN cell_means n ON n.artefact_id=m.artefact_id AND n.family IS m.family
                              AND n.question IS m.question AND n.role='N'
        LEFT JOIN cell_means c ON c.artefact_id=m.artefact_id AND c.family IS m.family
                              AND c.question IS m.question AND c.role='C'
        LEFT JOIN cell_means i ON i.artefact_id=m.artefact_id AND i.family IS m.family
                              AND i.question IS m.question AND i.role='I'
 """,
 # ── THE CHAT GATE OVER `cells`, WHICH IS THE ONLY WAY AN API ARM CAN BE GATED ───
 # `chat_gate` is built FROM `orderings`, and API runs populate `cells` only, so it
 # returns NOTHING for every deployed model: the figure could not fade a single API row
 # because the gate column was empty, not because the arms passed. This is the same
 # structural trap as positions_value/positions/ordering_means, which is why
 # cell_positions exists, and it has now cost three readings.
 #
 # THE RULE IS THE RULED ONE, UNCHANGED: mass(0-3) >= 0.8 on the blameless cell AND
 # answer mass >= 0.7 AND I >= 7.0 where read; the N mean is reported, never thresholded.
 #
 # AND IT HAS THREE OUTCOMES, NOT TWO. mass(0-3) is a LOG-PROB quantity: digit_cell sets
 # `probs` and `mass_0_3` only on the logprob path, so a SAMPLED arm has none from its
 # artefact and the share is recoverable only from its draws. Where neither exists the
 # verdict is UNREADABLE, never FAILED: a gate that cannot be evaluated and a gate that
 # was evaluated and failed are different facts, and reporting the first as the second
 # would have faded exactly the rows whose instrument was missing.
 "cell_chat_gate": """
    CREATE VIEW cell_chat_gate AS
        SELECT am.artefact_id, am.family, am.question,
               am.min_answer_mass AS answer_mass, i.m AS i_mean, nm.mass_0_3,
               nm.mass_0_3_source, nn.m AS n_mean,
               -- ── A COMPLETION ROW IS NEVER JUDGED BY THE CHAT RULE ───────────
               -- This view emitted a verdict for EVERY delivery, including 209
               -- completion rows (141 FAILED, 68 PASSED), and anything joining on
               -- (arm, run, family) without a delivery clause picked one of them up.
               -- llama31_base's ladder read FAILED here on blameless mass 0.8406 and
               -- I 6.6178 -- the CHAT thresholds -- while completion_gate reads it
               -- LICENSED at 11.33 bands. **That is the retired fixed-threshold logic
               -- returning by another route**, not through the old code but through
               -- the wrong rule being available to the wrong rows.
               -- A rule that declines to answer outside its own delivery cannot be
               -- misapplied by a join that forgot a column.
               CASE WHEN ag.delivery = 'completion' THEN 'WRONG_RULE_FOR_DELIVERY'
                    WHEN nm.mass_0_3 IS NULL OR am.min_answer_mass IS NULL
                         THEN 'UNREADABLE'
                    WHEN nm.mass_0_3 >= 0.8 AND am.min_answer_mass >= 0.7
                     AND (i.m IS NULL OR i.m >= 7.0) THEN 'PASSED'
                    ELSE 'FAILED' END AS verdict,
               CASE WHEN ag.delivery = 'completion' THEN
                      'the worksheet frame is gated by the COMPLETION rule ((C-N) >= 3 '
                      || 'bands AND answer mass >= 0.7). This view is the chat rule and '
                      || 'declines to judge it; use cell_gate, which picks by delivery'
                    WHEN nm.mass_0_3 IS NULL THEN
                      'UNREADABLE: no mass(0-3) on the blameless cell. It is a log-prob '
                      || 'quantity and this arm was not read that way'
                    WHEN am.min_answer_mass IS NULL THEN
                      'UNREADABLE: no answer mass on any cell of this scenario'
                    ELSE 'mass(0-3) >= 0.8 AND answer mass >= 0.7'
                      || CASE WHEN i.m IS NULL THEN ' (I not read on this cell)'
                              WHEN i.from_all_draws = 1 THEN
                                ' AND I >= 7.0 (the deliberate case read from ALL '
                                || 'DRAWS under the anchor convention: no draw of it '
                                || 'reasoned)'
                              ELSE ' AND I >= 7.0' END
                      || '; N mean reported, never thresholded' END AS rule_applied
        FROM (SELECT artefact_id, family, question,
                     MIN(answer_mass) AS min_answer_mass
              FROM cells WHERE answer_mass IS NOT NULL
              GROUP BY artefact_id, family, question) am
        JOIN artefacts ag ON ag.id = am.artefact_id
        -- ── THE MASS COMES FROM EITHER PLACE IT IS STORED ─────────────────────
        -- Two populations store it two ways and a view that reads one of them is a
        -- gate that cannot fire on the other. API cells carry a `mass_0_3` COLUMN
        -- (243 of 243 blameless cells) and mostly no `probs`; pod cells carry `probs`
        -- as a JSON ARRAY and no column at all (0 of 1,107). Reading the column alone
        -- returned UNREADABLE on every one of those 1,107 pod rows while `chat_gate`
        -- read them fine, which is how the first cut of this view disagreed with it
        -- on 1,107 of 1,107 overlapping rows. json_each over an array yields keys
        -- 0..9, so `key < 4` is the same mass(0-3) chat_gate computes, and the
        -- agreement test is what refused to let the first version stand.
        -- GROUPED, because a group can hold several blameless cells (up to ten on
        -- card 216) and an ungrouped join FANS OUT: the first cut of this view
        -- emitted one row per ordering, each carrying that ordering's own mass, so a
        -- scenario appeared four times with four different verdicts. One row per
        -- (artefact, family, question), and the mass is the mean of the group's cells.
        LEFT JOIN (SELECT artefact_id, family, question,
                          MIN(mass_0_3_source) AS mass_0_3_source,
                          AVG(COALESCE(mass_0_3,
                                       (SELECT SUM(j.value) FROM json_each(probs) j
                                         WHERE j.key < 4))) AS mass_0_3
                   FROM cells WHERE role='N'
                   GROUP BY artefact_id, family, question) nm
               ON nm.artefact_id=am.artefact_id AND nm.family IS am.family
              AND nm.question IS am.question
        LEFT JOIN cell_means nn ON nn.artefact_id=am.artefact_id
                               AND nn.family IS am.family
                               AND nn.question IS am.question AND nn.role='N'
        -- the I clause reads the ANCHOR, which is the reasoning-only value where one
        -- exists and all draws where none does. Reading `cell_means` here is what made
        -- the gate note say "I not read" about a cell B.2 reports at 9.00.
        LEFT JOIN cell_anchor_means i ON i.artefact_id=am.artefact_id
                              AND i.family IS am.family
                              AND i.question IS am.question AND i.role='I'
 """,
 # ── ONE GATE, CHOSEN BY DELIVERY, AND IT IS THE ONLY ONE A REPORT SHOULD READ ───
 # The ruled rules are different quantities on different scales: chat gates on the
 # blameless cell's mass(0-3) with a deliberate-case floor, the worksheet gates on
 # (C-N) in BANDS. Neither threshold means anything applied to the other's rows, and
 # leaving both available to a join is how a worksheet row came to be judged by the chat
 # rule. This view answers "did this row pass ITS gate", which is the only question a
 # figure ever wants, and it carries the rule it used so a reader can see which fired.
 "cell_gate": """
    CREATE VIEW cell_gate AS
        SELECT a.id AS artefact_id, a.arm, a.run, a.card, a.delivery,
               g.family, g.question, g.verdict, g.rule_applied,
               g.rule_kind, g.stat_name, g.stat_value, g.answer_mass,
               g.i_mean, g.n_mean
        FROM artefacts a JOIN (
            SELECT artefact_id, family, question, verdict, rule_applied,
                   'completion' AS rule_kind, '(C-N) in bands' AS stat_name,
                   c_minus_n_bands AS stat_value, answer_mass,
                   -- the chat rule's two extra quantities do not exist for the
                   -- worksheet rule and are NULL rather than borrowed, so a reader
                   -- cannot accidentally threshold a quantity this rule never used
                   NULL AS i_mean, NULL AS n_mean
            FROM completion_gate
            UNION ALL
            SELECT artefact_id, family, question, verdict, rule_applied,
                   'chat' AS rule_kind, 'mass(0-3) on the blameless cell' AS stat_name,
                   mass_0_3 AS stat_value, answer_mass, i_mean, n_mean
            FROM cell_chat_gate
        ) g ON g.artefact_id = a.id
        WHERE (a.delivery = 'completion' AND g.rule_kind = 'completion')
           OR (a.delivery <> 'completion' AND g.rule_kind = 'chat')
 """,
 "ordering_means": """
    CREATE VIEW ordering_means AS
    SELECT artefact_id, family, role, question,
           AVG(ev) AS ev_mean, COUNT(ev) AS n_orderings
    FROM orderings GROUP BY artefact_id, family, role, question;""",

 "positions": """
    CREATE VIEW positions AS
    SELECT m.artefact_id, a.run, a.card, a.arm, a.delivery, m.family, m.role,
           m.ev_mean,
           -- `family IS m.family`, NOT `=`. local_tuning's artefacts carry family NULL
           -- (the bicycle bank has no family column) and `NULL = NULL` is NULL in
           -- SQL, not true, so every subquery returned NULL and EVERY POSITION IN
           -- THE VIEW WAS NULL. Caught by the Table 5 reproduction test, which is
           -- the whole reason that test exists: a view that silently yields NULL
           -- produces an empty table rather than a wrong number, and an empty table
           -- is easy to mistake for "not ingested yet".
           (SELECT ev_mean FROM ordering_means WHERE artefact_id=m.artefact_id
              AND family IS m.family AND role='N' AND question=m.question) AS n_mean,
           (SELECT ev_mean FROM ordering_means WHERE artefact_id=m.artefact_id
              AND family IS m.family AND role='C' AND question=m.question) AS c_mean,
           (SELECT ev_mean FROM ordering_means WHERE artefact_id=m.artefact_id
              AND family IS m.family AND role='I' AND question=m.question) AS i_mean,
           m.n_orderings, m.question
    FROM ordering_means m JOIN artefacts a ON a.id=m.artefact_id;""",

 "positions_value": """
    CREATE VIEW positions_value AS
    SELECT *,
      CASE WHEN c_mean IS NOT NULL AND n_mean IS NOT NULL AND c_mean<>n_mean
           THEN (ev_mean-n_mean)/(c_mean-n_mean) END AS position,
      CASE WHEN i_mean IS NOT NULL AND n_mean IS NOT NULL AND i_mean<>n_mean
           THEN (ev_mean-n_mean)/(i_mean-n_mean) END AS position_NI
    FROM positions;""",
}

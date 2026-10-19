#!/usr/bin/env python3
"""THE ONE PLACE AN ARM IS EXCLUDED FROM REPORTING.

Before this module, five exporters each held their own exclusion table:
build_across_scenarios, build_b5_across_scenarios, build_b8_judgement,
figure1_panelB and build_figure1. They overlapped, they had drifted, and removing an
arm meant editing five lists and hoping. Appendix B.5 excluded `gemma27b_relaxed` and
`across_scenarios` did not; `figure1_panelB` knew the Haiku supersession and B.8 learned
it second-hand through B.5's file.

**AN ARTEFACT IS NEVER DELETED AND A ROW IS NEVER EDITED OUT OF A FILE.** The artefacts
stay in the database untouched and keep their cells; only REPORTING excludes them, by
this rule, so a reader can always ask what was measured and get a different answer from
what was reported. That distinction is the whole reason the exclusion lists exist.

Every exporter asks `excluded(arm)` and, if the answer is not None, writes the arm to its
own excluded-list file with that reason rather than a reported row. The build asserts
both halves: no reported row carries an excluded arm, and every excluded-list file names
each one with the reason from here.
"""

# ── READ BUT NOT REPORTED ───────────────────────────────────────────────────────
# An arm whose coverage is too thin to appear in a table that compares arms across
# scenarios. It was measured, it is in the database, and it is listed in Table 3 under
# "read, not reported" so the measurement is not lost by being unreported.
NOT_REPORTED = {
    "gptoss_r": "read on the bicycle only; not reported",
    "gemma27b_relaxed":
        "a relaxed-decoding probe of gemma27b, not a deployed configuration: it exists "
        "to test whether the arm's answer moves under a different sampling setting",
    # gemini_pro was here ("side-by-side only: never read the families or the
    # bicycle") until the v1.1 fill read it on the excuse test, all six scenarios
    # (completeness_fill_amendment C1, completeness_fill, registered as read later like gemini_pro_fill).
    # The reason stopped being true, so the exclusion is removed rather than kept.
}

# ── PARTIAL READS THAT ARE NOT ARMS ─────────────────────────────────────────────
PARTIAL = {
    "gemini_anchor": "a one-family anchor re-read, not an arm",
    "gemini_duty": "the duty factorial only, a different bank",
    "gemini_duty_N": "a blameless-row top-up for the duty factorial",
    "gemini_topup":
        "a top-up adding draws to gemini_r's cells; counting it beside gemini_r would "
        "double those draws",
}

# ── SUPERSEDED: ONE MODEL, A LATER AND FULLER READING ───────────────────────────
SUPERSEDED = {
    "haiku":
        "superseded by the full-bank reading in deployed_added_models as `haiku_s`: deployed_bicycle_rivals read only "
        "N, C, P0 and P1 on this model, deployed_added_models read all ten bicycle roles, the five "
        "scenarios and the side-by-side. Same weights and same configuration under two "
        "arm names",
    "deepseek_r":
        "the deployed_bicycle_ladder/215 DeepSeek reasoning arm, superseded by the mt-8192 re-read: a "
        "truncation void on a reasoning arm is a selection on the variable of interest",
    "deepseek_r_bike8192":
        "the THREE-role bicycle read (N, C and I only). The ten-role read "
        "`deepseek_r_bike8192_all` is the one carrying P0 and P1",
}

# ── RESOLVED INTO ANOTHER ARM: A LABELLING TABLE, AND NOT AN EXCLUSION ─────────
# **READ THIS BEFORE WIRING IT INTO `excluded()`. IT WAS, AND IT DELETED SEVEN ARMS.**
# `gpt6l_r_bike` is the name the BICYCLE reading of gpt6l_r was banked under, and
# `gpt6l_r` is the name its five other scenarios were banked under. Neither is a
# spare copy of the other: they are two halves of one arm, banked separately.
#
# So the two kinds of export want opposite things from this table:
#   - `across_scenarios` wants ONE ROW PER ARM PER SCENARIO, so it must merge the two
#     names and report them under one label. That is a RENAME.
#   - panel B, B.2, appendix B.2, B.5 and B.8 are BICYCLE tables, and they report the
#     bicycle under the name it was banked under. For them `gpt6l_r_bike` IS the arm.
#
# Having `excluded()` consult this table served the first and destroyed the second:
# panel B fell from 22 arms to 16, B.5 from 22 to 16, B.8 from 1001 rows to 716, and
# the DeepSeek reasoning arm vanished from every table at once, because its two halves
# were each excluded as a half of the other. The removal of ONE arm (gptoss_r) silently
# removed SEVEN, and every export still passed its own checks, because each had lost
# the same arms consistently.
#
# **AN EXCLUSION LAYER MAY DROP AN ARM; IT MAY NOT RENAME ONE.** The merge belongs
# where the merge happens, in `build_across_scenarios.RESOLVE`, which holds these same
# seven entries for that purpose. This table is kept here as documentation of the
# pairing and is deliberately NOT consulted by `excluded()` or `all_excluded()`.
RESOLVED_INTO = {
    "gpt6l_r_bike": "gpt6l_r", "gpt6l_s_bike": "gpt6l_s",
    "gpt6s_r_bike": "gpt6s_r", "gpt6s_s_bike": "gpt6s_s",
    "grok43_r_bike": "grok43_r", "grok43_s_bike": "grok43_s",
    "deepseek_r_bike8192_all": "deepseek_r_mt8192",
}

# ── WITHDRAWN ROLES: the arm is reported, named roles are not ───────────────────
# Keyed (arm, scenario) -> (roles, reason). Not an arm exclusion: the arm stays.
WITHDRAWN_ROLES = {
    ("gemini_r", "bicycle"): (
        ("P1_R", "P1_neutral", "P2_other", "BYSTANDER"),
        "withdrawn (deployed_bicycle_rivals): the reasoning-detector defect. That pass ran at max_tokens "
        "8, where the reasoning consumed the output budget and the completion came back "
        "EMPTY, so the draws that parsed were the draws that did NOT reason. Under the "
        "corrected text-OR-tokens predicate its blameless cell reads 1 parsed of 17 "
        "reasoned draws"),
}


# ── PAIRS EXCLUDED FROM REPORTING, BY RULE ─────────────────────────────────────
# Same discipline as the arm exclusions above: the artefacts stay, every cell keeps its
# readings, and only REPORTING drops the pair, in one place, so no export can disagree
# with another about what is in.
#
# **herbal medicine (duty pair 2) is not reported.** Ruled by the author 2026-10-09: the
# convention is CONTESTED, because the private leg -- a parent giving a child a dose too
# high to be safe -- is arguably abusive rather than merely less culpable than a
# shopkeeper. A pair whose private side may read as a worse act cannot measure whether a
# professional duty raises blame: the two readings are confounded.
#
# The data already showed the pair behaving unlike the others, which is consistent with
# the ruling and is why it is worth recording here rather than only in a note:
#   - 6 of 17 arms REVERSED it when judging separately, the most of any pair;
#   - `gemini_r` stated -0.35 and `deepseek_r` stated -1.600, both blaming the parent
#     MORE than the shopkeeper in the comparison channel itself;
#   - its between-model CV was 0.67 reasoning-off and 1.06 reasoning-on, the second
#     worst of the six.
NOT_REPORTED_PAIRS = {
    2: "herbal medicine: a contested convention. The private leg (a parent giving a "
       "child too high a dose) is arguably abusive rather than less culpable, so the "
       "pair cannot isolate the professional duty. Read and banked; not reported.",
}

# the duty pairs that ARE reported, in the paper's order
DUTY_PAIRS = (3, 1, 4, 5)
PAIR_NAMES = {1: "electrical work", 2: "herbal medicine", 3: "gas safety",
              4: "childcare", 5: "driving"}


def pair_excluded(pair):
    """The reason this duty pair is not reported, or None."""
    return NOT_REPORTED_PAIRS.get(int(pair))


def reported_pairs(pairs=None):
    """The pairs of `pairs` that are reported, in order."""
    src = pairs if pairs is not None else sorted(PAIR_NAMES)
    return [p for p in src if pair_excluded(p) is None]


# ── THE GATE RULE, IN ONE SENTENCE, FOR EVERY COUNT IN THE PAPER ───────────────
# **A SCENARIO THAT FAILS A MODEL'S GATE IS EXCLUDED FROM EVERY COUNT FOR THAT MODEL,
# JUDGEMENT QUESTIONS INCLUDED.**
#
# Ruled 2026-10-08, after the same claim appeared with two denominators. The
# introduction's "86.0% of non-reasoning target-case readings place blame beyond the
# noise" was 74 of 86 over gate-passing cells; the section counts' "blame above 0.10"
# was 77 of 90 over every cell B.8 holds. **The two are the same sentence, and the four
# extra readings are the four cells whose own blame gate failed** (deepseek/cheque,
# kimi/cheque, mistral24b/cheque, qwen30b/scaffolding). Under the rule the second
# becomes 74 of 86 = 86.0% and the disagreement is gone.
#
# The trap was that the gate was understood as a condition on BLAME readings, and the
# judgement questions were read as a separate channel that the blame gate had no
# business filtering. But the gate is a statement about whether the model ANSWERED THE
# SCENARIO usably at all, so a scenario it fails is not a scenario about which that
# model said anything countable, whatever the channel. Mistral-Small's cheque
# prevention reading was 0.9669, a clear yes, on a scenario where its blame reading is
# refused: it was being counted as a fourth yes-scenario on the strength of a cell the
# paper does not otherwise use.
#
# LICENSED is the completion-delivery pass verdict and PASSED the chat one; both are
# passes, and the set is here rather than written out at each site so that a future
# verdict name cannot be honoured in one count and ignored in another.
GATE_PASSES = ("PASSED", "LICENSED")

# The same set as a SQL fragment, so the SQL sites and the Python sites cannot drift.
GATE_SQL = "gate IN ('" + "','".join(GATE_PASSES) + "')"


def gate_passes(verdict):
    """Does this gate verdict admit the cell to a count? See GATE_PASSES above."""
    return verdict in GATE_PASSES


def excluded(arm):
    """The reason this arm is not reported, or None if it is.

    RESOLVED_INTO is NOT consulted: see the comment above it. A name that is one half
    of an arm is reported, under whichever label the export in question uses.
    """
    for table in (NOT_REPORTED, PARTIAL, SUPERSEDED):
        if arm in table:
            return table[arm]
    return None


def all_excluded():
    """{arm: reason} over every exclusion, for an excluded-list file."""
    out = {}
    for table in (NOT_REPORTED, PARTIAL, SUPERSEDED):
        out.update(table)
    return out


def resolved_into(arm):
    """The arm this banked name is one half of, or None. A LABEL, not an exclusion."""
    return RESOLVED_INTO.get(arm)


def withdrawn_roles(arm, scenario):
    """(roles, reason) for an arm and scenario, or ((), "")."""
    v = WITHDRAWN_ROLES.get((arm, scenario))
    return v if v else ((), "")


def reported(arms):
    """The arms of `arms` that are reported, in order."""
    return [a for a in arms if excluded(a) is None]


# ── CHECK READOUTS: SHOWN, NOT COUNTED ──────────────────────────────────────────
# Ruled 2026-10-16 (records/RULE_ONE_READOUT_PER_MODEL.md). **MODELS** are distinct
# models in a given reasoning mode; **ARMS** are configurations read; the paper's pooled
# figures count models. Where one model was read by two readouts in the same mode, the
# log-probability reading is primary and the other is a CHECK: it keeps every row in
# every table, marked CHECK_MARK, and is excluded from every count, correlation, median,
# share, bootstrap and floor pooled over models.
#
# **THIS IS NOT AN EXCLUSION AND `excluded()` DOES NOT CONSULT IT.** An excluded arm
# leaves the tables; a check arm stays in them and leaves only the pools. Wiring this
# into `excluded()` would delete deepseek_s's rows from Tables A.2 to A.10, which is the
# RESOLVED_INTO accident above in a new place.
#
# Keyed by every name the check reading was banked under: in general_principle both DeepSeek
# arms were sampled (every arm was), and the rule still keys on the arm, so `deepseek`
# stays primary there too.
CHECK_READOUTS = {
    "deepseek_s": ("deepseek", "DeepSeek-V4.1 without reasoning, read by sampling; the "
                               "log-probability reading `deepseek` is the model's "
                               "primary readout"),
}
CHECK_MARK = "(check; not counted)"

# The same set as a SQL fragment, for `AND <col> NOT IN ...` at every pooled SQL site.
CHECK_SQL_LIST = "('" + "','".join(CHECK_READOUTS) + "')"


def counted(arm):
    """Does this arm enter figures pooled over models? False only for a check readout."""
    return arm not in CHECK_READOUTS


def check_of(arm):
    """The primary arm this arm is a check on, or None."""
    v = CHECK_READOUTS.get(arm)
    return v[0] if v else None


def not_counted_sql(col="arm"):
    """`<col> NOT IN (<check arms>)`, for a pooled SQL query."""
    return f"{col} NOT IN {CHECK_SQL_LIST}"

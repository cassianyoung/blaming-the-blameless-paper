#!/usr/bin/env python3
"""The duty test (duty_pairs, duty_remedies, duty_hair_dye) as tables and views in results/results.sqlite.

Imported by `build_results_db.py`: `SCHEMA` is appended to the build's DDL, `ingest()`
reads the banks and artefacts, `VIEWS` are created with the rest, `tests()` returns rows
in the build's own (name, ok, n, detail) shape. **There is no second database and no
derived quantity in this file's tables**: every gap, floor, baseline, class and share is
a view.

FIVE DECISIONS THIS FILE MAKES, each one recorded because a later reader will otherwise
have to guess:

  **`prawns` AND `6` ARE DIFFERENT PAIRS AND BOTH ARE REAL.** `prawns` is the chef
  against home cook contrast (duty_chef_home_comparison/deployed_added_models), a REPORTED duty pair and the reference
  column of Figure 7. `6` is the CONTROL, whose two parties are described identically so
  that its gap is noise by construction. They are easy to conflate because the control's
  separate case is the prawns_home text; they are not the same measurement and no view
  mixes them.

  **NEUTRAL #1 LIVES IN TWO BANKS, SO THE INGEST HANDLES A DOUBLE READ EVEN THOUGH
  THERE ISN'T ONE.** Bank v1 holds it as `R227_P{p}_A_neutral_*` and bank v2 as
  `R227B_P{p}_A1_neutral_*`, byte-identical items (the v2 builder asserts the sha).
  claude and deepseek were read on the whole of v1 and then on v2 with `--only A2,A3`,
  precisely so that A1 was not paid for twice, so **measured on the banked artefacts no
  arm holds both reads**: the halt arms' neutral #1 comes from v1 and every other arm's
  from v2. `preferred` and `duplicate_of` exist anyway, because the two banks CAN carry
  the same cell and a collision that silently dropped one would be invisible; the build
  test states which bank each arm's neutral #1 came from rather than printing an empty
  0 of 0.

  **A MISSING CELL IS A ROW.** An arm whose provider vanished mid-read has cells with
  `status='unread'` and an `unread_reason`, never a zero and never an absent row, so a
  count over `duty_cells` has the same denominator as the read that produced it.

  **`answer_mass` IS NULL ON EVERY DUTY CELL AND SAYS WHY.** The duty readers take `ev`
  from the served log-prob distribution where there is one and from the first digit of
  the raw text otherwise; they never bank a digit distribution. So the column exists for
  schema compatibility with `cells` and every row carries `answer_mass_note`. A view
  that averaged it would be averaging nothing.

  **THE DRAW ROWS ARE WHAT THE ARTEFACTS HOLD, WHICH IS NOT EVERYTHING.** `duty_draws`
  carries the parsed digit (or the CMPN gap) and its index among the PARSED draws, which
  is what `analyse_duty_pairs.py`'s `zip(pro, priv)` pairs. The artefacts do not hold a
  per-draw reasoning flag, provider or timestamp (only per-cell counts), so those are
  absent rather than invented; they are in the call logs, which the database deliberately
  does not reach into at report time.
"""
import glob
import hashlib
import json
import os
import re
import statistics

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys as _sys  # noqa: E402
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report_exclusions as _RX  # noqa: E402
# ONE READOUT PER MODEL (records/RULE_ONE_READOUT_PER_MODEL.md, 2026-10-16): the panel
# counts and medians pool over models, so a check readout keeps its duty_fig7 rows and
# is left out of every aggregate over them
_COUNTED = "arm NOT IN " + _RX.CHECK_SQL_LIST

# ── THE BANKS, WITH THE SHA EACH ONE IS FROZEN AT ─────────────────────────────
BANKS = {
 "duty":   ("data/duty_bank/moral__duty__v1.jsonl",
            "b0ca3175775f9c1f13d87a7dbf25f82f02be627aabf349e5ddadbd4c44baa9d6"),
 "r227v1": ("data/duty_bank/moral__duty227__v1.jsonl",
            "8c42e7b23e7a5f155f8ae8ab2b2102012ffb4e12c37ccfd4881643b3726fcc0c"),
 "r227v2": ("data/duty_bank/moral__duty227b__v1.jsonl",
            "66dfa615014cab33d4e626878230d7e2d567fe8caa54e854e008f4bdc6e43a5a"),
 "r228":   ("data/duty_bank/moral__duty228__v1.jsonl",
            "1ac42d76dcf2ab18812cf721954c356d466241ad080017186c5d4f100e33c21b"),
 "r229":   ("data/duty_bank/moral__duty229__v1.jsonl",
            "00505bd83dadb20d95fda9c5e2cdf2625f1403db0bf266b083053ab1058d2180"),
 "cmp":    ("data/cmp_bank/moral__cmp__v1.jsonl",
            "bccac4f56b6742f9b2c60c4bf4e8e1a4ef5aa7e11303f55bc1e9eedb9874f0e8"),
}
# ── THE v1.1 PRAWNS BANK (completeness_fill, completeness_fill_amendment H4 to H6) ────────
# Byte copies of due-care-eval's v1.1 bank at tag v1.1-rc1 (data/duty_bank_v1_1/README.md).
# Its rows carry `sha256` rather than a uid, so it has its own loader below.
V11_TEXTS = ("data/duty_bank_v1_1/duty_texts_v1_1.jsonl",
             "86a3af3cddaab9d329530720e08923ab0b21c33d50f5bc489632eae5fd134a83")
V11_QUESTIONS = ("data/duty_bank_v1_1/duty_questions_v1_1.json",
                 "3c8f6c45ca9520442972b903fa17ed5b6af4701bb22b475fba2113242cfc24c8")
# the same-session re-read of the banked summary prompt is its OWN condition, so no
# stated-gap view can average it with the banked summary or the full text
V11_COND = {"neutral_1": "neutral_1", "neutral_2": "neutral_2", "neutral_3": "neutral_3",
            "comparand": "comparand", "cause": "bare",
            "full_pro_first": "cmp_full_pro_first",
            "full_priv_first": "cmp_full_priv_first",
            "pro_first": "cmp_reread_pro_first", "priv_first": "cmp_reread_priv_first"}

# pair_id, name, status, pro_label, priv_label, victim_chose, bank key, aka
PAIRS = [
 ("prawns", "prawns (chef against home cook)", "reported", "CHEF", "HOME_COOK", 1,
  "cmp", "the reference column of Figure 7; duty_chef_home_comparison/deployed_added_models, not 225"),
 ("1", "electrical work", "reported", "ELECTRICIAN", "HOMEOWNER", 0, "duty", None),
 ("2", "herbal medicine", "retired", "SHOPKEEPER", "FATHER", None, "duty", None),
 ("3", "gas safety", "reported", "LANDLORD", "FRIEND", 1, "duty", None),
 ("4", "childcare", "reported", "CHILDMINDER", "GRANDFATHER", 0, "duty", None),
 ("5", "driving", "reported", "TAXI_DRIVER", "FRIEND", 1, "duty", None),
 ("6", "control (no duty difference)", "control", "HOST_A", "HOST_B", None, "duty",
  "the two parties are described identically, so its gaps are draw noise by "
  "construction. NOT the prawns pair."),
 ("7", "hair dye", "reported", "HAIRDRESSER", "FRIEND", 1, "r228", None),
]
# the arm chosen to represent each model, per configuration set. MIRRORED FROM
# dispersion_duty_pairs.py AND ASSERTED EQUAL TO IT in tests(), so the two cannot drift.
MODEL_ARM_OFF = {
 "anthropic/claude-sonnet-5": "claude",
 "anthropic/claude-haiku-4.5": "haiku_s",
 "deepseek/deepseek-v4.1-flash": "deepseek",        # LOG-PROB, as ruled
 "google/gemma-3-27b-it": "gemma27b",
 "meta-llama/llama-3.3-70b-instruct": "llama70b",
 "mistralai/mistral-small-3.2-24b-instruct": "mistral24b",
 "moonshotai/kimi-k3": "kimi",
 "openai/gpt-4o": "gpt4o",
 "openai/gpt-6-luna": "gpt6l_s",
 "openai/gpt-6-sol": "gpt6s_s",
 "qwen/qwen3-235b-a22b-2507": "qwen235b",
 "qwen/qwen3-30b-a3b-instruct-2507": "qwen30b",
 "qwen/qwen3-next-80b-a3b-instruct": "qwen80b",
 "x-ai/grok-4.3": "grok43_s",
}
MODEL_ARM_ON = {
 "deepseek/deepseek-v4.1-flash": "deepseek_r",
 "google/gemini-3.1-pro-preview": "gemini_pro",
 "google/gemini-3.8-flash": "gemini_r",
 "openai/gpt-6-luna": "gpt6l_r",
 "openai/gpt-6-sol": "gpt6s_r",
 "x-ai/grok-4.3": "grok43_r",
 "anthropic/claude-haiku-4.5": "haiku_r",
}
Z = 2.33
DRAW_FLOOR_MIN = 0.30
# the 22 arms the duty test was read on, so coverage has a denominator
ARMS = ["claude", "deepseek", "deepseek_r", "deepseek_s", "gemini_pro", "gemini_r",
        "gemma27b", "gpt4o", "gpt6l_r", "gpt6l_s", "gpt6s_r", "gpt6s_s", "grok43_r",
        "grok43_s", "haiku_r", "haiku_s", "kimi", "llama70b", "mistral24b",
        "qwen235b", "qwen30b", "qwen80b"]
PAIRED_ONLY = ("gemini_pro",)
# a later reading keeps the run of the bank it was read from (see ingest_cells)
LATER_RUN = {"duty": "225", "r227v1": "227", "r227v2": "227", "r228": "228",
             "r229": "229", "families": "220"}

MASS_NOTE = ("not recorded: the duty readers take ev from the served log-prob "
             "distribution where there is one and from the first digit of the raw "
             "text otherwise, and never bank a digit distribution")


class Refuse(Exception):
    pass


SCHEMA = """
-- ── THE DUTY TEST: RAW READINGS ONLY. EVERY DERIVED QUANTITY IS A VIEW. ────────
CREATE TABLE duty_pairs(
  pair_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL,                 -- reported | retired | control
  retired_reason TEXT,
  pro_label TEXT NOT NULL,
  priv_label TEXT NOT NULL,
  -- the assumption-of-risk grouping (duty_hair_dye.P5). NULL is allowed only off the reported
  -- set: the control has no victim and the retired pair was never grouped.
  victim_chose_arrangement INTEGER,
  bank TEXT NOT NULL,
  bank_sha TEXT NOT NULL,
  notes TEXT,
  CHECK (status IN ('reported', 'retired', 'control')),
  CHECK (status <> 'retired' OR retired_reason IS NOT NULL),
  CHECK (status <> 'reported' OR victim_chose_arrangement IS NOT NULL));

CREATE TABLE duty_texts(
  text_id TEXT PRIMARY KEY,
  pair_id TEXT NOT NULL REFERENCES duty_pairs(pair_id),
  leg TEXT NOT NULL,                    -- pro | priv | both
  kind TEXT NOT NULL,                   -- separate | comparison | convention |
                                        -- neutral | comparand | cause_question
  variant TEXT,                         -- neutral_1..3, pro_first/priv_first
  text TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  word_count INTEGER NOT NULL,
  bank TEXT NOT NULL,
  bank_sha TEXT NOT NULL,
  CHECK (leg IN ('pro', 'priv', 'both')));

CREATE TABLE duty_cells(
  cell_id TEXT PRIMARY KEY,
  run TEXT NOT NULL,                    -- 225 | 227 | 228 | 221/224 for prawns
  arm TEXT NOT NULL,
  pair_id TEXT NOT NULL REFERENCES duty_pairs(pair_id),
  leg TEXT NOT NULL,
  condition TEXT NOT NULL,              -- bare | neutral_1..3 | stated | comparand |
                                        -- cmp_pro_first | cmp_priv_first
  question TEXT NOT NULL,               -- BLAME | CAUSE | CMPN
  text_id TEXT REFERENCES duty_texts(text_id),
  text_id_reason TEXT,                  -- why text_id is NULL, where it is
  n_draws INTEGER NOT NULL,
  -- ── n_parsed MAY BE UNKNOWN, AND THEN IT IS NULL WITH A NOTE, NOT A GUESS ───
  -- The duty readers record it per cell. The FAMILIES cells the prawns separate gap
  -- is taken from do not: `cells.n_draws` and `cells.n_void` are both NULL on them
  -- and only `n_reasoning` survives, so the draw count comes from the artefact's own
  -- `draws` field and the parsed count is not recorded anywhere. Writing n_draws
  -- into n_parsed would be a defaulted value in a column a view sums.
  n_parsed INTEGER,
  counts_note TEXT,
  ev REAL,                              -- BLAME/CAUSE: the cell mean
  score_pro REAL, score_priv REAL,      -- CMPN: the two parties' means
  sd REAL,
  answer_mass REAL,
  answer_mass_note TEXT NOT NULL,       -- never NULL: why answer_mass is
  n_reasoning INTEGER,
  reasoning_share REAL,
  provider TEXT NOT NULL,
  provider_served TEXT,
  model_id TEXT NOT NULL,
  wire_sha TEXT NOT NULL,
  source TEXT NOT NULL,                 -- main | topup | recovered-from-log |
                                        -- recovered+topped-up
  artefact TEXT NOT NULL,
  artefact_sha TEXT NOT NULL,
  -- ── NEUTRAL #1 EXISTS IN TWO BANKS; BOTH READS ARE KEPT ────────────────────
  bank TEXT NOT NULL,
  preferred INTEGER NOT NULL,           -- 1 = the row the views consume
  duplicate_of TEXT,                    -- the other read of the same text, if any
  status TEXT NOT NULL,                 -- read | unread
  unread_reason TEXT,
  -- ── A CELL READ AFTER ITS RUN, BESIDE THE BANKED ONES ──────────────────────
  -- NULL on every banked cell. On a later reading it holds the date and the
  -- amendment it was read under (Gemini 3.1 Pro, 2026-10-16), so a figure that
  -- moved because a model gained cells can always be traced to the reading.
  read_later TEXT,
  CHECK (status IN ('read', 'unread')),
  CHECK (status = 'read' OR unread_reason IS NOT NULL),
  CHECK (status = 'unread' OR ev IS NOT NULL OR score_pro IS NOT NULL),
  CHECK (n_parsed IS NOT NULL OR counts_note IS NOT NULL),
  CHECK (preferred IN (0, 1)));
CREATE INDEX duty_cells_apc ON duty_cells(arm, pair_id, condition);

CREATE TABLE duty_draws(
  cell_id TEXT NOT NULL REFERENCES duty_cells(cell_id),
  value_index INTEGER NOT NULL,         -- position among the PARSED draws, which is
                                        -- what analyse_duty_pairs.py's zip() pairs
  value REAL,                           -- BLAME/CAUSE: the parsed digit
  gap REAL,                             -- CMPN: score_pro - score_priv for that draw
  PRIMARY KEY(cell_id, value_index));

CREATE TABLE duty_model_arm(
  model_id TEXT NOT NULL,
  arm TEXT NOT NULL,
  config_set TEXT NOT NULL,             -- off | on
  PRIMARY KEY(model_id, config_set),
  CHECK (config_set IN ('off', 'on')));

-- ── THE ARTEFACTS THIS BUILD ACTUALLY INGESTED ────────────────────────────────
-- The build's own test used to re-glob records/ and compare against duty_cells, and a
-- read that finished BETWEEN the ingest's glob and the test's glob failed the build:
-- haiku_r's duty_remedies v2 leg landed 30 cells mid-build and the test reported 1970 of
-- 2000 against an ingest that had been correct. A file appearing while the database is
-- being built is a FRESHNESS fact, not an ingest defect, and the two have to be
-- reported apart. So the ingest records its own snapshot here, the test verifies every
-- cell of every file IN THE SNAPSHOT (re-hashing each one, so a file that changed
-- mid-build is still caught), and a separate reported test lists artefacts now on disk
-- that this build did not see.
CREATE TABLE duty_artefacts(
  path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, run TEXT NOT NULL,
  bank TEXT NOT NULL, arm TEXT NOT NULL, n_cells INTEGER NOT NULL,
  glob_pattern TEXT NOT NULL);

CREATE TABLE duty_coverage(
  run TEXT NOT NULL, arm TEXT NOT NULL,
  cells_expected INTEGER NOT NULL, cells_present INTEGER NOT NULL,
  cells_read INTEGER NOT NULL, cells_unread INTEGER NOT NULL,
  artefact TEXT, absent_reason TEXT,
  PRIMARY KEY(run, arm));
"""

# ──────────────────────────────────────────────────────────────────────────────
# THE VIEWS. Every one carries its denominator columns.
# ──────────────────────────────────────────────────────────────────────────────
VIEWS = {
 # ── THE PROVIDER GUARD, WHICH EVERY REPORTED VIEW GOES THROUGH ────────────────
 # A contrast is (run, arm, pair): the share divides that arm's separate gap by its
 # stated gap, the remedy effect differences its own conditions. If two providers
 # served one of those groups the difference is part model and part routing, and no
 # amount of care downstream can separate them.
 "duty_provider_span": """
    CREATE VIEW duty_provider_span AS
        SELECT run, arm, pair_id,
               COUNT(DISTINCT provider) AS n_providers,
               GROUP_CONCAT(DISTINCT provider) AS providers,
               COUNT(DISTINCT model_id) AS n_models,
               COUNT(*) AS n_cells
        FROM duty_cells
        WHERE status = 'read' AND preferred = 1
        GROUP BY run, arm, pair_id
 """,
 "duty_reported": """
    CREATE VIEW duty_reported AS
        SELECT c.*, p.name AS pair_name, p.status AS pair_status,
               p.pro_label, p.priv_label, p.victim_chose_arrangement,
               s.n_providers, s.providers
        FROM duty_cells c
        JOIN duty_pairs p ON p.pair_id = c.pair_id
        JOIN duty_provider_span s ON s.run = c.run AND s.arm = c.arm
                                 AND s.pair_id = c.pair_id
        WHERE p.status = 'reported' AND c.status = 'read' AND c.preferred = 1
          AND s.n_providers = 1 AND s.n_models = 1
 """,
 # the control is APPARATUS, not a reported pair: it is how the draw floor is
 # measured. It has its own accessor so that no export reaches past duty_reported.
 "duty_control": """
    CREATE VIEW duty_control AS
        SELECT c.* FROM duty_cells c JOIN duty_pairs p ON p.pair_id = c.pair_id
        WHERE p.status = 'control' AND c.status = 'read' AND c.preferred = 1
 """,
 # ── 1. THE STATED GAP, PER ORDER AND AS THE TWO-ORDER MEAN ────────────────────
 # Two side-by-side prompts exist for prawns: the banked SUMMARY prompt (duty_chef_home_comparison/deployed_added_models,
 # cmp_pro_first / cmp_priv_first) and, from the v1.1 fill (completeness_fill), one that sets out
 # the two separate cases IN FULL (cmp_full_*). completeness_fill_amendment H4 ruling 2
 # (the author, 2026-10-17): for prawns the FULL TEXT IS PRIMARY, and where it is not read
 # with both orders (void under the 10% rule, deferred, provider gone) the stated gap is
 # MISSING. It never falls back to the summary, because a pooled figure would then mix
 # two definitions across arms. The summary stays as the original record, in
 # `duty_stated_gap_summary`, and the same-session re-read of it (cmp_reread_*) is a
 # third condition that no stated-gap view reads (see duty_prawns_text_comparison).
 # Every pair but prawns has only the summary form, and its stated gap is that.
 "duty_stated_gap_summary": """
    CREATE VIEW duty_stated_gap_summary AS
        SELECT run, arm, pair_id, pair_name,
               MAX(CASE WHEN condition = 'cmp_pro_first'
                        THEN score_pro - score_priv END) AS gap_pro_first,
               MAX(CASE WHEN condition = 'cmp_priv_first'
                        THEN score_pro - score_priv END) AS gap_priv_first,
               AVG(score_pro - score_priv) AS stated_gap,
               MAX(score_pro - score_priv) - MIN(score_pro - score_priv)
                   AS order_spread,
               COUNT(*) AS n_orders,
               SUM(n_parsed) AS n_draws_parsed, SUM(n_draws) AS n_draws_asked,
               CASE WHEN MIN(ABS(score_pro - score_priv)) = 0.0 THEN 1 ELSE 0 END
                   AS exact_zero_in_an_order,
               CASE WHEN MAX(score_pro - score_priv) > 0
                     AND MIN(score_pro - score_priv) < 0 THEN 1 ELSE 0 END
                   AS sign_differs_across_orders
        FROM duty_reported WHERE question = 'CMPN'
          AND condition IN ('cmp_pro_first', 'cmp_priv_first')
        GROUP BY run, arm, pair_id, pair_name
 """,
 # both orders or no gap: a one-order mean is not the two-order quantity
 "duty_stated_gap_full": """
    CREATE VIEW duty_stated_gap_full AS
        SELECT run, arm, pair_id, pair_name,
               MAX(CASE WHEN condition = 'cmp_full_pro_first'
                        THEN score_pro - score_priv END) AS gap_pro_first,
               MAX(CASE WHEN condition = 'cmp_full_priv_first'
                        THEN score_pro - score_priv END) AS gap_priv_first,
               CASE WHEN COUNT(*) = 2 THEN AVG(score_pro - score_priv) END
                   AS stated_gap,
               CASE WHEN COUNT(*) = 2 THEN MAX(score_pro - score_priv)
                                           - MIN(score_pro - score_priv) END
                   AS order_spread,
               COUNT(*) AS n_orders,
               SUM(n_parsed) AS n_draws_parsed, SUM(n_draws) AS n_draws_asked,
               CASE WHEN COUNT(*) < 2 THEN NULL
                    WHEN MIN(ABS(score_pro - score_priv)) = 0.0 THEN 1 ELSE 0 END
                   AS exact_zero_in_an_order,
               CASE WHEN COUNT(*) < 2 THEN NULL
                    WHEN MAX(score_pro - score_priv) > 0
                     AND MIN(score_pro - score_priv) < 0 THEN 1 ELSE 0 END
                   AS sign_differs_across_orders
        FROM duty_reported WHERE question = 'CMPN'
          AND condition IN ('cmp_full_pro_first', 'cmp_full_priv_first')
        GROUP BY run, arm, pair_id, pair_name
 """,
 "duty_stated_gap": """
    CREATE VIEW duty_stated_gap AS
        SELECT f.*, 'full_text' AS stated_prompt FROM duty_stated_gap_full f
         WHERE f.pair_id = 'prawns'
        UNION ALL
        SELECT s.*, 'summary' AS stated_prompt FROM duty_stated_gap_summary s
         WHERE s.pair_id <> 'prawns'
 """,
 # ── H4 RULING 3: THE FULL TEXT AGAINST THE SUMMARY, LIKE FOR LIKE ─────────────
 # Per arm: the full-text stated gap minus the SAME-SESSION summary re-read, beside the
 # full text minus the BANKED summary, each judged against sqrt(2) x the arm's draw
 # floor (a difference of two readings each carrying one draw floor of noise). No
 # prediction of size or direction is registered (amendment §4).
 "duty_prawns_text_comparison": """
    CREATE VIEW duty_prawns_text_comparison AS
        WITH rr AS (
          SELECT arm,
                 MAX(CASE WHEN condition = 'cmp_reread_pro_first'
                          THEN score_pro - score_priv END) AS gap_pro_first,
                 MAX(CASE WHEN condition = 'cmp_reread_priv_first'
                          THEN score_pro - score_priv END) AS gap_priv_first,
                 CASE WHEN COUNT(*) = 2 THEN AVG(score_pro - score_priv) END AS gap,
                 COUNT(*) AS n_orders
          FROM duty_reported WHERE pair_id = 'prawns' AND question = 'CMPN'
            AND condition IN ('cmp_reread_pro_first', 'cmp_reread_priv_first')
          GROUP BY arm),
        arms AS (SELECT DISTINCT arm FROM duty_cells WHERE pair_id = 'prawns'
                   AND question = 'CMPN')
        SELECT a.arm, f.stated_gap AS full_text_gap, f.n_orders AS full_text_orders,
               rr.gap AS summary_same_session_gap, rr.n_orders AS reread_orders,
               bs.stated_gap AS summary_banked_gap, bs.run AS summary_banked_run,
               fd.draw_floor, SQRT(2.0) * fd.draw_floor AS threshold,
               f.stated_gap - rr.gap AS full_minus_same_session,
               f.stated_gap - bs.stated_gap AS full_minus_banked,
               CASE WHEN f.stated_gap IS NULL OR rr.gap IS NULL OR fd.draw_floor IS NULL
                      THEN NULL
                    WHEN ABS(f.stated_gap - rr.gap) > SQRT(2.0) * fd.draw_floor
                      THEN 'BEYOND' ELSE 'WITHIN' END AS same_session_verdict,
               CASE WHEN f.stated_gap IS NULL OR bs.stated_gap IS NULL
                      OR fd.draw_floor IS NULL THEN NULL
                    WHEN ABS(f.stated_gap - bs.stated_gap) > SQRT(2.0) * fd.draw_floor
                      THEN 'BEYOND' ELSE 'WITHIN' END AS banked_verdict,
               CASE WHEN f.stated_gap IS NULL THEN COALESCE(
                      (SELECT MIN(u.unread_reason) FROM duty_cells u
                        WHERE u.arm = a.arm AND u.pair_id = 'prawns'
                          AND u.condition LIKE 'cmp_full_%' AND u.status = 'unread'),
                      'no full-text cell')
                    WHEN rr.gap IS NULL THEN COALESCE(
                      (SELECT MIN(u.unread_reason) FROM duty_cells u
                        WHERE u.arm = a.arm AND u.pair_id = 'prawns'
                          AND u.condition LIKE 'cmp_reread_%' AND u.status = 'unread'),
                      'no same-session summary cell')
                    WHEN fd.draw_floor IS NULL THEN 'no draw floor on this arm'
                    END AS missing_reason
        FROM arms a
        LEFT JOIN duty_stated_gap_full f ON f.arm = a.arm AND f.pair_id = 'prawns'
        LEFT JOIN rr ON rr.arm = a.arm
        LEFT JOIN duty_stated_gap_summary bs ON bs.arm = a.arm AND bs.pair_id = 'prawns'
        LEFT JOIN duty_floor_draw fd ON fd.arm = a.arm
 """,
 # ── 2. THE SEPARATE GAP, AND THE HEADROOM THAT BOUNDS IT ──────────────────────
 "duty_separate_gap": """
    CREATE VIEW duty_separate_gap AS
        SELECT run, arm, pair_id, pair_name,
               MAX(CASE WHEN leg = 'pro' THEN ev END) AS ev_pro,
               MAX(CASE WHEN leg = 'priv' THEN ev END) AS ev_priv,
               MAX(CASE WHEN leg = 'pro' THEN ev END)
                 - MAX(CASE WHEN leg = 'priv' THEN ev END) AS separate_gap,
               9.0 - MAX(CASE WHEN leg = 'pro' THEN ev END) AS headroom_above_pro,
               COUNT(*) AS n_legs,
               SUM(n_parsed) AS n_draws_parsed, SUM(n_draws) AS n_draws_asked
        FROM duty_reported
        WHERE question = 'BLAME' AND condition = 'bare'
        GROUP BY run, arm, pair_id, pair_name
        HAVING COUNT(*) = 2
 """,
 # ── 3. THE FLOORS, PER ARM ────────────────────────────────────────────────────
 # DRAW floor: 2.33 x sd of the control's gaps, pooling its 20 comparison gaps with
 # its 10 separate gaps paired draw by draw, then floored at 0.30. That is duty_pairs's
 # own definition, re-expressed; the sd is two-pass, as Python's pstdev is.
 "duty_control_gaps": """
    CREATE VIEW duty_control_gaps AS
        SELECT c.arm, 'cmpn' AS src, d.value_index, d.gap AS g
        FROM duty_control c JOIN duty_draws d ON d.cell_id = c.cell_id
        WHERE c.question = 'CMPN' AND d.gap IS NOT NULL
        UNION ALL
        SELECT pr.arm, 'separate' AS src, dp.value_index,
               dp.value - dv.value AS g
        FROM duty_control pr
        JOIN duty_draws dp ON dp.cell_id = pr.cell_id
        JOIN duty_control pv ON pv.arm = pr.arm AND pv.question = 'BLAME'
                            AND pv.leg = 'priv'
        JOIN duty_draws dv ON dv.cell_id = pv.cell_id
                          AND dv.value_index = dp.value_index
        WHERE pr.question = 'BLAME' AND pr.leg = 'pro'
 """,
 "duty_floor_draw": """
    CREATE VIEW duty_floor_draw AS
        SELECT g.arm, COUNT(*) AS n,
               SUM(CASE WHEN g.src = 'cmpn' THEN 1 ELSE 0 END) AS n_cmpn,
               SUM(CASE WHEN g.src = 'separate' THEN 1 ELSE 0 END) AS n_separate,
               m.mg AS mean_gap,
               CASE WHEN COUNT(*) >= 2
                    THEN SQRT(MAX(SUM((g.g - m.mg) * (g.g - m.mg)) / COUNT(*), 0.0))
               END AS sd,
               CASE WHEN COUNT(*) >= 2
                    THEN MAX(2.33 * SQRT(MAX(SUM((g.g - m.mg) * (g.g - m.mg))
                                             / COUNT(*), 0.0)), 0.30)
               END AS draw_floor,
               CASE WHEN COUNT(*) >= 2 THEN NULL
                    ELSE 'fewer than two control gaps: the control pair is unread'
                         || ' on this arm' END AS refused_reason
        FROM duty_control_gaps g
        JOIN (SELECT arm, AVG(g) AS mg FROM duty_control_gaps GROUP BY arm) m
          ON m.arm = g.arm
        GROUP BY g.arm, m.mg
 """,
 # ── 4. THE NEUTRAL BASELINE: THE MEAN OVER THREE SENTENCES, OR REFUSED ────────
 "duty_neutral_gap": """
    CREATE VIEW duty_neutral_gap AS
        SELECT run, arm, pair_id, pair_name, condition,
               MAX(CASE WHEN leg = 'pro' THEN ev END)
                 - MAX(CASE WHEN leg = 'priv' THEN ev END) AS gap,
               COUNT(*) AS n_legs
        FROM duty_reported
        WHERE question = 'BLAME' AND condition LIKE 'neutral_%'
        GROUP BY run, arm, pair_id, pair_name, condition
        HAVING COUNT(*) = 2
 """,
 "duty_neutral_baseline": """
    CREATE VIEW duty_neutral_baseline AS
        SELECT run, arm, pair_id, pair_name,
               COUNT(*) AS n_neutrals,
               CASE WHEN COUNT(*) = 3 THEN AVG(gap) END AS neutral_baseline,
               CASE WHEN COUNT(*) = 3 THEN MAX(gap) - MIN(gap) END AS neutral_spread,
               CASE WHEN COUNT(*) = 3 THEN NULL
                    ELSE 'only ' || COUNT(*) || ' of 3 neutral sentences read; '
                         || 'Amendment 2 defines the baseline as the mean of three'
               END AS refused_reason
        FROM duty_neutral_gap
        GROUP BY run, arm, pair_id, pair_name
 """,
 # SENTENCE-NOISE floor: 2.33 x sd of the arm's neutral DEVIATIONS from that pair's
 # own bare separate gap, over the reported pairs only, and only over pairs with all
 # three neutrals. A fragment of a three-part control is not a control.
 "duty_neutral_deviation": """
    CREATE VIEW duty_neutral_deviation AS
        SELECT n.arm, n.pair_id, n.condition, n.gap - s.separate_gap AS dev
        FROM duty_neutral_gap n
        JOIN duty_neutral_baseline b ON b.arm = n.arm AND b.pair_id = n.pair_id
                                    AND b.n_neutrals = 3
        JOIN duty_separate_gap s ON s.arm = n.arm AND s.pair_id = n.pair_id
        WHERE s.separate_gap IS NOT NULL
 """,
 # ── THE SENTENCE FLOOR IS COMPUTED ON TWO PAIR SETS, NOT ONE ─────────────────
 # `all_reported` pools every reported pair including hair dye, which is duty_hair_dye §5's
 # definition and what the current analyses use. `r227_only` restricts to the four
 # pairs duty_remedies had, which is the definition its banked classes were computed under.
 # Keeping BOTH is what lets the build assert that the views reproduce duty_remedies's
 # figures exactly instead of nearly: a floor that gained a fifth pair's deviations is
 # a different floor, and comparing across that difference would make a correct view
 # look wrong.
 "duty_floor_sets": """
    CREATE VIEW duty_floor_sets AS
        SELECT 'all_reported' AS floor_set, arm, pair_id, condition, dev
        FROM duty_neutral_deviation
        UNION ALL
        SELECT 'r227_only' AS floor_set, arm, pair_id, condition, dev
        FROM duty_neutral_deviation WHERE pair_id IN ('1', '3', '4', '5')
 """,
 "duty_floor_sentence": """
    CREATE VIEW duty_floor_sentence AS
        SELECT d.floor_set, d.arm, COUNT(*) AS n,
               COUNT(DISTINCT d.pair_id) AS n_pairs,
               CASE WHEN COUNT(*) >= 3
                    THEN 2.33 * SQRT(MAX(SUM((d.dev - m.md) * (d.dev - m.md))
                                         / COUNT(*), 0.0))
               END AS sentence_floor_parametric,
               CASE WHEN COUNT(*) >= 3 THEN NULL
                    ELSE 'fewer than three neutral deviations on this pair set'
               END AS refused_reason
        FROM duty_floor_sets d
        JOIN (SELECT floor_set, arm, AVG(dev) AS md FROM duty_floor_sets
               GROUP BY floor_set, arm) m
          ON m.floor_set = d.floor_set AND m.arm = d.arm
        GROUP BY d.floor_set, d.arm, m.md
 """,
 "duty_dev_ranked": """
    CREATE VIEW duty_dev_ranked AS
        SELECT floor_set, arm, dev,
               ROW_NUMBER() OVER (PARTITION BY floor_set, arm ORDER BY dev) - 1 AS i,
               COUNT(*) OVER (PARTITION BY floor_set, arm) AS n
        FROM duty_floor_sets
 """,
 "duty_floor": """
    CREATE VIEW duty_floor AS
        WITH q AS (
          SELECT floor_set, arm, n, (n - 1) * 0.25 AS p1, (n - 1) * 0.75 AS p3
          FROM duty_dev_ranked GROUP BY floor_set, arm, n),
        iq AS (
          SELECT q.floor_set, q.arm, q.n,
                 (SELECT dev FROM duty_dev_ranked r
                   WHERE r.floor_set = q.floor_set AND r.arm = q.arm
                     AND r.i = CAST(q.p1 AS INTEGER))
                 + (q.p1 - CAST(q.p1 AS INTEGER))
                   * (COALESCE((SELECT dev FROM duty_dev_ranked r
                                 WHERE r.floor_set = q.floor_set AND r.arm = q.arm
                                   AND r.i = CAST(q.p1 AS INTEGER) + 1),
                               (SELECT dev FROM duty_dev_ranked r
                                 WHERE r.floor_set = q.floor_set AND r.arm = q.arm
                                   AND r.i = CAST(q.p1 AS INTEGER)))
                      - (SELECT dev FROM duty_dev_ranked r
                          WHERE r.floor_set = q.floor_set AND r.arm = q.arm
                            AND r.i = CAST(q.p1 AS INTEGER))) AS q1,
                 (SELECT dev FROM duty_dev_ranked r
                   WHERE r.floor_set = q.floor_set AND r.arm = q.arm
                     AND r.i = CAST(q.p3 AS INTEGER))
                 + (q.p3 - CAST(q.p3 AS INTEGER))
                   * (COALESCE((SELECT dev FROM duty_dev_ranked r
                                 WHERE r.floor_set = q.floor_set AND r.arm = q.arm
                                   AND r.i = CAST(q.p3 AS INTEGER) + 1),
                               (SELECT dev FROM duty_dev_ranked r
                                 WHERE r.floor_set = q.floor_set AND r.arm = q.arm
                                   AND r.i = CAST(q.p3 AS INTEGER)))
                      - (SELECT dev FROM duty_dev_ranked r
                          WHERE r.floor_set = q.floor_set AND r.arm = q.arm
                            AND r.i = CAST(q.p3 AS INTEGER))) AS q3
          FROM q)
        SELECT fs.floor_set, fs.arm,
               fd.draw_floor, fd.sd AS draw_sd, fd.n AS draw_n,
               fd.n_cmpn AS draw_n_cmpn, fd.n_separate AS draw_n_separate,
               fd.refused_reason AS draw_refused_reason,
               fs.sentence_floor_parametric, fs.n AS sentence_n,
               fs.n_pairs AS sentence_n_pairs,
               CASE WHEN iq.n >= 3 THEN 2.33 * (iq.q3 - iq.q1) / 1.349 END
                   AS sentence_floor_robust,
               iq.q1 AS dev_q1, iq.q3 AS dev_q3,
               fs.refused_reason AS sentence_refused_reason,
               CASE WHEN fs.sentence_floor_parametric IS NULL
                      OR iq.n < 3 OR iq.q3 = iq.q1 THEN NULL
                    WHEN fs.sentence_floor_parametric
                         / (2.33 * (iq.q3 - iq.q1) / 1.349) > 1.5
                      OR fs.sentence_floor_parametric
                         / (2.33 * (iq.q3 - iq.q1) / 1.349) < 0.6666666666666666
                    THEN 1 ELSE 0 END AS floors_diverge
        FROM duty_floor_sentence fs
        LEFT JOIN duty_floor_draw fd ON fd.arm = fs.arm
        LEFT JOIN iq ON iq.floor_set = fs.floor_set AND iq.arm = fs.arm
 """,
 # the draw floor alone, for arms with no sentence floor at all: an arm whose
 # neutrals are unread still has a control; duty_floor_used falls back to it.
 "duty_floor_any": """
    CREATE VIEW duty_floor_any AS
        SELECT a.arm, fd.draw_floor, fd.sd AS draw_sd, fd.n AS draw_n,
               fd.refused_reason AS draw_refused_reason
        FROM (SELECT DISTINCT arm FROM duty_cells) a
        LEFT JOIN duty_floor_draw fd ON fd.arm = a.arm
 """,
 # ── 5. THE SHARE: SEPARATE OVER STATED, ONLY ABOVE THE WORDING FLOOR ──────────
 # Withheld where the stated gap does not clear the arm's `floor_used`: the wording
 # floor (max(sentence floor, 0.30)), or the draw band where the arm has no sentence
 # floor. This is the floor duty_fig7, Figures 2 and 7 and Table B.9 use, so the share
 # here and the share there agree cell for cell. It used the draw floor until
 # 2026-10-12, which withheld a different set of 18 cells.
 "duty_share": """
    CREATE VIEW duty_share AS
        SELECT s.run, s.arm, s.pair_id, s.pair_name,
               s.separate_gap, t.stated_gap, f.floor_used, f.floor_used_source,
               CASE WHEN t.stated_gap IS NULL THEN NULL
                    WHEN f.floor_used IS NULL THEN NULL
                    WHEN ABS(t.stated_gap) <= f.floor_used THEN NULL
                    ELSE s.separate_gap / t.stated_gap END AS share,
               CASE WHEN t.stated_gap IS NULL
                      THEN 'the comparison is unread on this arm and pair'
                    WHEN f.floor_used IS NULL
                      THEN 'the arm has no floor: no sentence floor and no draw floor'
                    WHEN ABS(t.stated_gap) <= f.floor_used
                      THEN 'the stated gap ' || ROUND(t.stated_gap, 4)
                           || ' does not clear this arm''s wording floor '
                           || ROUND(f.floor_used, 4)
                    ELSE NULL END AS refused_reason,
               s.n_draws_parsed AS separate_draws,
               t.n_draws_parsed AS stated_draws
        FROM duty_separate_gap s
        LEFT JOIN duty_stated_gap t ON t.arm = s.arm AND t.pair_id = s.pair_id
        LEFT JOIN duty_floor_used f ON f.arm = s.arm
 """,
 # ── 6. THE REMEDY EFFECT, AND THE FOUR-WAY CLASS ──────────────────────────────
 "duty_remedy_gap": """
    CREATE VIEW duty_remedy_gap AS
        SELECT run, arm, pair_id, pair_name, condition,
               MAX(CASE WHEN leg = 'pro' THEN ev END) AS ev_pro,
               MAX(CASE WHEN leg = 'priv' THEN ev END) AS ev_priv,
               MAX(CASE WHEN leg = 'pro' THEN ev END)
                 - MAX(CASE WHEN leg = 'priv' THEN ev END) AS gap,
               COUNT(*) AS n_legs, SUM(n_parsed) AS n_draws_parsed
        FROM duty_reported
        WHERE question = 'BLAME' AND condition IN ('stated', 'comparand')
        GROUP BY run, arm, pair_id, pair_name, condition
        HAVING COUNT(*) = 2
 """,
 "duty_neutral_leg_mean": """
    CREATE VIEW duty_neutral_leg_mean AS
        SELECT arm, pair_id, leg, AVG(ev) AS m, COUNT(*) AS n
        FROM duty_reported
        WHERE question = 'BLAME' AND condition LIKE 'neutral_%'
        GROUP BY arm, pair_id, leg
 """,
 "duty_remedy_effect": """
    CREATE VIEW duty_remedy_effect AS
        SELECT f.floor_set, g.run, g.arm, g.pair_id, g.pair_name,
               g.condition, g.gap, b.neutral_baseline, b.n_neutrals,
               t.stated_gap AS target_gap,
               g.gap - b.neutral_baseline AS effect_digits,
               g.ev_pro - lp.m AS d_pro, g.ev_priv - lv.m AS d_priv,
               f.sentence_floor_parametric AS floor,
               f.sentence_floor_robust AS floor_robust, f.floors_diverge,
               -- the four-way class, on the arm's own stated gap
               CASE
                 WHEN b.neutral_baseline IS NULL OR t.stated_gap IS NULL
                      OR f.sentence_floor_parametric IS NULL THEN NULL
                 WHEN ABS(g.gap - b.neutral_baseline)
                        <= f.sentence_floor_parametric
                  AND ABS(g.gap - t.stated_gap) <= f.sentence_floor_parametric
                   THEN CASE WHEN ABS(g.gap - t.stated_gap)
                                  < ABS(g.gap - b.neutral_baseline) THEN 'AT'
                             WHEN ABS(g.gap - b.neutral_baseline)
                                  < ABS(g.gap - t.stated_gap) THEN 'WITHIN FLOOR'
                             ELSE 'NO VERDICT (equidistant)' END
                 WHEN ABS(g.gap - b.neutral_baseline)
                        <= f.sentence_floor_parametric THEN 'WITHIN FLOOR'
                 WHEN ABS(g.gap - t.stated_gap)
                        <= f.sentence_floor_parametric THEN 'AT'
                 WHEN g.gap > t.stated_gap THEN 'OVER'
                 ELSE 'UNDER' END AS class,
               CASE WHEN b.neutral_baseline IS NULL
                        OR t.stated_gap IS NULL
                        OR f.sentence_floor_parametric IS NULL THEN 1
                    WHEN ABS(g.gap - b.neutral_baseline)
                           <= f.sentence_floor_parametric
                     AND ABS(g.gap - t.stated_gap)
                           <= f.sentence_floor_parametric THEN 1
                    ELSE 0 END AS tie_broken,
               -- LOW RESOLUTION: the floor is wide against the distance the remedy
               -- has to travel, so a class is a weak statement about this arm
               CASE WHEN f.sentence_floor_parametric IS NULL
                        OR t.stated_gap IS NULL
                        OR b.neutral_baseline IS NULL THEN NULL
                    WHEN f.sentence_floor_parametric
                         > ABS(t.stated_gap - b.neutral_baseline) / 2.0
                    THEN 1 ELSE 0 END AS low_resolution,
               -- the recovery ratio exists only where the move clears the floor
               CASE WHEN b.neutral_baseline IS NULL OR t.stated_gap IS NULL
                        OR f.sentence_floor_parametric IS NULL THEN NULL
                    WHEN ABS(t.stated_gap - b.neutral_baseline)
                         <= f.sentence_floor_parametric THEN NULL
                    ELSE (g.gap - b.neutral_baseline)
                         / (t.stated_gap - b.neutral_baseline) END AS recovery,
               -- ── TWO DIFFERENT ABSENCES, AND THE PROSE HAS TO TELL THEM
               --    APART ────────────────────────────────────────────────────
               -- The first version said "this pair has no neutral sentences" for
               -- every missing baseline. True of prawns, whose cases come from the
               -- families bank and which has none; FALSE of qwen235b on gas, where
               -- the pair has three and the ARM served none of them. A correct
               -- numeric refusal carrying a false sentence is the stale-prose defect
               -- this programme has already met twice on pre-assigned branch labels.
               CASE WHEN b.neutral_baseline IS NULL
                      THEN COALESCE(b.refused_reason,
                             CASE WHEN NOT EXISTS (
                                    SELECT 1 FROM duty_texts dt
                                     WHERE dt.pair_id = g.pair_id
                                       AND dt.kind = 'neutral')
                                  THEN 'baseline not read: this pair has no neutral '
                                       || 'sentences, so a remedy class would have '
                                       || 'to borrow another pair''s baseline'
                                  ELSE 'baseline not read: this arm read none of '
                                       || 'this pair''s three neutral sentences'
                             END)
                    WHEN t.stated_gap IS NULL
                      THEN 'the comparison is unread on this arm and pair'
                    WHEN f.sentence_floor_parametric IS NULL
                      THEN COALESCE(f.sentence_refused_reason, 'no sentence floor')
                    WHEN ABS(t.stated_gap - b.neutral_baseline)
                           <= f.sentence_floor_parametric
                      THEN 'the distance from the baseline to the stated gap does'
                           || ' not clear the floor, so a recovery ratio would'
                           || ' divide by noise'
                    ELSE NULL END AS recovery_refused_reason,
               -- does the condition move the PROFESSIONAL up beyond the floor
               CASE WHEN f.sentence_floor_parametric IS NULL THEN NULL
                    WHEN g.ev_pro - lp.m > f.sentence_floor_parametric THEN 1
                    ELSE 0 END AS professional_rises
        FROM duty_remedy_gap g
        LEFT JOIN duty_neutral_baseline b ON b.arm = g.arm AND b.pair_id = g.pair_id
        LEFT JOIN duty_stated_gap t ON t.arm = g.arm AND t.pair_id = g.pair_id
        -- ── THE WORDING FLOOR, FLOORED AT 0.30 AS EVERY OTHER DUTY VERDICT IS ──
        -- The exported set (all_reported) takes max(sentence floor, 0.30), the
        -- floor_used of duty_floor_used, so a remedy class and a Figure 7 verdict are
        -- judged against the same number. r227_only keeps the unfloored value: it
        -- exists to reproduce duty_remedies's banked classes and is never exported.
        JOIN (SELECT floor_set, arm,
                     CASE WHEN floor_set = 'all_reported'
                               AND sentence_floor_parametric IS NOT NULL
                          THEN MAX(sentence_floor_parametric, 0.30)
                          ELSE sentence_floor_parametric END
                       AS sentence_floor_parametric,
                     sentence_floor_robust, floors_diverge, sentence_refused_reason
                FROM duty_floor) f ON f.arm = g.arm
        LEFT JOIN duty_neutral_leg_mean lp ON lp.arm = g.arm
                                          AND lp.pair_id = g.pair_id
                                          AND lp.leg = 'pro'
        LEFT JOIN duty_neutral_leg_mean lv ON lv.arm = g.arm
                                          AND lv.pair_id = g.pair_id
                                          AND lv.leg = 'priv'
 """,
 # ── 7. CAUSE, AND THE DILUTION CHECK ──────────────────────────────────────────
 "duty_cause": """
    CREATE VIEW duty_cause AS
        SELECT c.run, c.arm, c.pair_id, c.pair_name,
               MAX(CASE WHEN c.leg = 'pro' THEN c.ev END) AS cause_pro,
               MAX(CASE WHEN c.leg = 'priv' THEN c.ev END) AS cause_priv,
               (MAX(CASE WHEN c.leg = 'pro' THEN c.ev END)
                + MAX(CASE WHEN c.leg = 'priv' THEN c.ev END)) / 2.0 AS cause_mean,
               COUNT(*) AS n_legs, SUM(c.n_parsed) AS n_draws_parsed
        FROM duty_reported c
        WHERE c.question = 'CAUSE'
        GROUP BY c.run, c.arm, c.pair_id, c.pair_name
        HAVING COUNT(*) = 2
 """,
 "duty_cause_deviation": """
    CREATE VIEW duty_cause_deviation AS
        SELECT a.arm, a.pair_id, a.pair_name, a.cause_mean,
               (SELECT COUNT(*) FROM duty_cause o
                 WHERE o.arm = a.arm AND o.pair_id <> a.pair_id) AS n_other_pairs,
               -- the median over the OTHER pairs on this arm, by linear
               -- interpolation at the midpoint, as statistics.median does
               (SELECT AVG(cause_mean) FROM (
                   SELECT o.cause_mean,
                          ROW_NUMBER() OVER (ORDER BY o.cause_mean) - 1 AS i,
                          (SELECT COUNT(*) FROM duty_cause o2
                            WHERE o2.arm = a.arm AND o2.pair_id <> a.pair_id) AS n
                   FROM duty_cause o
                   WHERE o.arm = a.arm AND o.pair_id <> a.pair_id)
                 WHERE i IN ((n - 1) / 2, n / 2)) AS others_median
        FROM duty_cause a
 """,
 # ── 8. THE SPREAD ACROSS MODELS, ONE ARM PER MODEL ────────────────────────────
 "duty_spread_vals": """
    CREATE VIEW duty_spread_vals AS
        SELECT m.config_set, g.pair_id, g.pair_name, m.model_id, g.arm,
               g.stated_gap AS gap, g.exact_zero_in_an_order
        FROM duty_stated_gap g
        JOIN duty_model_arm m ON m.arm = g.arm
        WHERE g.stated_gap IS NOT NULL
 """,
 "duty_spread_ranked": """
    CREATE VIEW duty_spread_ranked AS
        SELECT config_set, pair_id, gap,
               ROW_NUMBER() OVER (PARTITION BY config_set, pair_id
                                  ORDER BY gap) - 1 AS i,
               COUNT(*) OVER (PARTITION BY config_set, pair_id) AS n
        FROM duty_spread_vals
 """,
 "duty_spread": """
    CREATE VIEW duty_spread AS
        WITH q AS (
          SELECT config_set, pair_id, n,
                 (n - 1) * 0.25 AS p1, (n - 1) * 0.75 AS p3
          FROM duty_spread_ranked GROUP BY config_set, pair_id, n),
        iq AS (
          SELECT q.config_set, q.pair_id, q.n,
                 (SELECT gap FROM duty_spread_ranked r
                   WHERE r.config_set = q.config_set AND r.pair_id = q.pair_id
                     AND r.i = CAST(q.p1 AS INTEGER))
                 + (q.p1 - CAST(q.p1 AS INTEGER))
                   * (COALESCE((SELECT gap FROM duty_spread_ranked r
                                 WHERE r.config_set = q.config_set
                                   AND r.pair_id = q.pair_id
                                   AND r.i = CAST(q.p1 AS INTEGER) + 1),
                               (SELECT gap FROM duty_spread_ranked r
                                 WHERE r.config_set = q.config_set
                                   AND r.pair_id = q.pair_id
                                   AND r.i = CAST(q.p1 AS INTEGER)))
                      - (SELECT gap FROM duty_spread_ranked r
                          WHERE r.config_set = q.config_set
                            AND r.pair_id = q.pair_id
                            AND r.i = CAST(q.p1 AS INTEGER))) AS q1,
                 (SELECT gap FROM duty_spread_ranked r
                   WHERE r.config_set = q.config_set AND r.pair_id = q.pair_id
                     AND r.i = CAST(q.p3 AS INTEGER))
                 + (q.p3 - CAST(q.p3 AS INTEGER))
                   * (COALESCE((SELECT gap FROM duty_spread_ranked r
                                 WHERE r.config_set = q.config_set
                                   AND r.pair_id = q.pair_id
                                   AND r.i = CAST(q.p3 AS INTEGER) + 1),
                               (SELECT gap FROM duty_spread_ranked r
                                 WHERE r.config_set = q.config_set
                                   AND r.pair_id = q.pair_id
                                   AND r.i = CAST(q.p3 AS INTEGER)))
                      - (SELECT gap FROM duty_spread_ranked r
                          WHERE r.config_set = q.config_set
                            AND r.pair_id = q.pair_id
                            AND r.i = CAST(q.p3 AS INTEGER))) AS q3
          FROM q)
        SELECT v.config_set, v.pair_id, v.pair_name,
               COUNT(*) AS n_models, AVG(v.gap) AS mean_gap,
               -- ── SAMPLE sd HERE, POPULATION sd FOR THE FLOORS, DELIBERATELY ────
               -- A floor is a property of ONE arm's own draws and is a population
               -- quantity; a spread ACROSS models is a sample of the model
               -- population, and `statistics.stdev` is what banked
               -- dispersion.json. Using the population form here differed from
               -- every banked figure by a factor of sqrt(n/(n-1)) -- 3.8% at n=14 --
               -- which is small enough to look like rounding and is not.
               CASE WHEN COUNT(*) >= 2
                    THEN SQRT(MAX(SUM((v.gap - mm.m) * (v.gap - mm.m))
                                  / (COUNT(*) - 1), 0.0)) END AS sd,
               -- CV IS BLANK ON A NEAR-ZERO MEAN. An earlier run settled this on this
               -- programme's own data: a ratio to a denominator near zero is an
               -- artefact of the denominator.
               CASE WHEN ABS(mm.m) >= 0.05 AND COUNT(*) >= 2
                    THEN SQRT(MAX(SUM((v.gap - mm.m) * (v.gap - mm.m))
                                  / (COUNT(*) - 1), 0.0)) / mm.m END AS cv,
               CASE WHEN ABS(mm.m) < 0.05
                    THEN 'mean within 0.05 of zero: a CV would be an artefact of'
                         || ' the denominator' END AS cv_refused_reason,
               iq.q3 - iq.q1 AS iqr, iq.q1, iq.q3,
               MIN(v.gap) AS min_gap, MAX(v.gap) AS max_gap,
               SUM(v.exact_zero_in_an_order) AS n_exact_zero_flagged
        FROM duty_spread_vals v
        JOIN (SELECT config_set, pair_id, AVG(gap) AS m
                FROM duty_spread_vals GROUP BY config_set, pair_id) mm
          ON mm.config_set = v.config_set AND mm.pair_id = v.pair_id
        LEFT JOIN iq ON iq.config_set = v.config_set AND iq.pair_id = v.pair_id
        GROUP BY v.config_set, v.pair_id, v.pair_name, mm.m, iq.q1, iq.q3
 """,
 # ── FIGURE 7: THE ARM ROWS, THE FLOOR IT IS JUDGED AGAINST, AND THE VERDICT ───
 # Figure 6's arm set is derived the way build_chef_home.py derives it -- from what is
 # PRESENT rather than from a list of names -- so the two figures cannot come to hold
 # different arms. `deepseek_r_mt8192` is dropped because it is the same model as
 # `deepseek_r` under the name its families read was banked under.
 "duty_fig6_arms": """
    CREATE VIEW duty_fig6_arms AS
        WITH armset AS (
          SELECT a.arm FROM cells c JOIN artefacts a ON a.id = c.artefact_id
          WHERE a.card = 'api' GROUP BY a.arm
          -- ── A COMPLETE SCENARIO PAIR, OR A SIDE-BY-SIDE. NOT "SOME PRAWNS
          --    CELLS". ──────────────────────────────────────────────────────
          -- build_chef_home.py reaches the same 22 arms but excludes `gemini_topup`
          -- BY NAME, with the reason that it is a top-up read rather than a full arm.
          -- The structural fact behind that name is checkable: it holds no CARELESS
          -- role on either prawns scenario, only N and I. So the predicate asks for
          -- the careless role on BOTH scenarios -- which is exactly what the separate
          -- gap is computed from -- or a side-by-side. Same 22 arms, derived from
          -- what an arm lacks rather than from a list of exceptions.
          HAVING (SUM(CASE WHEN c.family = 'prawns_home' AND c.role = 'C'
                            AND c.question = 'BLAME' THEN 1 ELSE 0 END) > 0
              AND SUM(CASE WHEN c.family = 'prawns_restaurant' AND c.role = 'C'
                            AND c.question = 'BLAME' THEN 1 ELSE 0 END) > 0)
              OR (SELECT COUNT(*) FROM cells c2
                   JOIN artefacts a2 ON a2.id = c2.artefact_id
                   WHERE a2.arm = a.arm AND a2.run = 'duty_chef_home_comparison'
                     AND c2.question = 'CMPN') > 0),
        arms AS (SELECT arm FROM armset WHERE arm <> 'deepseek_r_mt8192'),
        -- the WIRE's reasoning configuration, asserted unambiguous per arm
        rc AS (SELECT a.arm, MIN(c.reasoning_configured) AS lo,
                      MAX(c.reasoning_configured) AS hi
               FROM cells c JOIN artefacts a ON a.id = c.artefact_id
               WHERE c.reasoning_configured IS NOT NULL GROUP BY a.arm),
        -- and the DRAWS, for an arm read on a pass that recorded no reasoning field.
        -- gemini_pro is the case: 39 of its 40 draws reasoned and no wire field
        -- exists, so "not resolved" would be true of the log and false of the
        -- question. The source is carried beside the answer, never merged into it.
        dr AS (SELECT a.arm, SUM(c.n_reasoning) AS nr, SUM(c.n_draws) AS nd
               FROM cells c JOIN artefacts a ON a.id = c.artefact_id
               WHERE c.n_reasoning IS NOT NULL GROUP BY a.arm),
        res AS (
          SELECT x.arm,
                 CASE WHEN rc.lo IS NOT NULL AND rc.lo = rc.hi THEN rc.lo
                      WHEN dr.nr > 0 THEN 'on'
                      WHEN dr.nd > 0 THEN 'off' END AS reasoning,
                 CASE WHEN rc.lo IS NOT NULL AND rc.lo = rc.hi
                        THEN 'reasoning_configured on the wire'
                      WHEN dr.nr > 0
                        THEN 'from the draws (' || dr.nr || ' of ' || dr.nd
                             || ' reasoned); no reasoning field on the wire'
                      WHEN dr.nd > 0
                        THEN 'from the draws (0 of ' || dr.nd
                             || ' reasoned); no reasoning field on the wire'
                      END AS reasoning_source,
                 CASE WHEN rc.lo IS NOT NULL AND rc.lo <> rc.hi THEN 1 ELSE 0 END
                   AS reasoning_ambiguous
          FROM arms x LEFT JOIN rc ON rc.arm = x.arm LEFT JOIN dr ON dr.arm = x.arm)
        SELECT res.arm,
               (SELECT model_id FROM artefacts WHERE arm = res.arm
                 AND model_id IS NOT NULL ORDER BY id LIMIT 1) AS model_label,
               res.reasoning, res.reasoning_source, res.reasoning_ambiguous,
               CASE WHEN res.reasoning = 'on' THEN 2 ELSE 1 END AS group_order,
               ROW_NUMBER() OVER (
                 PARTITION BY CASE WHEN res.reasoning = 'on' THEN 2 ELSE 1 END
                 ORDER BY res.arm) AS row_order
        FROM res
 """,
 # THE FLOOR FIGURE 7 JUDGES AGAINST, with its provenance on the row.
 # max(sentence floor, 0.30); the draw band where an arm has no sentence floor at all,
 # labelled so a reader never has to work out which quantity a verdict used.
 "duty_floor_used": """
    CREATE VIEW duty_floor_used AS
        SELECT a.arm, a.draw_floor AS floor_draw,
               f.sentence_floor_parametric AS floor_sentence,
               f.sentence_floor_robust AS floor_sentence_robust,
               f.sentence_n, f.floors_diverge,
               CASE WHEN f.sentence_floor_parametric IS NOT NULL
                      THEN MAX(f.sentence_floor_parametric, 0.30)
                    ELSE a.draw_floor END AS floor_used,
               CASE WHEN f.sentence_floor_parametric IS NOT NULL
                      THEN 'sentence floor (all_reported pair set), floored at 0.30'
                    WHEN a.draw_floor IS NOT NULL
                      THEN 'DRAW BAND: this arm has no sentence floor ('
                           || COALESCE(f.sentence_refused_reason,
                                       'no neutral readings') || ')'
                    ELSE NULL END AS floor_used_source
        FROM duty_floor_any a
        LEFT JOIN duty_floor f ON f.arm = a.arm AND f.floor_set = 'all_reported'
 """,
 # ── THE FIGURE-7 ROW ITSELF: ONE PER ARM x PAIR, READ OR MISSING WITH A REASON ─
 "duty_fig7": """
    CREATE VIEW duty_fig7 AS
        SELECT m.arm, m.model_label, m.reasoning, m.reasoning_source,
               m.group_order, m.row_order,
               p.pair_id, p.name AS pair_label,
               CASE p.pair_id WHEN 'prawns' THEN 1 WHEN '1' THEN 2 WHEN '3' THEN 3
                              WHEN '4' THEN 4 WHEN '5' THEN 5 WHEN '7' THEN 6 END
                 AS panel_order,
               t.gap_pro_first AS stated_gap_pro_first,
               t.gap_priv_first AS stated_gap_priv_first,
               t.stated_gap, t.order_spread, t.exact_zero_in_an_order AS exact_zero_flag,
               t.n_orders,
               s.ev_pro AS sep_pro, s.ev_priv AS sep_priv, s.separate_gap,
               s.headroom_above_pro,
               -- ── THE SEPARATE GAP WITH THE CONVENTION STATED ──────────────
               -- duty_remedies and duty_hair_dye read it for the five authored pairs; duty_prawns_convention reads
               -- it for prawns. RAW digits, professional minus private, never divided
               -- by anything: the prawns pair has no neutral baseline, so a figure
               -- that normalised this column could not carry prawns at all.
               sc.ev_pro AS stated_condition_pro,
               sc.ev_priv AS stated_condition_priv,
               sc.gap AS stated_condition_gap,
               sc.run AS stated_condition_run,
               CASE WHEN sc.gap IS NOT NULL THEN 'read' ELSE 'missing' END
                 AS stated_condition_status,
               CASE WHEN sc.gap IS NOT NULL THEN NULL
                    ELSE COALESCE(
                      (SELECT 'unread: ' || MIN(u.unread_reason) FROM duty_cells u
                        WHERE u.arm = m.arm AND u.pair_id = p.pair_id
                          AND u.condition = 'stated' AND u.status = 'unread'),
                      'no stated-condition cell exists for this arm and pair')
                    END AS stated_condition_reason,
               fu.floor_draw, fu.floor_sentence, fu.floor_used, fu.floor_used_source,
               CASE WHEN t.stated_gap IS NULL OR fu.floor_used IS NULL THEN NULL
                    WHEN ABS(t.stated_gap) > fu.floor_used THEN 1 ELSE 0 END
                 AS convention_stated,
               CASE
                 WHEN t.stated_gap IS NULL OR fu.floor_used IS NULL
                      OR s.separate_gap IS NULL THEN NULL
                 WHEN ABS(t.stated_gap) <= fu.floor_used THEN 'NO CONVENTION STATED'
                 WHEN ABS(s.separate_gap - t.stated_gap) <= fu.floor_used
                  AND ABS(s.separate_gap) <= fu.floor_used
                   THEN CASE WHEN ABS(s.separate_gap - t.stated_gap)
                                  < ABS(s.separate_gap) THEN 'APPLIED'
                             WHEN ABS(s.separate_gap)
                                  < ABS(s.separate_gap - t.stated_gap)
                               THEN 'NOT APPLIED'
                             ELSE 'NO VERDICT (equidistant)' END
                 WHEN ABS(s.separate_gap - t.stated_gap) <= fu.floor_used
                   THEN 'APPLIED'
                 WHEN ABS(s.separate_gap) <= fu.floor_used THEN 'NOT APPLIED'
                 ELSE 'PARTLY' END AS verdict,
               CASE WHEN t.stated_gap IS NULL OR fu.floor_used IS NULL
                      OR s.separate_gap IS NULL THEN NULL
                    WHEN ABS(t.stated_gap) <= fu.floor_used THEN 0
                    WHEN ABS(s.separate_gap - t.stated_gap) <= fu.floor_used
                     AND ABS(s.separate_gap) <= fu.floor_used THEN 1
                    ELSE 0 END AS verdict_tie_broken,
               CASE WHEN t.stated_gap IS NULL OR fu.floor_used IS NULL THEN NULL
                    WHEN fu.floor_used > ABS(t.stated_gap) / 2.0 THEN 1
                    ELSE 0 END AS low_resolution,
               -- ── WHERE THE STATED CONDITION SITS AGAINST THE ARM'S OWN
               --    COMPARISON GAP ─────────────────────────────────────────
               -- RAW digits against raw digits, both read on the same arm, judged
               -- against that arm's own floor_used. WITHIN takes precedence over
               -- BELOW and ABOVE, so an arm inside one floor of its comparison gap
               -- is never also counted as having missed it. No neutral baseline is
               -- needed, which is what lets prawns be counted on the same basis as
               -- the five authored pairs.
               CASE WHEN sc.gap IS NULL OR t.stated_gap IS NULL
                      OR fu.floor_used IS NULL THEN NULL
                    WHEN ABS(sc.gap - t.stated_gap) <= fu.floor_used THEN 'WITHIN'
                    WHEN sc.gap < t.stated_gap THEN 'BELOW'
                    ELSE 'ABOVE' END AS stated_condition_vs_stated,
               CASE WHEN t.stated_gap IS NULL OR fu.floor_used IS NULL
                      OR s.separate_gap IS NULL THEN NULL
                    WHEN ABS(t.stated_gap) <= fu.floor_used THEN NULL
                    ELSE s.separate_gap / t.stated_gap END AS share,
               CASE WHEN t.stated_gap IS NOT NULL THEN 'read' ELSE 'missing' END
                 AS status,
               -- ── WHY A VALUE IS ABSENT, FROM THE DATABASE AND NOT FROM A GUESS ─
               TRIM(COALESCE(
                 CASE WHEN t.stated_gap IS NULL THEN
                   COALESCE((SELECT 'comparison unread: ' || MIN(u.unread_reason)
                               FROM duty_cells u
                              WHERE u.arm = m.arm AND u.pair_id = p.pair_id
                                AND u.question = 'CMPN' AND u.status = 'unread'),
                            'no comparison cell exists for this arm and pair')
                 END || ' ', '')
                 || COALESCE(
                 CASE WHEN s.separate_gap IS NULL THEN
                   COALESCE((SELECT 'separate unread: ' || MIN(u.unread_reason)
                               FROM duty_cells u
                              WHERE u.arm = m.arm AND u.pair_id = p.pair_id
                                AND u.question = 'BLAME' AND u.condition = 'bare'
                                AND u.status = 'unread'),
                            CASE WHEN NOT EXISTS (
                                   SELECT 1 FROM duty_cells u2
                                    WHERE u2.arm = m.arm AND u2.question = 'BLAME'
                                      AND u2.condition = 'bare')
                                 THEN 'comparison only: this arm has no separate-case '
                                      || 'cell in any duty run'
                                 ELSE 'no separate cell exists for this arm and pair'
                            END)
                 END, '')) AS missing_reason
        FROM duty_fig6_arms m
        CROSS JOIN duty_pairs p
        LEFT JOIN duty_stated_gap t ON t.arm = m.arm AND t.pair_id = p.pair_id
        LEFT JOIN duty_separate_gap s ON s.arm = m.arm AND s.pair_id = p.pair_id
        LEFT JOIN duty_floor_used fu ON fu.arm = m.arm
        LEFT JOIN duty_remedy_gap sc ON sc.arm = m.arm AND sc.pair_id = p.pair_id
                                    AND sc.condition = 'stated'
        WHERE p.status = 'reported'
 """,
 "duty_fig7_panels": """
    CREATE VIEW duty_fig7_panels AS
        SELECT f.pair_id, f.pair_label, MIN(f.panel_order) AS panel_order,
               COUNT(f.stated_gap) AS n_arms_stated,
               COUNT(f.separate_gap) AS n_arms_separate,
               SUM(COALESCE(f.convention_stated, 0)) AS n_convention_stated,
               SUM(CASE WHEN f.verdict = 'APPLIED' THEN 1 ELSE 0 END) AS n_applied,
               SUM(CASE WHEN f.verdict = 'PARTLY' THEN 1 ELSE 0 END) AS n_partly,
               SUM(CASE WHEN f.verdict = 'NOT APPLIED' THEN 1 ELSE 0 END)
                 AS n_not_applied,
               SUM(CASE WHEN f.verdict = 'NO CONVENTION STATED' THEN 1 ELSE 0 END)
                 AS n_no_convention,
               SUM(CASE WHEN f.verdict IS NULL THEN 1 ELSE 0 END) AS n_no_verdict,
               SUM(COALESCE(f.low_resolution, 0)) AS n_low_resolution,
               -- ── THE STATED CONDITION, PER PANEL ──────────────────────────
               COUNT(f.stated_condition_gap) AS n_stated_condition,
               SUM(CASE WHEN f.stated_condition_vs_stated = 'BELOW' THEN 1 ELSE 0 END)
                 AS n_sc_below_stated,
               SUM(CASE WHEN f.stated_condition_vs_stated = 'WITHIN' THEN 1 ELSE 0 END)
                 AS n_sc_within_stated,
               SUM(CASE WHEN f.stated_condition_vs_stated = 'ABOVE' THEN 1 ELSE 0 END)
                 AS n_sc_above_stated,
               SUM(CASE WHEN f.stated_condition_gap IS NOT NULL
                         AND f.stated_condition_vs_stated IS NULL THEN 1 ELSE 0 END)
                 AS n_sc_unplaced,
               -- ── WHETHER THIS PANEL HAS A NEUTRAL BASELINE AT ALL ─────────
               -- prawns does not: its two cases come from the families bank and no
               -- neutral sentences were ever written for it, so its remedy class is
               -- refused rather than borrowed. The stated-condition columns above
               -- need no baseline, which is why prawns is counted in them on the
               -- same basis as every other panel.
               CASE WHEN EXISTS (SELECT 1 FROM duty_texts dt
                                  WHERE dt.pair_id = f.pair_id
                                    AND dt.kind = 'neutral')
                    THEN 'read: three neutral sentences'
                    ELSE 'NONE: this pair has no neutral sentences, so it has no '
                         || 'remedy class and no recovery ratio' END
                 AS neutral_baseline,
               COUNT(*) AS n_rows
        FROM duty_fig7 f
        WHERE f.""" + _COUNTED + """
        GROUP BY f.pair_id, f.pair_label
 """,
 # the medians and the one-arm-per-model dispersion the panel headers quote, by the
 # same linear interpolation statistics.median and statistics.quantiles use
 # ── ONE ARM PER MODEL, ACROSS BOTH CONFIGURATIONS ────────────────────────────
 # duty_model_arm holds one arm per model PER configuration set, which is right for
 # the off/on dispersion blocks and wrong for a single CV per panel: five models
 # appear in both sets and would be counted twice. The rule is the one already ruled
 # for the spread -- the reasoning-off arm where both exist -- so the preference is
 # expressed once here rather than restated by whatever consumes it.
 "duty_model_arm_one": """
    CREATE VIEW duty_model_arm_one AS
        SELECT model_id,
               COALESCE(MAX(CASE WHEN config_set = 'off' THEN arm END),
                        MAX(CASE WHEN config_set = 'on' THEN arm END)) AS arm,
               CASE WHEN MAX(CASE WHEN config_set = 'off' THEN 1 ELSE 0 END) = 1
                    THEN 'off' ELSE 'on' END AS config_set_used,
               COUNT(*) AS n_config_sets
        FROM duty_model_arm GROUP BY model_id
 """,
 "duty_fig7_cv": """
    CREATE VIEW duty_fig7_cv AS
        SELECT f.pair_id, COUNT(*) AS n_models_cv, AVG(f.stated_gap) AS mean_gap,
               CASE WHEN COUNT(*) >= 2
                    THEN SQRT(MAX(SUM((f.stated_gap - m.mg) * (f.stated_gap - m.mg))
                                  / (COUNT(*) - 1), 0.0)) END AS sd_stated,
               CASE WHEN COUNT(*) >= 2 AND ABS(m.mg) >= 0.05
                    THEN SQRT(MAX(SUM((f.stated_gap - m.mg) * (f.stated_gap - m.mg))
                                  / (COUNT(*) - 1), 0.0)) / m.mg END AS cv_stated,
               CASE WHEN ABS(m.mg) < 0.05
                    THEN 'mean within 0.05 of zero: a CV would be an artefact of'
                         || ' the denominator' END AS cv_refused_reason
        FROM duty_fig7 f
        JOIN duty_model_arm_one o ON o.arm = f.arm
        JOIN (SELECT f2.pair_id, AVG(f2.stated_gap) AS mg FROM duty_fig7 f2
               JOIN duty_model_arm_one o2 ON o2.arm = f2.arm
               WHERE f2.stated_gap IS NOT NULL GROUP BY f2.pair_id) m
          ON m.pair_id = f.pair_id
        WHERE f.stated_gap IS NOT NULL
        GROUP BY f.pair_id, m.mg
 """,
 "duty_fig7_stated_ranked": """
    CREATE VIEW duty_fig7_stated_ranked AS
        SELECT pair_id, stated_gap AS g,
               ROW_NUMBER() OVER (PARTITION BY pair_id ORDER BY stated_gap) - 1 AS i,
               COUNT(*) OVER (PARTITION BY pair_id) AS n
        FROM duty_fig7 WHERE stated_gap IS NOT NULL AND """ + _COUNTED + """
 """,
 "duty_fig7_sc_ranked": """
    CREATE VIEW duty_fig7_sc_ranked AS
        SELECT pair_id, stated_condition_gap AS g,
               ROW_NUMBER() OVER (PARTITION BY pair_id
                                  ORDER BY stated_condition_gap) - 1 AS i,
               COUNT(*) OVER (PARTITION BY pair_id) AS n
        FROM duty_fig7 WHERE stated_condition_gap IS NOT NULL AND """ + _COUNTED + """
 """,
 "duty_fig7_share_ranked": """
    CREATE VIEW duty_fig7_share_ranked AS
        SELECT pair_id, share AS g,
               ROW_NUMBER() OVER (PARTITION BY pair_id ORDER BY share) - 1 AS i,
               COUNT(*) OVER (PARTITION BY pair_id) AS n
        FROM duty_fig7 WHERE share IS NOT NULL AND """ + _COUNTED + """
 """,
 # ── SIGNAL-TO-NOISE (TABLE B.9) ───────────────────────────────────────────────
 # The stated gap divided by the arm's own wording floor (floor_used), signed, per
 # arm and pair, with convention_stated and low_resolution carried beside it as
 # duty_fig7 defines them. NULL with a reason where either term is missing; a
 # floor_used of zero cannot occur (it is floored at 0.30 or is a draw band, which
 # is itself floored at 0.30), so no division guard is needed beyond NULL.
 "duty_signal_to_noise": """
    CREATE VIEW duty_signal_to_noise AS
        SELECT f.arm, f.model_label, f.reasoning, f.pair_id, f.pair_label,
               f.panel_order, f.stated_gap, f.floor_used, f.floor_used_source,
               CASE WHEN f.stated_gap IS NULL OR f.floor_used IS NULL THEN NULL
                    ELSE f.stated_gap / f.floor_used END AS signal_to_noise,
               f.convention_stated, f.low_resolution,
               CASE WHEN f.stated_gap IS NULL THEN 'no stated gap: ' || f.missing_reason
                    WHEN f.floor_used IS NULL THEN 'no floor_used for this arm'
                    END AS refused_reason
        FROM duty_fig7 f
 """,
 "duty_snr_ranked": """
    CREATE VIEW duty_snr_ranked AS
        SELECT arm, signal_to_noise AS g,
               ROW_NUMBER() OVER (PARTITION BY arm ORDER BY signal_to_noise) - 1 AS i,
               COUNT(*) OVER (PARTITION BY arm) AS n
        FROM duty_signal_to_noise WHERE signal_to_noise IS NOT NULL
 """,
 # per-arm median over the pairs it has a value for, by the linear interpolation
 # statistics.median uses; n_pairs is the denominator and n_pairs_refused what fell out
 "duty_signal_to_noise_arm": """
    CREATE VIEW duty_signal_to_noise_arm AS
        WITH q AS (SELECT arm, n, (n - 1) * 0.5 AS p FROM duty_snr_ranked
                   GROUP BY arm, n)
        SELECT a.arm, q.n AS n_pairs,
               (SELECT COUNT(*) FROM duty_signal_to_noise s
                 WHERE s.arm = a.arm AND s.signal_to_noise IS NULL) AS n_pairs_refused,
               (SELECT g FROM duty_snr_ranked r WHERE r.arm = q.arm
                   AND r.i = CAST(q.p AS INTEGER))
               + (q.p - CAST(q.p AS INTEGER))
                 * (COALESCE((SELECT g FROM duty_snr_ranked r WHERE r.arm = q.arm
                                 AND r.i = CAST(q.p AS INTEGER) + 1),
                             (SELECT g FROM duty_snr_ranked r WHERE r.arm = q.arm
                                 AND r.i = CAST(q.p AS INTEGER)))
                    - (SELECT g FROM duty_snr_ranked r WHERE r.arm = q.arm
                          AND r.i = CAST(q.p AS INTEGER))) AS median_signal_to_noise
        FROM (SELECT DISTINCT arm FROM duty_signal_to_noise) a
        LEFT JOIN q ON q.arm = a.arm
 """,
 # ── 9. THE ASSUMPTION-OF-RISK GROUPING (duty_hair_dye.P5) ───────────────────────────────
 "duty_risk_grouping": """
    CREATE VIEW duty_risk_grouping AS
        SELECT g.arm, p.victim_chose_arrangement AS chose,
               COUNT(*) AS n_pairs, AVG(g.stated_gap) AS mean_stated_gap,
               AVG(s.separate_gap) AS mean_separate_gap,
               COUNT(s.separate_gap) AS n_separate
        FROM duty_stated_gap g
        JOIN duty_pairs p ON p.pair_id = g.pair_id
        LEFT JOIN duty_separate_gap s ON s.arm = g.arm AND s.pair_id = g.pair_id
        WHERE p.status = 'reported'
        GROUP BY g.arm, p.victim_chose_arrangement
 """,
}


# ──────────────────────────────────────────────────────────────────────────────
# INGEST
# ──────────────────────────────────────────────────────────────────────────────
def _sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def _fsha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _bank(key):
    rel, want = BANKS[key]
    p = os.path.join(R, rel)
    if not os.path.exists(p):
        raise Refuse(f"{rel} is missing")
    got = _fsha(p)
    if got != want:
        raise Refuse(f"{rel} is sha {got[:16]}, frozen at {want[:16]}")
    rows, meta = {}, None
    for line in open(p):
        d = json.loads(line)
        if d.get("uid") == "_meta":
            meta = d
            continue
        k = "text" if "text" in d else "item"
        if _sha(d[k]) != d[f"{k}_sha256"]:
            raise Refuse(f"{rel}: {d['uid']} does not hash to its banked sha")
        rows[d["uid"]] = d
    return rel, want, rows, meta


def _wire_sha(w):
    return _sha(json.dumps(w, sort_keys=True))[:32] if w else "none"


def ingest_texts(con):
    """duty_pairs and duty_texts, from the frozen banks."""
    shas = {}
    banks = {}
    for k in BANKS:
        banks[k] = _bank(k)
        shas[k] = banks[k][1]
    for pid, name, status, pl, vl, chose, bk, note in PAIRS:
        con.execute(
            "INSERT INTO duty_pairs(pair_id,name,status,retired_reason,pro_label,"
            "priv_label,victim_chose_arrangement,bank,bank_sha,notes) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            (pid, name, status,
             ("herbal medicine: a contested convention. The private leg (a parent "
              "giving a child too high a dose) is arguably abusive rather than less "
              "culpable, so the pair cannot isolate the professional duty. Read and "
              "banked; not reported." if status == "retired" else None),
             pl, vl, chose, banks[bk][0], shas[bk], note))

    def put(tid, pid, leg, kind, variant, text, bk):
        con.execute("INSERT OR IGNORE INTO duty_texts(text_id,pair_id,leg,kind,"
                    "variant,text,sha256,word_count,bank,bank_sha) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (tid, pid, leg, kind, variant, text, _sha(text),
                     len(text.split()), banks[bk][0], shas[bk]))

    # pairs 1-6, from the duty_pairs bank
    for uid, d in sorted(banks["duty"][2].items()):
        pid = str(d["pair"])
        if d["kind"] == "separate":
            leg = {"PRO": "pro", "PRIV": "priv", "BOTH": "both"}[d["slot"]]
            put(uid, pid, leg, "separate", None, d["text"], "duty")
        else:
            put(uid, pid, "both", "comparison", d["order"], d["text"], "duty")
    # pair 7 and its cause questions, from the duty_hair_dye bank
    for uid, d in sorted(banks["r228"][2].items()):
        pid = str(d["pair"])
        if d["kind"] == "separate":
            put(uid, pid, {"PRO": "pro", "PRIV": "priv"}[d["slot"]],
                "separate", None, d["text"], "r228")
        elif d["kind"] == "cmpn":
            put(uid, pid, "both", "comparison", d["order"], d["text"], "r228")
        else:
            leg = {"PRO": "pro", "PRIV": "priv"}[d["slot"]]
            kind = ("neutral" if d["condition"].endswith("neutral")
                    else "convention" if d["condition"] == "B_stated"
                    else "comparand")
            var = (f"neutral_{d['neutral_index']}" if d["neutral_index"] else None)
            put(uid, pid, leg, kind, var, d["item"], "r228")
    # the cause questions, frozen in the 228 bank's _meta with their own shas
    cm = banks["r228"][3]["cause"]
    for k, c in sorted(cm.items()):
        put(f"CAUSE_P{k}", str(k), "both", "cause_question", c["harm_noun"],
            c["body"], "r228")
    # the duty_remedies conditions. The CONVENTION and NEUTRAL sentences are also stored on
    # their own, because the paper prints the sentence and not the rendered item.
    m1 = banks["r227v1"][3]
    for p, s in sorted(m1["stated"].items()):
        put(f"CONVENTION_P{p}", str(p), "both", "convention", None, s, "r227v1")
    for p, s in sorted(m1["neutral"].items()):
        put(f"NEUTRALSENT_P{p}_1", str(p), "both", "neutral", "neutral_1", s,
            "r227v1")
    for uid, d in sorted(banks["r227v1"][2].items()):
        leg = {"PRO": "pro", "PRIV": "priv"}[d["slot"]]
        kind = ("neutral" if d["condition"] == "A_neutral"
                else "convention" if d["condition"] == "B_stated" else "comparand")
        var = "neutral_1" if kind == "neutral" else None
        put(uid, str(d["pair"]), leg, kind, var, d["item"], "r227v1")
    for uid, d in sorted(banks["r227v2"][2].items()):
        leg = {"PRO": "pro", "PRIV": "priv"}[d["slot"]]
        put(uid, str(d["pair"]), leg, "neutral",
            f"neutral_{d['neutral_index']}", d["item"], "r227v2")
    # the second and third sentences themselves, as printed, read off the v2 rows'
    # own `prefix` field rather than retyped
    for uid, d in sorted(banks["r227v2"][2].items()):
        put(f"NEUTRALSENT_P{d['pair']}_{d['neutral_index']}", str(d["pair"]),
            "both", "neutral", f"neutral_{d['neutral_index']}", d["prefix"],
            "r227v2")
    # pair 7's convention and neutral sentences, as printed
    m8 = banks["r228"][3]
    for p, s in sorted(m8["stated"].items()):
        put(f"CONVENTION_P{p}", str(p), "both", "convention", None, s, "r228")
    for k, s in sorted(m8["neutral"].items()):
        put(f"NEUTRALSENT_P7_{k}", "7", "both", "neutral", f"neutral_{k}", s, "r228")
    # prawns' CONVENTION condition (duty_prawns_convention). Its two cases come from the families
    # bank by sha, so the items are banked here and the cases are identified by family
    # and role rather than by a duty_texts row that does not exist.
    m9 = banks["r229"][3]
    put("CONVENTION_Pprawns", "prawns", "both", "convention", None,
        m9["stated"]["prawns"], "r229")
    for uid, d in sorted(banks["r229"][2].items()):
        put(uid, "prawns", {"PRO": "pro", "PRIV": "priv"}[d["slot"]],
            "convention", None, d["item"], "r229")
    # prawns, v1.1: the neutral items, the full-text joint prompt and the reference case
    rel, want = V11_TEXTS
    if _fsha(os.path.join(R, rel)) != want:
        raise Refuse(f"{rel} is not the pinned v1.1 bank")
    banks["v11"] = (rel, want, {}, None)
    shas["v11"] = want
    for line in open(os.path.join(R, rel)):
        d = json.loads(line)
        if _sha(d["text"]) != d["sha256"]:
            raise Refuse(f"{rel}: a {d['kind']} row does not hash to its banked sha")
        tid = (f"V11_prawns_{d['variant']}" if d["kind"] == "comparison"
               else f"V11_prawns_{d['variant']}_{d['leg'].upper()}")
        put(tid, "prawns", d["leg"], d["kind"],
            (f"cmp_{d['variant']}" if d["kind"] == "comparison"
             else None if d["kind"] == "comparand" else d["variant"]), d["text"], "v11")
    rel, want = V11_QUESTIONS
    if _fsha(os.path.join(R, rel)) != want:
        raise Refuse(f"{rel} is not the pinned v1.1 question file")
    banks["v11q"] = (rel, want, {}, None)
    shas["v11q"] = want
    cq = json.load(open(os.path.join(R, rel)))["cause"]["prawns"]
    if _sha(cq["body"]) != cq["sha256"]:
        raise Refuse(f"{rel}: the prawns CAUSE body does not hash to its sha")
    put("CAUSE_Pprawns", "prawns", "both", "cause_question", cq["harm_noun"],
        cq["body"], "v11q")
    # prawns: the comparison texts, from the cmp bank
    for uid, d in sorted(banks["cmp"][2].items()):
        if not uid.startswith("CMPN_"):
            continue
        order = ("cmp_priv_first" if "home_first" in uid else "cmp_pro_first")
        put(uid, "prawns", "both", "comparison", order, d["text"], "cmp")
    return banks


# how each artefact's cell keys map onto (pair, leg, condition, question, text_id)
_RE_SEP = re.compile(r"^p(\d+)\|sep\|(PRO|PRIV)$")
_RE_CMP = re.compile(r"^p(\d+)\|cmpn\|(pro_first|priv_first)$")
_RE_CAU = re.compile(r"^p(\d+)\|cause\|(PRO|PRIV)$")
_RE_R227 = re.compile(r"^R227_P(\d+)_(A_neutral|B_stated|C_comparand)_(PRO|PRIV)$")
_RE_R227B = re.compile(r"^R227B_P(\d+)_A(\d)_neutral_(PRO|PRIV)$")
_RE_R228 = re.compile(r"^R228_P(\d+)_(A\d_neutral|B_stated|C_comparand)_(PRO|PRIV)$")
_RE_R229 = re.compile(r"^R229_PRAWNS_(B_stated)_(PRO|PRIV)$")
# only a later reading carries this key: every banked prawns separate cell comes from
# the families bank through the main `cells` table (see ingest_cells)
_RE_PRAWNS_SEP = re.compile(r"^prawns\|sep\|(PRO|PRIV)$")
_LEG = {"PRO": "pro", "PRIV": "priv"}
_COND = {"A_neutral": "neutral_1", "B_stated": "stated", "C_comparand": "comparand"}


def _classify(key):
    """(pair_id, leg, condition, question) for an artefact cell key, or None."""
    m = _RE_SEP.match(key)
    if m:
        return m.group(1), _LEG[m.group(2)], "bare", "BLAME"
    m = _RE_CMP.match(key)
    if m:
        return m.group(1), "both", f"cmp_{m.group(2)}", "CMPN"
    m = _RE_CAU.match(key)
    if m:
        return m.group(1), _LEG[m.group(2)], "bare", "CAUSE"
    m = _RE_R227.match(key)
    if m:
        return m.group(1), _LEG[m.group(3)], _COND[m.group(2)], "BLAME"
    m = _RE_R227B.match(key)
    if m:
        return m.group(1), _LEG[m.group(3)], f"neutral_{m.group(2)}", "BLAME"
    m = _RE_R229.match(key)
    if m:
        return "prawns", _LEG[m.group(2)], _COND[m.group(1)], "BLAME"
    m = _RE_PRAWNS_SEP.match(key)
    if m:
        return "prawns", _LEG[m.group(1)], "bare", "BLAME"
    m = _RE_R228.match(key)
    if m:
        c = m.group(2)
        cond = (f"neutral_{c[1]}" if c.endswith("neutral") else _COND[c])
        return m.group(1), _LEG[m.group(3)], cond, "BLAME"
    return None


def _ins(con, row, draws):
    row.setdefault("counts_note", None)
    row.setdefault("read_later", None)
    con.execute(
        "INSERT INTO duty_cells(cell_id,run,arm,pair_id,leg,condition,question,"
        "text_id,text_id_reason,n_draws,n_parsed,counts_note,ev,score_pro,score_priv,sd,"
        "answer_mass,answer_mass_note,n_reasoning,reasoning_share,provider,"
        "provider_served,model_id,wire_sha,source,artefact,artefact_sha,bank,"
        "preferred,duplicate_of,status,unread_reason,read_later) "
        "VALUES(:cell_id,:run,:arm,:pair_id,:leg,:condition,:question,:text_id,"
        ":text_id_reason,:n_draws,:n_parsed,:counts_note,:ev,:score_pro,:score_priv,:sd,"
        ":answer_mass,:answer_mass_note,:n_reasoning,:reasoning_share,:provider,"
        ":provider_served,:model_id,:wire_sha,:source,:artefact,:artefact_sha,"
        ":bank,:preferred,:duplicate_of,:status,:unread_reason,:read_later)", row)
    for i, (v, g) in enumerate(draws):
        con.execute("INSERT INTO duty_draws(cell_id,value_index,value,gap) "
                    "VALUES(?,?,?,?)", (row["cell_id"], i, v, g))


def v11_cell(key, c):
    """(arm, sample parts, leg, condition, question, bank, cell_id) for a completeness_fill duty
    cell of the extract. One definition, used by the ingest and by its test."""
    arm = key.split("|", 1)[0]
    parts = c["sample_id"].split("|")          # prawns|LEG|COND|chat, prawns|cmp|ORDER
    if parts[1] == "cmp":
        leg, cond, q = "both", V11_COND[parts[2]], "CMPN"
    else:
        leg = parts[1]
        cond = V11_COND[parts[2]]
        q = "CAUSE" if parts[2] == "cause" else "BLAME"
    bank = "cmp" if cond.startswith("cmp_reread") else "v11"
    return arm, parts, leg, cond, q, bank, f"237|{arm}|prawns|{cond}|{leg}|{q}|{bank}"


def ingest_cells(con, rep):
    """duty_cells and duty_draws, from every banked duty_pairs/227/228 artefact plus the
    prawns comparison from duty_chef_home_comparison/deployed_added_models."""
    seen, cov, refusals = {}, [], []
    tex = {t for (t,) in con.execute("SELECT text_id FROM duty_texts")}

    def wire_of(d, question):
        if question == "CMPN":
            w = d.get("wire_paired") or d.get("wire")
        else:
            w = d.get("wire_separate") or d.get("wire")
        return w

    def add(run, arm, key, c, d, path, asha, bank, src_default):
        cl = _classify(key)
        if cl is None:
            refusals.append(f"{path}: cell key {key!r} does not classify")
            return
        pair, leg, cond, q = cl
        w = wire_of(d, q) or {}
        prov = w.get("provider")
        if not prov:
            refusals.append(f"{path}: {key} has no provider on the wire")
            return
        uid = c.get("uid") or key
        tid = uid if uid in tex else None
        if tid is None and q == "CAUSE":
            tid = f"CAUSE_P{pair}"
            tid = tid if tid in tex else None
        reason = None if tid else ("the artefact names no banked row for this cell "
                                   f"(uid {uid!r})")
        if q == "CMPN":
            gap = c.get("stated_gap_pro_minus_priv")
            first, second = c.get("mean_first"), c.get("mean_second")
            if cond == "cmp_pro_first":
                spro, spriv = first, second
            else:
                spro, spriv = second, first
            ev = None
            gaps = c.get("gaps") or []
            draws = [(None, float(g)) for g in gaps]
            read = gap is not None
        else:
            ev = c.get("mean")
            spro = spriv = None
            draws = [(float(v), None) for v in (c.get("values") or [])]
            read = ev is not None
        npar = c.get("n_parsed")
        nrea = c.get("n_reasoning")
        cid = f"{run}|{arm}|{pair}|{cond}|{leg}|{q}|{bank}"
        row = {
            "cell_id": cid, "run": run, "arm": arm, "pair_id": pair, "leg": leg,
            "condition": cond, "question": q, "text_id": tid,
            "text_id_reason": reason,
            "n_draws": c.get("n_drawn") or d.get("draws_per_cell")
            or d.get("draws") or 0,
            "n_parsed": npar if npar is not None else 0,
            "ev": ev, "score_pro": spro, "score_priv": spriv, "sd": c.get("sd"),
            "answer_mass": None, "answer_mass_note": MASS_NOTE,
            "n_reasoning": nrea,
            "reasoning_share": ((nrea / npar) if (nrea is not None and npar)
                                else None),
            "provider": prov,
            "provider_served": json.dumps(d.get("provider_served"))
            if d.get("provider_served") else None,
            "model_id": w.get("model") or "UNRECORDED", "wire_sha": _wire_sha(w),
            "source": c.get("source") or src_default,
            "artefact": path, "artefact_sha": asha, "bank": bank,
            "preferred": 1, "duplicate_of": None,
            "status": "read" if read else "unread",
            "unread_reason": None if read else (
                "no value returned: "
                + ("; ".join((c.get("errors") or [])[:1])[:200]
                   if c.get("errors") else
                   f"{npar} of {c.get('n_drawn')} draws parsed")),
        }
        prev = seen.get((run, arm, pair, cond, leg, q))
        if prev:
            # NEUTRAL #1 IN TWO BANKS: both reads kept, one preferred (v2 over v1,
            # the preference analyse_duty_remedies_rerun.py already uses)
            keep_new = bank == "r227v2"
            con.execute("UPDATE duty_cells SET preferred=?, duplicate_of=? "
                        "WHERE cell_id=?",
                        (0 if keep_new else 1, cid, prev))
            row["preferred"] = 1 if keep_new else 0
            row["duplicate_of"] = prev
        seen[(run, arm, pair, cond, leg, q)] = cid
        _ins(con, row, draws)

    def artefacts(pat):
        return sorted(glob.glob(os.path.join(R, pat)))

    # ── duty_pairs, duty_remedies (both banks), duty_hair_dye, and the duty_hair_dye top-up ───────────────────
    SPECS = [
        ("records/read__*.json", "225", "duty", 13, "main"),
        ("records/read__*.json", "227", "r227v1", 13, "main"),
        ("records/read__*.json", "227", "r227v2", 14, "main"),
        ("records/read__*.json", "228", "r228", 13, "main"),
        ("records/topup__*.json", "228", "r228", 14, "topup"),
        ("records/read__*.json", "229", "r229", 13, "main"),
    ]
    for pat, run, bank, cut, src in SPECS:
        for path in artefacts(pat):
            rel = os.path.relpath(path, R)
            d = json.load(open(path))
            asha = _fsha(path)
            arm = d.get("arm") or os.path.basename(path)[cut:-5]
            cells = d.get("cells") or {}
            con.execute("INSERT INTO duty_artefacts(path,sha256,run,bank,arm,"
                        "n_cells,glob_pattern) VALUES(?,?,?,?,?,?,?)",
                        (rel, asha, run, bank, arm, len(cells), pat))
            for key, c in cells.items():
                add(run, arm, key, c, d, rel, asha, bank, src)

    # ── LATER READINGS: CELLS READ AFTER THEIR RUN, UNDER A DATED AMENDMENT ───
    # Gemini 3.1 Pro's 76 cells (records/AMENDMENT_GEMINI_PRO_DUTY_20261016.md). Each
    # cell keeps the run of the bank it was read from, so every view treats it as that
    # run's cell, and `read_later` carries the date and the amendment. No banked cell is
    # touched: these arms had no cell at these positions. A _PARTIAL file is never
    # ingested. A cell losing more than 10% of its draws is entered UNREAD with its
    # count (the truncation-void rule), never averaged over what was left.
    for path in artefacts("records/LATER_20261016__*__*.json"):
        if "_PARTIAL" in path:
            continue
        rel = os.path.relpath(path, R)
        d = json.load(open(path))
        asha = _fsha(path)
        arm = d["arm"]
        cells = d.get("cells") or {}
        con.execute("INSERT INTO duty_artefacts(path,sha256,run,bank,arm,"
                    "n_cells,glob_pattern) VALUES(?,?,?,?,?,?,?)",
                    (rel, asha, "later", d["group"], arm, len(cells),
                     "records/LATER_20261016__*__*.json"))
        note = (f"read later, {d['read_date']}, under {d['amendment']}; banked "
                f"comparison wire unchanged")
        for key, c in cells.items():
            bank = c["bank"]
            before = con.total_changes
            add(LATER_RUN[bank], arm, key, c, d, rel, asha, bank, "later")
            if con.total_changes == before:
                continue
            cid = con.execute("SELECT MAX(rowid), cell_id FROM duty_cells").fetchone()[1]
            con.execute("UPDATE duty_cells SET read_later=? WHERE cell_id=?",
                        (note, cid))
            if c.get("void_rule_fails"):
                con.execute(
                    "UPDATE duty_cells SET status='unread', unread_reason=? "
                    "WHERE cell_id=?",
                    (f"truncation-void rule: {c.get('n_void', 0)} void and "
                     f"{c.get('n_call_failed', 0)} failed of {c.get('n_drawn')} draws "
                     f"(over 10%)", cid))

    # ── completeness_fill: THE v1.1 PRAWNS CELLS (H4 to H6), READ LATER ─────────────────
    # From records/eval_extract.json, at the sitting final_eval_cells
    # names. Filed under completeness_fill, the run that read them: unlike the gemini_pro_fill cells,
    # these sit at no banked run's position (prawns had no neutral, reference-case,
    # CAUSE or full-text cell in any run), so there is no banked run to file them under.
    # A cell not read (no log-probabilities, deferred, provider gone) or void under the
    # 10% rule is a row with status 'unread' and its reason, never an absent row.
    import completeness_fill_fills as F237
    ex, _tg = F237.load()
    rel = F237.EXTRACT
    asha = _fsha(os.path.join(R, rel))
    n237 = 0
    duty_keys = sorted(k for k, c in ex["cells"].items() if c["test"] == "duty")
    con.execute("INSERT INTO duty_artefacts(path,sha256,run,bank,arm,n_cells,"
                "glob_pattern) VALUES(?,?,?,?,?,?,?)",
                (rel, asha, "237", "v11", "all", len(duty_keys), rel))
    unread_30b = [(k.replace("qwen235b|", "qwen30b|", 1), ex["cells"][k])
                  for k in duty_keys if k.startswith("qwen235b|")]
    for key, c in [(k, ex["cells"][k]) for k in duty_keys] + unread_30b:
        arm, parts, leg, cond, q, bank, _cid = v11_cell(key, c)
        if q == "CAUSE":
            tid = "CAUSE_Pprawns"
        elif q == "CMPN" and bank == "cmp":
            tid = ("CMPN_home_first" if "priv" in cond else "CMPN_chef_first")
        elif q == "CMPN":
            tid = f"V11_prawns_{parts[2]}"
        else:
            tid = f"V11_prawns_{parts[2]}_{leg.upper()}"
        if tid not in tex:
            raise Refuse(f"{rel}: {key} names no banked text ({tid})")
        if arm == "qwen30b":
            cls, why, sitting = ("UNREAD_PROVIDER_GONE", "Qwen3-30B: StreamLake, its "
                                 "banked provider, no longer serves it; no other "
                                 "provider is substituted (amendment §0)", "-")
        else:
            cls, why = F237.final_class(dict(c, arm=arm))
            sitting = c["sitting"]
        sc = c.get("score") or {}
        w = c.get("wire") or {}
        read = cls == "READ"
        dr = c.get("draws") if read else None
        if q == "CMPN":
            ev, spro, spriv = None, sc.get("score_pro"), sc.get("score_priv")
            draws = [(None, float(g)) for g in (dr or [])]
        else:
            ev, spro, spriv = sc.get("ev"), None, None
            draws = [(float(v), None) for v in (dr or [])]
        if not read:
            ev = spro = spriv = None
            draws = []
        # the eval's text sha must be the banked text's (the CAUSE prompt's item is
        # the families-bank separate case, so it is checked by the eval's pre-flight,
        # not here)
        if read and q != "CAUSE":
            got = con.execute("SELECT sha256 FROM duty_texts WHERE text_id=?",
                              (tid,)).fetchone()[0]
            if got != (c.get("meta") or {}).get("text_sha256"):
                raise Refuse(f"{rel}: {key} was read on a text whose sha is not {tid}'s")
        nr = sc.get("n_reasoning")
        npar = (len(dr) if dr is not None else None) if read else 0
        cid = _cid
        _ins(con, {
            "cell_id": cid, "run": "237", "arm": arm, "pair_id": "prawns", "leg": leg,
            "condition": cond, "question": q, "text_id": tid, "text_id_reason": None,
            "n_draws": sc.get("n_draws") or sc.get("draws_asked") or 0,
            "n_parsed": npar,
            "counts_note": (None if npar is not None else
                            "a log-prob cell is a distribution, not draws"),
            "ev": ev, "score_pro": spro, "score_priv": spriv,
            # a CMPN cell's spread is the population sd of its per-draw gaps, the
            # construction of the banked side-by-side's gap_sd
            "sd": ((statistics.pstdev(dr) if dr and len(dr) >= 2 else None)
                   if q == "CMPN" else sc.get("ev_sd")) if read else None,
            "answer_mass": None, "answer_mass_note": MASS_NOTE,
            "n_reasoning": nr,
            "reasoning_share": ((nr / npar) if (nr is not None and npar) else None),
            "provider": w.get("provider") or "UNREAD",
            "provider_served": json.dumps(c.get("served")) if c.get("served") else None,
            "model_id": w.get("model") or "UNREAD",
            "wire_sha": c.get("wire_sha") or "none",
            "source": "completeness_fill", "artefact": rel, "artefact_sha": asha, "bank": bank,
            "preferred": 1, "duplicate_of": None,
            "status": "read" if read else "unread",
            "unread_reason": None if read else f"{cls}: {why}",
            "read_later": (f"read later, 2026-10-17, completeness_fill sitting {sitting}, under "
                           f"completeness_fill_amendment (2d61d1f1)"),
        }, draws)
        n237 += 1
    rep.append(f"  completeness_fill (v1.1 prawns): {n237} duty cells from {rel}, 14 per arm "
               f"over 22 arms (Qwen3-30B entered unread: provider gone)")

    # ── PRAWNS: THE CHEF AGAINST HOME COOK COMPARISON, duty_chef_home_comparison and deployed_added_models ───────
    # It is a reported duty pair and its cells are not in duty_pairs, so they are
    # ingested here from their own artefacts rather than reached for across tables.
    # The artefacts hold no per-draw list, so prawns has no duty_draws rows: that is
    # recorded in build_meta rather than filled with anything.
    # ── deployed_added_models's CMP ARTEFACTS ARE NOT UNDER records/ ────────────────────────
    # They are in runs/deployed_added_models/results/. A records/-only glob found 0 of them, and the
    # three arms read there (haiku_s, kimi, haiku_r) silently lost their prawns cells:
    # the spread view then counted 12 models where the banked dispersion counted 14,
    # which is a smaller n on one pair and nothing in the numbers looking wrong.
    for pat, run in (("records/cmp__*.json", "221"),
                     ("records/cmp__*.json", "224"),
                     ("runs/deployed_added_models/results/cmp__*.json", "224")):
        for path in artefacts(pat):
            rel = os.path.relpath(path, R)
            d = json.load(open(path))
            asha = _fsha(path)
            arm = d.get("tag") or d.get("arm")
            cells = d.get("cells") or {}
            con.execute("INSERT INTO duty_artefacts(path,sha256,run,bank,arm,"
                        "n_cells,glob_pattern) VALUES(?,?,?,?,?,?,?)",
                        (rel, asha, run, "cmp", arm,
                         sum(1 for c in cells.values() if c.get("form") == "CMPN"),
                         pat))
            for key, c in cells.items():
                if c.get("form") != "CMPN":
                    continue
                order = c.get("order")
                cond = ("cmp_priv_first" if order == "home_first"
                        else "cmp_pro_first")
                gap = c.get("gap_chef_minus_home")
                cid = f"{run}|{arm}|prawns|{cond}|both|CMPN|cmp"
                _ins(con, {
                    "cell_id": cid, "run": run, "arm": arm, "pair_id": "prawns",
                    "leg": "both", "condition": cond, "question": "CMPN",
                    "text_id": c.get("uid") if c.get("uid") in tex else None,
                    "text_id_reason": None if c.get("uid") in tex else
                    f"the cmp bank has no row {c.get('uid')!r}",
                    "n_draws": c.get("n_asked") or d.get("draws") or 0,
                    "n_parsed": c.get("n_used") or 0,
                    "ev": None, "score_pro": c.get("chef_mean"),
                    "score_priv": c.get("home_mean"), "sd": c.get("gap_sd"),
                    "answer_mass": None, "answer_mass_note": MASS_NOTE,
                    "n_reasoning": c.get("n_reasoning"),
                    "reasoning_share": ((c["n_reasoning"] / c["n_used"])
                                        if c.get("n_used") else None),
                    "provider": d.get("provider_asked") or "UNRECORDED",
                    "provider_served": json.dumps(d.get("provider_served"))
                    if d.get("provider_served") else None,
                    "model_id": d.get("model_asked") or "UNRECORDED",
                    "wire_sha": _wire_sha({"model": d.get("model_asked"),
                                           "provider": d.get("provider_asked"),
                                           "max_tokens": d.get("max_tokens"),
                                           "readout": d.get("readout")}),
                    "source": "main", "artefact": rel, "artefact_sha": asha,
                    "bank": "cmp", "preferred": 1, "duplicate_of": None,
                    "status": "read" if gap is not None else "unread",
                    "unread_reason": None if gap is not None
                    else "no gap in the artefact",
                }, [])

    # ── PRAWNS' SEPARATE CELLS, SO ALL SIX FIGURE-7 PANELS COME FROM ONE PLACE ─
    # The prawns pair's separate gap is the CARELESS role read on the two scenarios:
    # prawns_restaurant C is the professional leg and prawns_home C the private one.
    # Those cells were banked in deployed_scenarios (and 222/224 for the late arms) and live in
    # the main `cells` table, so the VALUES are taken from there -- identical to what
    # `chef_home.csv` uses, asserted cell by cell in tests() -- while the PROVIDER is
    # read out of the artefact the database already records the path and sha of.
    # Without that the provider guard would have a hole exactly on the pair the figure
    # uses as its reference column.
    FAMLEG = {"prawns_restaurant": "pro", "prawns_home": "priv"}
    PRAWNS_FAM_ALIAS = {"deepseek_r_mt8192": "deepseek_r"}
    provcache = {}

    def artefact_provider(path):
        if path in provcache:
            return provcache[path]
        try:
            d = json.load(open(os.path.join(R, path)))
        except Exception:
            provcache[path] = (None, None, None)
            return provcache[path]
        prov = d.get("provider_requested") or d.get("provider_asked")
        served = d.get("provider_served")
        mid = d.get("model") or d.get("model_asked")
        provcache[path] = (prov, json.dumps(served) if served else None, mid,
                           d.get("draws"), d.get("readout"), d.get("mode"))
        return provcache[path]

    for row in con.execute(
            "SELECT a.path, a.sha256, a.run, a.arm, c.family, c.role, c.ev, c.ev_sd, "
            "       c.n_draws, c.n_reasoning, cp.delivery, c.reasoning_configured "
            "FROM cells c JOIN artefacts a ON a.id = c.artefact_id "
            "JOIN cell_positions cp ON cp.artefact_id = a.id AND cp.family IS c.family "
            "     AND cp.role = c.role AND cp.question IS c.question "
            "WHERE c.question = 'BLAME' AND c.role = 'C' AND cp.delivery = 'api' "
            "  AND c.family IN ('prawns_home', 'prawns_restaurant') "
            # a later excuse reading (completeness_fill) is not a prawns duty cell: Gemini 3.1
            # Pro's prawns separate cells are its gemini_pro_fill duty reading, and its C1
            # excuse cells would be a second, different-wire copy of the same position
            "  AND c.read_later IS NULL "
            "ORDER BY a.arm, c.family").fetchall():
        path, ash, run, arm, fam, role, ev, sd, nd, nr, _deliv, rcfg = row
        arm = PRAWNS_FAM_ALIAS.get(arm, arm)
        prov, served, mid, art_draws, art_readout, art_mode = artefact_provider(path)
        # ── THE DRAW COUNT COMES FROM THE ARTEFACT, NOT FROM A FALLBACK ───────
        # `cells.n_draws` is NULL on every families cell. Defaulting it to 10 made
        # `gpt6s_r` look like a 10-draw arm when its prawns cells were read at 20,
        # which is also the arm count duty_prawns_convention's call estimate turns on (440, not 420).
        if nd is None:
            nd = art_draws
        if not prov:
            refusals.append(f"{path}: prawns {fam} C has no provider on the artefact")
            continue
        leg = FAMLEG[fam]
        cid = f"{run}|{arm}|prawns|bare|{leg}|BLAME|families"
        if con.execute("SELECT 1 FROM duty_cells WHERE cell_id=?", (cid,)).fetchone():
            refusals.append(f"{cid}: two prawns {leg} cells for one arm and run")
            continue
        _ins(con, {
            "cell_id": cid, "run": run, "arm": arm, "pair_id": "prawns",
            "leg": leg, "condition": "bare", "question": "BLAME",
            "text_id": None,
            "text_id_reason": f"the {fam} C row is in the families bank, which this "
                              f"schema does not hold; it is identified by family and "
                              f"role on the cell",
            "n_draws": nd if nd is not None else 0,
            "n_parsed": None,
            "counts_note": (
                f"draws from the artefact's own `draws` field ({art_draws}); "
                f"cells.n_draws and cells.n_void are both NULL on the families "
                f"cells, so no parsed count is recorded for this cell anywhere"),
            "ev": ev, "score_pro": None, "score_priv": None, "sd": sd,
            "answer_mass": None, "answer_mass_note": MASS_NOTE,
            "n_reasoning": nr,
            "reasoning_share": ((nr / nd) if (nr is not None and nd) else None),
            "provider": prov, "provider_served": served,
            "model_id": mid or "UNRECORDED",
            # ── EACH ARM'S OWN WIRE (builder fix, 2026-10-17) ─────────────────
            # This hashed {model, provider, family} only, so arms reading one model on
            # one provider shared a hash (deepseek, deepseek_r and deepseek_s carried
            # the same two; so did the gpt6/grok/haiku _r and _s pairs), which reads as
            # one wire when the call logs show three. The artefact's readout, mode and
            # draws and the cell's configured reasoning (resolved from the call log's
            # on-the-wire field) are what differ between those arms, so they enter it.
            "wire_sha": _wire_sha({"model": mid, "provider": prov, "family": fam,
                                   "readout": art_readout, "mode": art_mode,
                                   "draws": art_draws, "reasoning_configured": rcfg}),
            "source": "main", "artefact": path, "artefact_sha": ash,
            "bank": "families", "preferred": 1, "duplicate_of": None,
            "status": "read" if ev is not None else "unread",
            "unread_reason": None if ev is not None else "no ev on the banked cell",
        }, [])

    # ── COVERAGE, SO EVERY COUNT HAS ITS DENOMINATOR ──────────────────────────
    EXPECT = {"225": 24, "227": 50, "228": 24}
    for run, nexp in sorted(EXPECT.items()):
        for arm in ARMS:
            if arm in PAIRED_ONLY and not con.execute(
                    "SELECT 1 FROM duty_cells WHERE arm=? AND read_later IS NOT NULL",
                    (arm,)).fetchone():
                nexp_arm = {"225": 12, "227": 0, "228": 2}[run]
            elif arm in PAIRED_ONLY:
                # read later in full: every reported position, not the retired pair 2
                nexp_arm = {"225": 22, "227": 40, "228": 24}[run]
            else:
                nexp_arm = nexp
            got = con.execute(
                "SELECT COUNT(*), SUM(status='read'), SUM(status='unread') "
                "FROM duty_cells WHERE run=? AND arm=?", (run, arm)).fetchone()
            paths = con.execute("SELECT DISTINCT artefact FROM duty_cells "
                                "WHERE run=? AND arm=?", (run, arm)).fetchall()
            con.execute("INSERT INTO duty_coverage(run,arm,cells_expected,"
                        "cells_present,cells_read,cells_unread,artefact,"
                        "absent_reason) VALUES(?,?,?,?,?,?,?,?)",
                        (run, arm, nexp_arm, got[0] or 0, got[1] or 0, got[2] or 0,
                         ", ".join(p[0] for p in paths) or None,
                         None if got[0] else
                         "no artefact: this arm has not been read on this run"))
    for mid, arm in MODEL_ARM_OFF.items():
        con.execute("INSERT INTO duty_model_arm(model_id,arm,config_set) "
                    "VALUES(?,?,'off')", (mid, arm))
    for mid, arm in MODEL_ARM_ON.items():
        con.execute("INSERT INTO duty_model_arm(model_id,arm,config_set) "
                    "VALUES(?,?,'on')", (mid, arm))
    n = con.execute("SELECT COUNT(*) FROM duty_cells").fetchone()[0]
    nd = con.execute("SELECT COUNT(*) FROM duty_draws").fetchone()[0]
    nu = con.execute("SELECT COUNT(*) FROM duty_cells "
                     "WHERE status='unread'").fetchone()[0]
    rep += ["", "## The duty test (duty_pairs, duty_remedies, duty_hair_dye)", "",
            f"  {con.execute('SELECT COUNT(*) FROM duty_pairs').fetchone()[0]} pairs, "
            f"{con.execute('SELECT COUNT(*) FROM duty_texts').fetchone()[0]} frozen "
            f"texts",
            f"  {n} cells ({n - nu} read, {nu} unread with a reason), "
            f"{nd} draw rows"]
    for r_ in refusals:
        rep.append(f"  REFUSED {r_}")
    return n, nd, nu, refusals


def ingest(con, rep):
    banks = ingest_texts(con)
    n, nd, nu, refusals = ingest_cells(con, rep)
    con.execute("INSERT INTO build_meta(k,v) VALUES('duty_draws_fields',?)",
                ("duty_draws holds the parsed digit (BLAME/CAUSE) or the per-draw gap "
                 "(CMPN) and its index among the PARSED draws. The artefacts hold no "
                 "per-draw reasoning flag, provider or timestamp, only per-cell "
                 "counts, so those columns do not exist rather than being filled. "
                 "The prawns comparison artefacts hold no per-draw list at all, so "
                 "pair 'prawns' has no draw rows.",))
    return n, nd, nu, refusals


# ──────────────────────────────────────────────────────────────────────────────
# BUILD TESTS. Same (name, ok, n, detail) shape the build's own tests use.
# ──────────────────────────────────────────────────────────────────────────────
def _close(a, b, tol=5e-4):
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tol


def tests(con):
    T = []

    # ── 1. EVERY CELL OF EVERY INGESTED ARTEFACT IS A ROW ─────────────────────
    want, miss = 0, []
    for rel, asha, run, bank, arm, ncells in con.execute(
            "SELECT path,sha256,run,bank,arm,n_cells FROM duty_artefacts "
            "WHERE bank<>'cmp' ORDER BY path"):
        p = os.path.join(R, rel)
        if not os.path.exists(p):
            miss.append(f"{rel}: ingested and now absent")
            want += ncells
            continue
        if _fsha(p) != asha:
            miss.append(f"{rel}: changed since it was ingested this build")
            want += ncells
            continue
        d = json.load(open(p))
        if run == "237":
            # the extract holds every completeness_fill cell; its duty cells, plus Qwen3-30B's
            # fourteen entered unread beside Qwen3-235B's
            dk = sorted(k for k, c in d["cells"].items() if c["test"] == "duty")
            for k in dk + [k.replace("qwen235b|", "qwen30b|", 1) for k in dk
                           if k.startswith("qwen235b|")]:
                want += 1
                cid = v11_cell(k, d["cells"].get(k) or
                               d["cells"][k.replace("qwen30b|", "qwen235b|", 1)])[6]
                if not con.execute("SELECT 1 FROM duty_cells WHERE cell_id=?",
                                   (cid,)).fetchone():
                    miss.append(cid)
            continue
        for key, cv in (d.get("cells") or {}).items():
            cl = _classify(key)
            if cl is None:
                miss.append(f"{os.path.basename(rel)}: {key} unclassified")
                continue
            pair, leg, cond, q = cl
            want += 1
            if run == "later":         # the cell names its own bank, and so its run
                cid = (f"{LATER_RUN[cv['bank']]}|{arm}|{pair}|{cond}|{leg}|{q}|"
                       f"{cv['bank']}")
            else:
                cid = f"{run}|{arm}|{pair}|{cond}|{leg}|{q}|{bank}"
            if not con.execute("SELECT 1 FROM duty_cells WHERE cell_id=?",
                               (cid,)).fetchone():
                miss.append(cid)
    T.append(("duty: every cell of every ingested artefact is a row in duty_cells",
              want - len(miss), want, miss[:6]))

    # ── AND SEPARATELY: IS THE BUILD STALE? ───────────────────────────────────
    # A read that finishes between the ingest and this test is a freshness fact, not an
    # ingest defect. Reported, never gated: gating it would fail a correct build
    # because a background read landed, and the remedy is to rebuild, not to fix code.
    on_disk, fresh = [], []
    for pat in ("records/read__*.json", "records/read__*.json",
                "records/read__*.json", "records/read__*.json",
                "records/topup__*.json", "records/cmp__*.json",
                "records/cmp__*.json"):
        for p in sorted(glob.glob(os.path.join(R, pat))):
            rel = os.path.relpath(p, R)
            on_disk.append(rel)
            if not con.execute("SELECT 1 FROM duty_artefacts WHERE path=?",
                               (rel,)).fetchone():
                fresh.append(rel)
    T.append(("REPORTED not gated | duty: every duty artefact on disk was seen by "
              "this build", len(on_disk) - len(fresh), len(on_disk),
              [f"NOT INGESTED (landed after the ingest, or a new arm): {x}"
               for x in fresh[:8]]))

    nu = con.execute("SELECT COUNT(*) FROM duty_cells "
                     "WHERE status='unread'").fetchone()[0]
    nur = con.execute("SELECT COUNT(*) FROM duty_cells WHERE status='unread' "
                      "AND unread_reason IS NOT NULL AND unread_reason<>''"
                      ).fetchone()[0]
    T.append(("duty: every unread cell carries a reason", nur, nu, []))

    # ── 2. EVERY TEXT RESOLVES AND HASHES TO ITS BANK ─────────────────────────
    bad = []
    rows = con.execute("SELECT text_id,text,sha256,bank,bank_sha,word_count "
                       "FROM duty_texts").fetchall()
    for tid, txt, sh, bank, bsha, wc in rows:
        if _sha(txt) != sh:
            bad.append(f"{tid}: text does not hash to its stored sha")
        if len(txt.split()) != wc:
            bad.append(f"{tid}: word_count {wc} is not the text's")
        p = os.path.join(R, bank)
        if not os.path.exists(p) or _fsha(p) != bsha:
            bad.append(f"{tid}: bank {bank} is not at sha {bsha[:16]}")
    T.append(("duty: every duty_texts row hashes to its bank", len(rows) - len(bad),
              len(rows), bad[:6]))
    nulltid = con.execute("SELECT COUNT(*) FROM duty_cells WHERE text_id IS NULL "
                          "AND text_id_reason IS NULL").fetchone()[0]
    ntid = con.execute("SELECT COUNT(*) FROM duty_cells").fetchone()[0]
    T.append(("duty: a cell with no text_id says why", ntid - nulltid, ntid, []))
    orphan = con.execute("SELECT COUNT(*) FROM duty_cells c WHERE c.text_id IS NOT "
                         "NULL AND NOT EXISTS(SELECT 1 FROM duty_texts t WHERE "
                         "t.text_id=c.text_id)").fetchone()[0]
    T.append(("duty: every text_id resolves to a frozen text", ntid - orphan, ntid,
              []))

    # ── 3. NO REPORTED CONTRAST SPANS TWO PROVIDERS ───────────────────────────
    span = con.execute("""SELECT s.run,s.arm,s.pair_id,s.n_providers,s.providers
        FROM duty_provider_span s JOIN duty_pairs p ON p.pair_id=s.pair_id
        WHERE p.status='reported' AND s.n_providers > 1""").fetchall()
    tot = con.execute("""SELECT COUNT(*) FROM duty_provider_span s
        JOIN duty_pairs p ON p.pair_id=s.pair_id
        WHERE p.status='reported'""").fetchone()[0]
    T.append(("duty: no reported contrast spans two providers", tot - len(span), tot,
              [f"{r[1]} pair {r[2]}: {r[4]}" for r in span[:6]]))
    # and the same question asked of every view that differences two cells
    multi = []
    for v in ("duty_stated_gap", "duty_separate_gap", "duty_remedy_gap",
              "duty_cause", "duty_neutral_gap"):
        q = (f"SELECT COUNT(*) FROM {v} v JOIN duty_provider_span s "
             f"ON s.arm=v.arm AND s.pair_id=v.pair_id WHERE s.n_providers>1")
        k = con.execute(q).fetchone()[0]
        if k:
            multi.append(f"{v}: {k} row(s)")
    T.append(("duty: no view row differences cells from two providers",
              5 - len(multi), 5, multi))

    # ── 4. PAIR 2 IS IN EVERY RAW TABLE AND NO REPORTED VIEW ──────────────────
    raw_ok, raw_n, det = 0, 0, []
    for t in ("duty_pairs", "duty_texts", "duty_cells", "duty_draws"):
        raw_n += 1
        if t == "duty_draws":
            k = con.execute("SELECT COUNT(*) FROM duty_draws d JOIN duty_cells c "
                            "ON c.cell_id=d.cell_id WHERE c.pair_id='2'").fetchone()[0]
        else:
            k = con.execute(f"SELECT COUNT(*) FROM {t} WHERE pair_id='2'").fetchone()[0]
        if k:
            raw_ok += 1
        else:
            det.append(f"{t} holds no pair-2 row")
    for v in ("duty_reported", "duty_stated_gap", "duty_separate_gap",
              "duty_share", "duty_neutral_baseline", "duty_remedy_effect",
              "duty_cause", "duty_spread"):
        raw_n += 1
        k = con.execute(f"SELECT COUNT(*) FROM {v} WHERE pair_id='2'").fetchone()[0]
        if k == 0:
            raw_ok += 1
        else:
            det.append(f"{v} leaks {k} pair-2 row(s)")
    T.append(("duty: pair 2 is in every raw table and no reported view", raw_ok,
              raw_n, det))

    # ── 5. THE MODEL-ARM TABLE AGREES WITH dispersion_duty_pairs ──────────────────
    try:
        import importlib
        import sys as _s
        _s.path.insert(0, os.path.join(R, "scripts"))
        D225 = importlib.import_module("dispersion_duty_pairs")
        pairs = []
        for cs, src in (("off", D225.OFF), ("on", D225.ON)):
            for mid, arm in src.items():
                pairs.append((cs, mid, arm))
        bad = []
        for cs, mid, arm in pairs:
            got = con.execute("SELECT arm FROM duty_model_arm WHERE model_id=? "
                              "AND config_set=?", (mid, cs)).fetchone()
            if not got or got[0] != arm:
                bad.append(f"{cs}/{mid}: table has {got and got[0]!r}, "
                           f"dispersion_duty_pairs has {arm!r}")
        k = con.execute("SELECT COUNT(*) FROM duty_model_arm").fetchone()[0]
        if k != len(pairs):
            bad.append(f"duty_model_arm has {k} rows, dispersion_duty_pairs has "
                       f"{len(pairs)}")
        T.append(("duty: duty_model_arm agrees with dispersion_duty_pairs exactly",
                  len(pairs) - len(bad), len(pairs), bad[:6]))
    except Exception as exc:
        T.append(("duty: duty_model_arm agrees with dispersion_duty_pairs exactly", 0, 1,
                  [repr(exc)[:160]]))

    # ── 6. THE VIEWS REPRODUCE THE BANKED FIGURES ─────────────────────────────
    ok, n, det = 0, 0, []
    for path in sorted(glob.glob(os.path.join(R, "records/analysis__*.json"))):
        a = json.load(open(path))
        arm = a["arm"]
        for p in ("1", "3", "4", "5"):
            q = a["pairs"].get(p) or {}
            for col, view, want in (
                    ("stated_gap", "duty_stated_gap", q.get("stated_gap")),
                    ("separate_gap", "duty_separate_gap", q.get("separate_gap"))):
                n += 1
                r = con.execute(f"SELECT {col} FROM {view} WHERE arm=? AND pair_id=?",
                                (arm, p)).fetchone()
                got = r[0] if r else None
                if _close(got, want):
                    ok += 1
                else:
                    det.append(f"{arm} pair {p} {col}: view {got}, banked {want}")
        # the control's band: sd and n, which the draw floor is built from
        n += 2
        r = con.execute("SELECT sd, n FROM duty_floor_draw WHERE arm=?",
                        (arm,)).fetchone()
        if r and _close(r[0], a.get("band_sd")):
            ok += 1
        else:
            det.append(f"{arm} control band sd: view {r and r[0]}, "
                       f"banked {a.get('band_sd')}")
        if r and r[1] == a.get("band_n"):
            ok += 1
        else:
            det.append(f"{arm} control band n: view {r and r[1]}, "
                       f"banked {a.get('band_n')}")
    T.append(("REPORTED not gated | duty: views reproduce duty_pairs's banked gaps and "
              "control band", ok, n, det[:10]))

    # duty_remedies's classes, on the r227_only floor they were computed under
    MAP = {"RESTORED": ("AT",), "NOT": ("WITHIN FLOOR",),
           "PARTLY": ("OVER", "UNDER")}
    ok, n, det = 0, 0, []
    p227 = os.path.join(R, "records/analysis.json")
    if os.path.exists(p227):
        a227 = json.load(open(p227))
        for arm, rec in sorted((a227.get("arms") or {}).items()):
            n += 1
            r = con.execute("SELECT sentence_floor_parametric FROM duty_floor "
                            "WHERE arm=? AND floor_set='r227_only'", (arm,)).fetchone()
            if r and _close(r[0], rec.get("floor_parametric")):
                ok += 1
            else:
                det.append(f"{arm} r227 floor: view {r and r[0]}, "
                           f"banked {rec.get('floor_parametric')}")
            for k, row in sorted((rec.get("rows") or {}).items()):
                pair, cond = k.split("|")
                cond = "stated" if cond == "B_stated" else "comparand"
                n += 1
                g = con.execute("SELECT class FROM duty_remedy_effect WHERE arm=? "
                                "AND pair_id=? AND condition=? AND "
                                "floor_set='r227_only'",
                                (arm, pair, cond)).fetchone()
                got = g[0] if g else None
                allowed = MAP.get(row.get("verdict"), ())
                if got in allowed:
                    ok += 1
                else:
                    det.append(f"{arm} pair {pair} {cond}: view {got!r}, banked "
                               f"{row.get('verdict')!r}")
    T.append(("REPORTED not gated | duty: views reproduce duty_remedies's banked classes "
              "(r227_only floor)", ok, n, det[:10]))

    ok, n, det = 0, 0, []
    p228 = os.path.join(R, "records/analysis.json")
    if os.path.exists(p228):
        a228 = json.load(open(p228))
        for arm, rec in sorted((a228.get("arms") or {}).items()):
            for key, want in (("stated_gap", rec.get("stated_gap")),
                              ("separate_gap", rec.get("separate_gap"))):
                if want is None:
                    continue
                n += 1
                view = ("duty_stated_gap" if key == "stated_gap"
                        else "duty_separate_gap")
                r = con.execute(f"SELECT {key} FROM {view} WHERE arm=? "
                                f"AND pair_id='7'", (arm,)).fetchone()
                if r and _close(r[0], want):
                    ok += 1
                else:
                    det.append(f"{arm} pair 7 {key}: view {r and r[0]}, "
                               f"banked {want}")
            if rec.get("neutral_baseline") is not None and rec.get(
                    "neutral_gaps_n", 3) == 3:
                n += 1
                r = con.execute("SELECT neutral_baseline FROM duty_neutral_baseline "
                                "WHERE arm=? AND pair_id='7'", (arm,)).fetchone()
                if r and _close(r[0], rec["neutral_baseline"]):
                    ok += 1
                else:
                    det.append(f"{arm} pair 7 neutral baseline: view {r and r[0]}, "
                               f"banked {rec['neutral_baseline']}")
            for cond, row in sorted((rec.get("remedies") or {}).items()):
                n += 1
                g = con.execute("SELECT class FROM duty_remedy_effect WHERE arm=? "
                                "AND pair_id='7' AND condition=? AND "
                                "floor_set='all_reported'", (arm, cond)).fetchone()
                got = g[0] if g else None
                if got == row.get("classification"):
                    ok += 1
                else:
                    det.append(f"{arm} pair 7 {cond}: view {got!r}, banked "
                               f"{row.get('classification')!r}")
    T.append(("REPORTED not gated | duty: views reproduce duty_hair_dye's banked analysis",
              ok, n, det[:10]))

    # ── THE SPREAD VIEW AGAINST THE BANKED DISPERSION RECORD ─────────────────
    ok, n, det = 0, 0, []
    pdis = os.path.join(R, "records/dispersion.json")
    if os.path.exists(pdis):
        dis = json.load(open(pdis))
        NAME = {"prawns (reference)": "prawns", "gas safety": "3",
                "electrical work": "1", "childcare": "4", "driving": "5"}
        for cs in ("off", "on"):
            for row in (dis.get("blocks") or {}).get(cs) or []:
                pid = NAME.get(row["pair"])
                if pid is None:
                    continue
                v = con.execute("SELECT n_models,mean_gap,sd,iqr,q1,q3 FROM "
                                "duty_spread WHERE config_set=? AND pair_id=?",
                                (cs, pid)).fetchone()
                for col, i, want in (("n_models", 0, row["n"]),
                                     ("mean_gap", 1, row["mean"]),
                                     ("sd", 2, row["sd"]),
                                     ("iqr", 3, row["iqr"]),
                                     ("q1", 4, row["q1"]),
                                     ("q3", 5, row["q3"])):
                    n += 1
                    got = v[i] if v else None
                    good = (got == want if col == "n_models" else _close(got, want))
                    if good:
                        ok += 1
                    else:
                        det.append(f"{cs} {row['pair']} {col}: view {got}, "
                                   f"banked {want}")
    T.append(("REPORTED not gated | duty: duty_spread reproduces the banked "
              "dispersion figures", ok, n, det[:10]))

    # ── 7. NEUTRAL #1 WAS READ TWICE ON SOME ARMS: WHAT THE TWO READS SAY ─────
    # ── WHICH BANK EACH ARM'S NEUTRAL #1 CAME FROM ───────────────────────────
    # The two banks hold the same text, so one arm could in principle carry two reads.
    # None does, because the halt arms' v2 read was --only A2,A3. The fact is reported
    # rather than an empty 0 of 0, and a genuine double read would show as n_banks 2
    # with its two values.
    srcs = con.execute("""SELECT arm, COUNT(DISTINCT bank) AS nb,
                                 GROUP_CONCAT(DISTINCT bank) AS banks
        FROM duty_cells WHERE run='duty_remedies' AND condition='neutral_1'
        GROUP BY arm ORDER BY arm""").fetchall()
    one = sum(1 for r in srcs if r[1] == 1)
    byb = {}
    for r in srcs:
        byb.setdefault(r[2], []).append(r[0])
    T.append(("REPORTED not gated | duty: neutral #1 comes from exactly one bank per "
              "arm", one, len(srcs),
              [f"{b}: {len(v)} arm(s) ({', '.join(sorted(v)[:4])}"
               + ("..." if len(v) > 4 else "") + ")" for b, v in sorted(byb.items())]
              + [f"TWO READS on {r[0]}: {r[2]}" for r in srcs if r[1] > 1]))
    dup = con.execute("""SELECT a.arm,a.pair_id,a.leg,a.ev,b.ev
        FROM duty_cells a JOIN duty_cells b ON b.cell_id=a.duplicate_of
        WHERE a.preferred=1 AND a.ev IS NOT NULL AND b.ev IS NOT NULL""").fetchall()
    if dup:
        agree = sum(1 for r in dup if abs(r[3] - r[4]) <= 0.5)
        T.append(("REPORTED not gated | duty: where a text was read twice, the two "
                  "reads within 0.5 digits", agree, len(dup),
                  [f"{r[0]} pair {r[1]} {r[2]}: {r[3]:.3f} vs {r[4]:.3f}"
                   for r in dup if abs(r[3] - r[4]) > 0.5][:6]))

    # ── 8. COVERAGE, WITH ITS DENOMINATOR ─────────────────────────────────────
    cov = con.execute("SELECT run,arm,cells_expected,cells_present,cells_read,"
                      "cells_unread,absent_reason FROM duty_coverage "
                      "ORDER BY run,arm").fetchall()
    full = sum(1 for r in cov if r[3] >= r[2])
    T.append(("REPORTED not gated | duty: arm x run coverage (cells present against "
              "expected)", full, len(cov),
              [f"run {r[0]} {r[1]}: {r[3]} of {r[2]} present, {r[4]} read, "
               f"{r[5]} unread" + (f" -- {r[6]}" if r[6] else "")
               for r in cov if r[3] < r[2]][:12]))

    # ── 9. SIGNAL-TO-NOISE: THE VIEW AGAINST PYTHON, ROW BY ROW AND BY MEDIAN ──
    import statistics
    rows = con.execute("SELECT arm,stated_gap,floor_used,signal_to_noise,"
                       "refused_reason FROM duty_signal_to_noise").fetchall()
    bad = [f"{a}: {g}/{fu} -> {s}" for a, g, fu, s, why in rows
           if (s is None) != (g is None or fu is None)
           or (s is not None and abs(s - g / fu) > 1e-12)
           or (s is None and not why)]
    T.append(("duty: signal_to_noise equals stated_gap / floor_used on every row, and "
              "every NULL carries a reason", len(rows) - len(bad), len(rows), bad[:6]))
    per = {}
    for a, g, fu, s, _ in rows:
        if s is not None:
            per.setdefault(a, []).append(s)
    arms = con.execute("SELECT arm,n_pairs,median_signal_to_noise "
                       "FROM duty_signal_to_noise_arm").fetchall()
    bad = [f"{a}: view {m} n {n} vs python {statistics.median(per[a]) if a in per else None}"
           for a, n, m in arms
           if (a in per) != (m is not None)
           or (a in per and (abs(m - statistics.median(per[a])) > 1e-12
                             or n != len(per[a])))]
    T.append(("duty: duty_signal_to_noise_arm's median equals statistics.median per arm",
              len(arms) - len(bad), len(arms), bad[:6]))
    return T

-- Figure 7. Database sha256: 08edd685103cca145d379f7e820ce357cb05be9e9b96a8d05576d688d5aebfd2

-- fig4to7_duty.csv
SELECT arm, model_label, reasoning, reasoning_source, group_order, row_order, pair_id, pair_label, panel_order, stated_gap_pro_first, stated_gap_priv_first, stated_gap, order_spread, exact_zero_flag, sep_pro, sep_priv, separate_gap, headroom_above_pro, stated_condition_pro, stated_condition_priv, stated_condition_gap, stated_condition_run, stated_condition_status, stated_condition_reason, stated_condition_vs_stated, floor_draw, floor_sentence, floor_used, floor_used_source, convention_stated, verdict, verdict_tie_broken, low_resolution, share, status, missing_reason
FROM duty_fig7
ORDER BY panel_order, group_order, row_order

-- fig6_duty_panels.csv
WITH med AS (
  SELECT pair_id, AVG(g) AS median_stated_gap FROM duty_fig7_stated_ranked
  WHERE i IN ((n - 1) / 2, n / 2) GROUP BY pair_id),
medsc AS (
  SELECT pair_id, AVG(g) AS median_stated_condition_gap FROM duty_fig7_sc_ranked
  WHERE i IN ((n - 1) / 2, n / 2) GROUP BY pair_id),
medshare AS (
  SELECT pair_id, AVG(g) AS median_share FROM duty_fig7_share_ranked
  WHERE i IN ((n - 1) / 2, n / 2) GROUP BY pair_id),
q AS (SELECT pair_id, n, (n - 1) * 0.25 AS p1, (n - 1) * 0.75 AS p3
      FROM duty_fig7_stated_ranked GROUP BY pair_id, n),
iq AS (
  SELECT q.pair_id,
         (SELECT g FROM duty_fig7_stated_ranked r WHERE r.pair_id = q.pair_id
           AND r.i = CAST(q.p1 AS INTEGER))
         + (q.p1 - CAST(q.p1 AS INTEGER))
           * (COALESCE((SELECT g FROM duty_fig7_stated_ranked r
                         WHERE r.pair_id = q.pair_id
                           AND r.i = CAST(q.p1 AS INTEGER) + 1),
                       (SELECT g FROM duty_fig7_stated_ranked r
                         WHERE r.pair_id = q.pair_id
                           AND r.i = CAST(q.p1 AS INTEGER)))
              - (SELECT g FROM duty_fig7_stated_ranked r WHERE r.pair_id = q.pair_id
                  AND r.i = CAST(q.p1 AS INTEGER))) AS q1,
         (SELECT g FROM duty_fig7_stated_ranked r WHERE r.pair_id = q.pair_id
           AND r.i = CAST(q.p3 AS INTEGER))
         + (q.p3 - CAST(q.p3 AS INTEGER))
           * (COALESCE((SELECT g FROM duty_fig7_stated_ranked r
                         WHERE r.pair_id = q.pair_id
                           AND r.i = CAST(q.p3 AS INTEGER) + 1),
                       (SELECT g FROM duty_fig7_stated_ranked r
                         WHERE r.pair_id = q.pair_id
                           AND r.i = CAST(q.p3 AS INTEGER)))
              - (SELECT g FROM duty_fig7_stated_ranked r WHERE r.pair_id = q.pair_id
                  AND r.i = CAST(q.p3 AS INTEGER))) AS q3
  FROM q)
SELECT p.panel_order, p.pair_id, p.pair_label,
       p.n_arms_stated, p.n_arms_separate, p.n_rows,
       med.median_stated_gap, iq.q3 - iq.q1 AS iqr_stated, iq.q1, iq.q3,
       cv.n_models_cv, cv.sd_stated, cv.cv_stated, cv.cv_refused_reason,
       p.n_convention_stated, medshare.median_share,
       p.n_applied, p.n_partly, p.n_not_applied, p.n_no_convention, p.n_no_verdict,
       p.n_low_resolution,
       p.n_stated_condition, medsc.median_stated_condition_gap,
       p.n_sc_below_stated, p.n_sc_within_stated, p.n_sc_above_stated,
       p.n_sc_unplaced, p.neutral_baseline
FROM duty_fig7_panels p
LEFT JOIN med ON med.pair_id = p.pair_id
LEFT JOIN medsc ON medsc.pair_id = p.pair_id
LEFT JOIN medshare ON medshare.pair_id = p.pair_id
LEFT JOIN iq ON iq.pair_id = p.pair_id
LEFT JOIN duty_fig7_cv cv ON cv.pair_id = p.pair_id
ORDER BY p.panel_order

-- the duty test's exports. Database sha256: ecb3380493fe29bdd25e7534076411429e11947978d2d8402d15c42da46742e2

-- duty_remedies.csv
SELECT e.floor_set, e.run, e.arm, e.pair_id, e.pair_name, e.condition,
       e.gap, e.neutral_baseline, e.n_neutrals, e.target_gap, e.effect_digits,
       e.d_pro, e.d_priv, e.floor, e.floor_robust, e.floors_diverge,
       e.class, e.tie_broken, e.low_resolution, e.recovery,
       e.recovery_refused_reason, e.professional_rises,
       p.victim_chose_arrangement
FROM duty_remedy_effect e JOIN duty_pairs p ON p.pair_id = e.pair_id
WHERE e.floor_set = 'all_reported'
ORDER BY e.arm, e.pair_id, e.condition

-- duty_remedies_summary.csv
SELECT arm,
       COUNT(*) AS n_cells,
       SUM(condition = 'stated') AS n_stated,
       SUM(condition = 'comparand') AS n_comparand,
       SUM(class = 'AT') AS n_at,
       SUM(class = 'OVER') AS n_over,
       SUM(class = 'UNDER') AS n_under,
       SUM(class = 'WITHIN FLOOR') AS n_within_floor,
       SUM(class IS NULL) AS n_no_class,
       SUM(low_resolution) AS n_low_resolution,
       SUM(professional_rises) AS n_professional_rises,
       MAX(floor) AS sentence_floor, MAX(floor_robust) AS sentence_floor_robust,
       MAX(floors_diverge) AS floors_diverge,
       COUNT(recovery) AS n_recovery_defined
FROM duty_remedy_effect WHERE floor_set = 'all_reported'
GROUP BY arm ORDER BY arm

-- duty_remedies_excluded.csv
-- every reported arm x pair that COULD have carried a remedy row and does not
SELECT c.arm, c.pair_id, p.name AS pair_name,
       COALESCE(b.refused_reason,
                'no stated comparison on this arm and pair',
                'unknown') AS reason,
       COALESCE(b.n_neutrals, 0) AS n_neutrals,
       (SELECT COUNT(*) FROM duty_cells u WHERE u.arm = c.arm
         AND u.pair_id = c.pair_id AND u.status = 'unread') AS unread_cells
FROM (SELECT DISTINCT arm, pair_id FROM duty_cells WHERE run IN ('duty_remedies','duty_hair_dye')) c
JOIN duty_pairs p ON p.pair_id = c.pair_id
LEFT JOIN duty_neutral_baseline b ON b.arm = c.arm AND b.pair_id = c.pair_id
WHERE p.status = 'reported'
  AND NOT EXISTS (SELECT 1 FROM duty_remedy_effect e
                   WHERE e.arm = c.arm AND e.pair_id = c.pair_id
                     AND e.floor_set = 'all_reported')
ORDER BY c.arm, c.pair_id

-- duty_spread.csv
SELECT config_set, pair_id, pair_name, n_models, mean_gap, sd, cv,
       cv_refused_reason, iqr, q1, q3, min_gap, max_gap, n_exact_zero_flagged
FROM duty_spread
ORDER BY config_set DESC,
         CASE pair_id WHEN 'prawns' THEN 0 WHEN '3' THEN 1 WHEN '1' THEN 2
                      WHEN '4' THEN 3 WHEN '5' THEN 4 WHEN '7' THEN 5 ELSE 9 END

-- duty_pairs_not_reported.csv
SELECT pair_id, name, status, retired_reason FROM duty_pairs
WHERE status <> 'reported' ORDER BY pair_id

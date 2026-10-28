-- Appendix A.9. Database sha256: d6f19e3a99edcf4cc9da7775e8fd762ae751955c5358ac4e5e104ac0fcbc8a97
-- arms excluded at the export: 
-- told class: w = 1 - stated_condition_gap / stated_gap where share is defined; |w| <= 0.10 within a tenth, <= 0.30 a tenth to three tenths, else more than three tenths; short if w > 0, over if w < 0
-- arm order: within reasoning, mean over pairs of (stated_gap - separate_gap), descending

-- A9_duty_long.csv
SELECT arm, model_label, reasoning, pair_id, pair_label, panel_order,
       stated_gap_pro_first, stated_gap_priv_first, stated_gap, order_spread,
       separate_gap, share, convention_stated, stated_condition_gap,
       stated_condition_run, stated_condition_status, stated_condition_reason,
       floor_sentence, floor_used, floor_draw, status, missing_reason
FROM duty_fig7
ORDER BY panel_order, group_order, row_order

-- A9_duty_arm.csv (signal_to_noise)
SELECT arm, n_pairs, n_pairs_refused, median_signal_to_noise
FROM duty_signal_to_noise_arm

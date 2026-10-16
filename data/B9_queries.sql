-- Appendix B.9. Database sha256: 851c599ba656280971dede42e2ca67e3d5def98e3ed39fcc6273045f9dcfaec3
-- arms excluded at the export: gemini_pro

-- B9_signal_to_noise_long.csv
SELECT arm, model_label, reasoning, pair_id, pair_label, panel_order,
       stated_gap, floor_used, floor_used_source, signal_to_noise,
       convention_stated, low_resolution, refused_reason
FROM duty_signal_to_noise
ORDER BY reasoning, arm, panel_order

-- B9_signal_to_noise_arm.csv
SELECT a.arm, a.n_pairs, a.n_pairs_refused, a.median_signal_to_noise
FROM duty_signal_to_noise_arm a

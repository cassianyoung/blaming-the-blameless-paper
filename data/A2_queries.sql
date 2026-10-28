-- Appendix A.2. Database sha256: e038ad003cc83a9a759deca959237109aaf36e93122f4dd6f96cc9e91b2a0ab3

-- the bicycle cell for one arm and role, with everything the appendix prints
SELECT c.ev, c.ev_all_draws, c.ev_source, c.n_draws, c.n_reasoning,
       c.answer_mass, c.answer_mass_source, c.mass_0_3, c.mass_0_3_source,
       c.reasoning_configured, a.readout, a.run, substr(a.sha256,1,16)
FROM cells c JOIN artefacts a ON a.id = c.artefact_id
WHERE a.arm = :arm AND c.role = :role AND c.question = 'BLAME' AND a.card = 'api'
  AND (c.family IS NULL OR c.family = 'bicycle')


-- the gate THIS row's delivery is gated by; never the other rule
SELECT g.verdict, g.rule_kind, g.stat_value, g.answer_mass, g.i_mean, g.rule_applied
FROM cell_gate g JOIN artefacts a ON a.id = g.artefact_id
WHERE a.arm = :arm AND g.question = 'BLAME' AND a.run = :run
  AND (g.family IS NULL OR g.family = 'bicycle')

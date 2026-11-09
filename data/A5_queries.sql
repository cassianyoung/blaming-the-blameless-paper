-- Appendix A.5. Database sha256: 5a2d048b9a0e6beaa8b086ed603aa762baf49b26381b4cdeadc39206d8f6b54e

-- one role on one scenario for one arm, with the reported reading in `ev`
SELECT c.role, c.ev, c.ev_all_draws, c.n_reasoning, c.n_draws, c.reasoning_configured,
       a.run, substr(a.sha256, 1, 16), a.readout
FROM cells c JOIN artefacts a ON a.id = c.artefact_id
WHERE a.arm = :arm AND c.family = :fam AND c.question = 'BLAME' AND a.card = 'api'


-- the gate THIS row's delivery is gated by, with every clause's input
SELECT g.verdict, g.rule_kind, g.stat_value, g.answer_mass, g.i_mean, a.run
FROM cell_gate g JOIN artefacts a ON a.id = g.artefact_id
WHERE a.arm = :arm AND g.question = 'BLAME' AND g.family IS :fam

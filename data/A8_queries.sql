-- Appendix A.8. Database sha256: 70ff118005cfa0e9aef3ddb9d93cc8b2d9fbe380f5a207b5c563746552a9fd2b

-- every channel for one arm, scenario and role: the two judgement questions, the blame
-- expected value and CAUSE, with the answer mass each probability rests on
SELECT c.question, c.p_yes, c.ev, c.answer_mass, c.answer_mass_source, c.n_draws,
       c.n_reasoning, c.reasoning_configured
FROM cells c JOIN artefacts a ON a.id = c.artefact_id
WHERE a.arm = :arm AND a.card = 'api' AND c.role = :role AND a.run = :run
  AND (CASE WHEN :fam = 'bicycle' THEN (c.family IS NULL OR c.family = 'bicycle')
            ELSE c.family = :fam END)


SELECT g.verdict FROM cell_gate g JOIN artefacts a ON a.id = g.artefact_id
WHERE a.arm = :arm AND g.question = 'BLAME' AND a.run = :run
  AND (CASE WHEN :fam = 'bicycle' THEN (g.family IS NULL OR g.family = 'bicycle')
            ELSE g.family = :fam END)

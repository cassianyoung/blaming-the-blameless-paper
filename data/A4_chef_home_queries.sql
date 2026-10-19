-- chef / home cook. Database sha256: 237a8a711cac2ef6ddde7c94ba500ebe0ecef19da7371bb694c3822f1eb6efdb

-- FAMILY CELL

-- A role's expected value and position on one prawns scenario, for one arm.
-- API arms and local instruct releases read on chat both land here;
-- cell_positions covers both because it is built on `cells`.
SELECT ev_mean, position FROM cell_positions
WHERE arm = :arm AND family = :fam AND role = :role AND question = 'BLAME'
  AND run = :run AND delivery = :delivery

-- STATED GAP (CMPN)

-- The stated gap: each side-by-side cell carries the chef-minus-home gap as ev and
-- its sd as ev_sd, so the mean over the two orders of mention is a query.
SELECT AVG(c.ev), AVG(c.ev_sd), COUNT(*)
FROM cells c JOIN artefacts a ON a.id = c.artefact_id
-- The side-by-side readings are held in two runs; both are included.
WHERE a.run IN ('duty_chef_home_comparison', 'deployed_added_models') AND a.arm = :arm AND c.question = 'CMPN'

-- SIDE-BY-SIDE (CMP3)

SELECT c.role, c.probs FROM cells c JOIN artefacts a ON a.id = c.artefact_id
WHERE a.arm = :arm AND c.question = 'CMP3' AND c.probs IS NOT NULL

-- CARELESS p(yes)

SELECT c.p_yes FROM cells c JOIN artefacts a ON a.id = c.artefact_id
WHERE a.arm = :arm AND c.family = :fam AND c.role = 'P0'
  AND c.question = 'CARELESS' AND a.run = :run

-- CHAT GATE

-- The gate is read from `cell_gate`, which is built over `cells` (so API arms are
-- gated) and chooses the gate rule from each row's own delivery. The query also
-- filters on delivery, because each local release has a worksheet and a chat
-- artefact. `stat_value` is mass(0-3) on a chat or api row.
SELECT g.verdict, g.stat_value, g.answer_mass, g.i_mean, g.rule_applied, g.n_mean
FROM cell_gate g JOIN artefacts a ON a.id = g.artefact_id
WHERE a.arm = :arm AND g.family = :fam AND g.question = 'BLAME' AND a.run = :run
  AND a.delivery = :delivery

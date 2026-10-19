-- Appendix A.6. Database sha256: 356f079a59309d0d5bd2897ae7494dd98f23313aa5794995adc6ce9190a21061

-- POINT

-- the point: the `positions` view's ratio of means over the five orderings, the same
-- construction B.1 and Figure 1 panel A use
SELECT role, ev_mean, n_mean, c_mean, n_orderings
FROM positions_value
WHERE run = 'local_frames' AND delivery = 'completion' AND question = 'BLAME'
  AND arm = :arm AND family = :fam

-- PER-ORDERING, for the interval

-- per-ordering ev for one arm and scenario, so the interval is PAIRED across orderings
SELECT o.frame, o.role, o.ev
FROM orderings o JOIN artefacts a ON a.id = o.artefact_id
WHERE a.arm = :arm AND a.run = 'local_frames' AND a.delivery = 'completion'
  AND o.family = :fam AND o.question = 'BLAME' AND o.ev IS NOT NULL

-- THE NOISE BAND

-- the noise band: 2.33 x AVG(sd) over P0, P1 and BYSTANDER across the five orderings
SELECT b.band, b.n_roles_in_band FROM band b JOIN artefacts a ON a.id = b.artefact_id
WHERE a.arm = :arm AND a.run = 'local_frames' AND a.delivery = 'completion'
  AND b.family = :fam AND b.question = 'BLAME'

-- GATE, by delivery

-- the COMPLETION rule, because every row here is a worksheet row
SELECT g.verdict, g.rule_kind FROM cell_gate g JOIN artefacts a ON a.id = g.artefact_id
WHERE a.arm = :arm AND a.run = 'local_frames' AND a.delivery = 'completion'
  AND g.family = :fam AND g.question = 'BLAME'

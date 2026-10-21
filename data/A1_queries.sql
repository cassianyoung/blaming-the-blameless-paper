-- tuning table. Database sha256: 7df3fb7c39fc0c088f5b6e09f3edf28e7b5b5d9ad3dd768416e193b380319393

-- ORDERINGS

-- Per-ordering ev for one arm on the bicycle worksheet. The five orderings are the unit:
-- a position is formed WITHIN each ordering so the five are paired observations.
SELECT o.frame, o.role, o.ev
FROM orderings o JOIN artefacts a ON a.id = o.artefact_id
WHERE a.run = 'local_frames' AND a.arm = :arm AND a.delivery = 'completion'
  AND o.family = 'bicycle' AND o.question = 'BLAME'
  AND (o.void IS NULL OR o.void = 0)

-- POSITION

-- The position, from the `positions` view plus its division (`positions_value`).
SELECT position, ev_mean, n_mean, c_mean
FROM positions_value
WHERE run = 'local_frames' AND arm = :arm AND delivery = 'completion'
  AND family = 'bicycle' AND role = :role AND question = 'BLAME'

-- BAND

-- The band is joined on the family: each worksheet arm has one artefact per scenario
-- family, so the join selects the bicycle artefact explicitly rather than relying on
-- a scalar subquery over the arm.
SELECT b.band FROM band b JOIN artefacts a ON a.id = b.artefact_id
WHERE a.run='local_frames' AND a.arm=:arm AND a.delivery='completion'
  AND b.family='bicycle' AND b.question='BLAME'

-- GATE

SELECT g.verdict FROM completion_gate g JOIN artefacts a ON a.id = g.artefact_id
WHERE a.run='local_frames' AND a.arm=:arm AND a.delivery='completion'
  AND g.family='bicycle' AND g.question='BLAME'

-- EARLIER BICYCLE READING

-- The earlier bicycle reading used a bank of its own, where `family` is NULL.
SELECT position FROM positions_value
WHERE run='local_tuning' AND arm=:arm AND delivery='completion' AND family IS NULL
  AND role='P0' AND question='BLAME'

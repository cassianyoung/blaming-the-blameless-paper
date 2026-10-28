-- Figure 1. Database sha256: b5488dfbf83d017145e95cb72494626672eb22fb14087090408bbd00a640b53c

-- PANEL A

-- Panel A: per ORDERING position for the four roles the panel needs, on the bicycle.
-- The position is formed WITHIN each ordering, so the five are paired observations.
SELECT a.arm, a.run, a.card, o.frame, o.role, o.ev
FROM orderings o JOIN artefacts a ON a.id = o.artefact_id
-- The bicycle is selected as the scenario family `bicycle` within the families
-- bank, not by bank name.
WHERE a.run = :run AND a.delivery = 'completion'
  AND o.family = 'bicycle'
  AND a.arm LIKE :armlike
  AND o.role IN ('N','C','P0','BYSTANDER')
  AND (o.void IS NULL OR o.void = 0)

-- PANEL B

-- Panel B: API arms on the bicycle, with draw accounting and the artefact sha.
SELECT a.arm, a.run, a.readout, a.sha256, a.superseded_by,
       c.role, c.question, c.ev, c.n_draws, c.n_reasoning, c.reasoning_share,
       c.thin, c.void
FROM cells c JOIN artefacts a ON a.id = c.artefact_id
WHERE a.card = 'api' AND a.bank_name LIKE '%excuse_bank%'
  AND c.role IN ('N','C','P0','P1','P1_R','BYSTANDER')

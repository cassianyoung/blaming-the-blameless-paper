-- Appendix A.7. Database sha256: d7a97c940acafbae66495dbe312379628cfd19091513a078e137b2a42507867b

-- POINT

SELECT role, ev_mean, n_mean, c_mean, n_orderings FROM positions_value
WHERE run = :run AND question = 'BLAME' AND arm = :arm AND delivery = :deliv
  AND family = :fam

-- PER-ORDERING, for the interval

SELECT o.frame, o.role, o.ev FROM orderings o JOIN artefacts a ON a.id = o.artefact_id
WHERE a.arm = :arm AND a.run = :run AND a.delivery = :deliv AND o.family = :fam
  AND o.question = 'BLAME' AND o.ev IS NOT NULL

-- THE NOISE BAND

SELECT b.band FROM band b JOIN artefacts a ON a.id = b.artefact_id
WHERE a.arm = :arm AND a.run = :run AND a.delivery = :deliv AND b.family = :fam
  AND b.question = 'BLAME'

-- GATE, by delivery

SELECT g.verdict, g.rule_kind FROM cell_gate g JOIN artefacts a ON a.id = g.artefact_id
WHERE a.arm = :arm AND a.run = :run AND a.delivery = :deliv AND g.family = :fam
  AND g.question = 'BLAME'

-- ADAPTER AND ARTEFACT SHA

SELECT a.adapter_digest, substr(a.sha256,1,16), a.run FROM artefacts a
WHERE a.arm = :arm AND a.run = :run AND a.delivery = :deliv ORDER BY a.id LIMIT 1

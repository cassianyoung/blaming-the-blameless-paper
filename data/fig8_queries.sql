-- frame by scenario. Database sha256: fe2ead2ac2da346bb790e3da2338b20561eeabd3b6108a1066dc5fdcc2a1aad3
-- chat gate:      N_mass_0_3 >= 0.8 AND answer_mass >= 0.7 AND (I >= 7.0 where read)
-- worksheet gate: (C-N) >= 3 bands AND answer mass >= 0.7
-- Imported from build_frame_table so the figure and the frame table share one definition.

-- SAME-LOAD ASSERTION

-- THE SAME-LOAD ASSERTION. Both frames must report one load.
SELECT w.load_seconds, c.load_seconds,
       w.load_shared_with IS c.load_shared_with,
       substr(w.sha256,1,16), substr(c.sha256,1,16)
FROM artefacts w JOIN artefacts c ON c.arm=w.arm AND c.run=w.run
WHERE w.run='local_frames' AND w.arm=:arm AND w.delivery='completion' AND c.delivery='chat'
  AND w.path LIKE :famlike AND c.path LIKE :famlike

-- WORKSHEET

-- Worksheet: the ratio of means over five orderings, from the positions view.
SELECT position, ev_mean FROM positions_value
WHERE run='local_frames' AND arm=:arm AND delivery='completion' AND family=:fam
  AND role=:role AND question='BLAME'

-- CHAT

-- Chat: one frame, no orderings, so the cells-based view.
SELECT position, ev_mean FROM cell_positions
WHERE run='local_frames' AND arm=:arm AND delivery='chat' AND family=:fam
  AND role=:role AND question='BLAME'

-- CHAT GATE

SELECT g.mass_0_3, g.answer_mass, g.i_mean, g.verdict, g.rule_applied
FROM chat_gate g JOIN artefacts a ON a.id=g.artefact_id
WHERE a.run='local_frames' AND a.arm=:arm AND a.delivery='chat' AND g.family=:fam
  AND g.question='BLAME'

-- WORKSHEET GATE

SELECT g.verdict, g.c_minus_n_bands, g.answer_mass, g.rule_applied
FROM completion_gate g JOIN artefacts a ON a.id=g.artefact_id
WHERE a.run='local_frames' AND a.arm=:arm AND a.delivery='completion' AND g.family=:fam
  AND g.question='BLAME'

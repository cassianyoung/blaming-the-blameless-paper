# Changelog

## Since v1.2 (main)

The PDF at the v1.2 tag cites release v1.1 (10.5281/zenodo.23733138), because a release cannot carry its own DOI. The PDF on main cites release v1.2 (10.5281/zenodo.24108122) and corrects two repeated phrases present in the tagged PDF (§1, §5). Nothing else differs.

## v1.2

### Corrections to v1.1

Replication: `replication/later_readings/question_word/` could not reproduce its own figures. Its
analysis names the bicycle scenario `bicycle`, its public label, while the cell files are named
`<model>__bicycle216.json`, so a re-run dropped the bicycle scenario on every model and wording
without an error (30 of 36 readings; it would have printed 0.550, 0.548, 29 of 29 and 29 of 30). The
folder now has `check_registered.py`, which reads each cell file by its real name. The registered
figures (ids 1076 to 1079: 0.565, 0.554, 34 of 34, 34 of 36) were computed before packaging and are
unaffected: the corrected re-run reproduces all four from the committed cells.

Text: §3 had a verb that disagreed with its subject and a stray possessive in the description of the duty test; both corrected.

### Added

The duty test on base checkpoints (`replication/later_readings/duty_on_base/`, pre-registered in `pre-registration/duty_on_base.md`): the duty test's six pairs read leg by leg on six pretrained checkpoints and their developer releases on the worksheet frame; its figures are ids 1133 to 1152 in `paper_numbers.csv`, and `check_registered.py` recomputes them from the committed per-cell results. Ids 1135 to 1137 (three per-family values the text gives as a range) are marked not printed. Id 1061 (fault blindness in eight of nine pretrained checkpoints) now names the abstract and §7, which link it. `data/` restamped at database 5a2d048b (sha headers only). The manuscript reports it in §1.2, §4.5, §6 and Appendix B.7 from v0.28; its PDF follows with v1.2.

## v1.1

PDF: `paper/blaming-the-blameless.pdf` at the v1.1 tag cites this repository's release v1.0 and its DOI (https://doi.org/10.5281/zenodo.23568407) in Code and data and in Young (2026a), because a release cannot carry its own DOI; the PDF on main cites release v1.1 and its DOI (https://doi.org/10.5281/zenodo.23733138). Nothing else differs.

### Corrections to v1.0

Text: §4.1 (p. 11 of v1.01) said four models without reasoning are cleared by the stated excuse on no scenario. Table A.5 shows three (Qwen3-235B, Qwen3-Next-80B, grok-4.3) under P1; Mistral-Small-24B is cleared on 3 of 5 under P1 and on none under P1-R. Corrected.

Links: grok-4.3’s bicycle position (§4.1) and “all 12 models” (§4.1) linked to the wrong registry entries; the numbers were correct. Corrected.

# Recovered figure renderers (Figures 1-9 of the manuscript)

These are the scripts that drew the manuscript's figures, reconstructed from the
claude.ai session transcripts (30 Sept - 14 Oct 2026) by replaying every write and every
in-place edit to each script in order. They were never on the AI_Ethics machine.

| Manuscript | Script | Reads (from the paper tree's data/ exports) | Wrote |
|---|---|---|---|
| Figure 1, re-scaling | fig1_rescaling.py | (values in the script) | Figure_measuring_the_effect |
| Figure 2, fault blindness | fig2_fault_blindness.py | fig1_panelA.csv, fig1_panelB.csv | Figure1_headline |
| Figure 3, across scenarios | fig3_across_scenarios.py | B5_across_scenarios_long.csv | Figure_deployed_by_scenario |
| Figure 4, role blindness | fig4_role_blindness.py | fig7_duty.csv | Figure_bias2_headline |
| Figure 5, prawns pair | fig5_prawns.py | chef_home.csv, chef_home_cmp3_probabilities.csv, fig7_duty.csv | Figure5_prawns |
| Figure 6, six conventions | fig6_six_conventions.py | fig7_duty.csv (+ panels) | Figure7_duty |
| Figure 7, noise | fig7_noise.py | fig7_duty.csv | Figure_wording_noise |
| Figure 8, frames | fig8_frames.py | frame_by_scenario.csv | Figure_frame_by_scenario |
| Figure 9, tuning | fig9_tuning.py | tuning_table.csv | Figure_tuning |

Caveats:
- Input paths are hard-coded to /mnt/user-data/uploads/ and outputs to
  /mnt/user-data/outputs/. Change both to the paper tree's data/ and figures/out/.
- Fidelity: every recorded edit was replayed, but two edit commands ended with shell
  errors after their edits (both on the prawns figure); the edits themselves applied.
  Verify each script by rendering it against the exports it was last run on and
  comparing with v0_4's image before using it on new data.
- Display names and arm lists are hard-coded in the scripts; new arms (Gemini 3.1 Pro
  in the excuse test) and dropped elements (the one-word columns in Figure 5; the
  sampled DeepSeek row in Figure 6) need adding or removing in code.

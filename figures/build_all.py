#!/usr/bin/env python3
"""Draw every figure of the manuscript (Figures 1-9) into figures/out/, from data/ only."""
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = ["fig1_rescaling.py", "fig2_fault_blindness.py", "fig3_across_scenarios.py",
           "fig4_role_blindness.py", "fig5_prawns.py", "fig6_six_conventions.py",
           "fig7_noise.py", "fig8_frames.py", "fig9_tuning.py"]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    for s in SCRIPTS:
        runpy.run_path(os.path.join(HERE, s), run_name="__main__")

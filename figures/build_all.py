#!/usr/bin/env python3
"""Draw every figure into figures/out/ (PNG plus the plotted values), from data/ only."""
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = ["fig1_bias1.py", "fig2_bias2_slack.py", "fig2_rescaling.py",
           "fig3_frames.py", "fig4_across_scenarios.py", "fig5_tuning.py",
           "fig6_chef_home.py"]

if __name__ == "__main__":
    for s in SCRIPTS:
        runpy.run_path(os.path.join(HERE, s), run_name="__main__")

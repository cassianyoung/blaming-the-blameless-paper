#!/usr/bin/env python3
"""Build every table into tables/out/ (CSV and Markdown), from data/ only."""
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = ["table3_deployed_models.py", "table_B1_tuning.py",
           "table_B2_deployed_bicycle.py", "table_B3_frames.py",
           "table_B4_chef_home.py", "table_B5_across_scenarios.py",
           "table_B6_bystander.py", "table_B7_yi.py", "table_B8_judgement.py",
           "table_B9_signal_to_noise.py",
           "table_B10_duty_by_model.py", "table_B11_syllogism.py"]

if __name__ == "__main__":
    for s in SCRIPTS:
        runpy.run_path(os.path.join(HERE, s), run_name="__main__")

#!/usr/bin/env python3
"""Build every table into tables/out/ (CSV and Markdown), from data/ only."""
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = ["tableB1_deployed_models.py", "tableB2_local_families.py",
           "table_A1_tuning.py",
           "table_A2_deployed_bicycle.py", "table_A3_frames.py",
           "table_A4_chef_home.py", "table_A5_across_scenarios.py",
           "table_A6_bystander.py", "table_A7_yi.py", "table_A8_judgement.py",
           "table_A9_duty_by_model.py", "table_A10_syllogism.py",
           "table4_syllogism.py"]

if __name__ == "__main__":
    for s in SCRIPTS:
        runpy.run_path(os.path.join(HERE, s), run_name="__main__")

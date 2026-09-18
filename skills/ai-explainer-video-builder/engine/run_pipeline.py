#!/usr/bin/env python3
"""Run the deterministic post-analysis pipeline. No semantic model calls occur here."""
from pathlib import Path
import argparse, subprocess, sys
from common import update_state

STEPS=[
    "validate_analysis.py",
    "semantic_match.py",
    "compile_plan.py",
    "make_subtitles.py",
    "prepare_narration.py",
    "render_slots.py",
    "assemble.py",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--stop-before-render",action="store_true"); args=ap.parse_args()
    project=Path(args.project).expanduser().resolve(); here=Path(__file__).resolve().parent
    update_state(project,"deterministic_pipeline","RUNNING")
    for step in STEPS:
        if args.stop_before_render and step=="render_slots.py": break
        print(f"\n=== {step} ===")
        p=subprocess.run([sys.executable,str(here/step),str(project)])
        if p.returncode!=0:
            update_state(project,"deterministic_pipeline","FAILED",f"{step} exit={p.returncode}")
            raise SystemExit(p.returncode)
    update_state(project,"deterministic_pipeline","COMPLETED")

if __name__=="__main__": main()

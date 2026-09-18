#!/usr/bin/env python3
from pathlib import Path
import argparse, json, shutil
from common import find_skill_root, write_json

DIRS = [
    "01_primary/video","01_primary/audio","01_primary/script",
    "02_screen_recordings","03_images","04_extra_videos","05_references",
    "06_brand_assets","07_background_music","08_sound_effects","09_voice_reference",
    "config","content_analysis","visual_plan","generated_assets/slides","generated_assets/motion",
    "generated_assets/ai_images","generated_assets/rendered_clips","logs",
    "output/01_final","output/02_timeline_clips","output/03_audio","output/04_subtitles",
    "output/05_source_assets","output/06_generated_assets","output/07_editing_data"
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--profile")
    args = ap.parse_args()
    root = Path(args.name).expanduser().resolve()
    for d in DIRS: (root/d).mkdir(parents=True, exist_ok=True)
    write_json(root/"config/workflow_state.json", {"version":2,"stage":"created","tasks":{}})
    src = Path(args.profile).expanduser().resolve() if args.profile else find_skill_root()/"config/default_profile.json"
    if src.exists(): shutil.copy2(src, root/"config/rule_profile.json")
    print(root)
    print("Add video/audio/script to 01_primary, then run scan_assets.py.")

if __name__ == "__main__": main()

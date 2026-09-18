#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil, subprocess
from common import read_json, update_state

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--all",action="store_true"); args=ap.parse_args()
    project=Path(args.project).expanduser().resolve(); idx=read_json(project/"config/asset_index.base.json")
    out=project/"config/contact_sheets"; out.mkdir(parents=True,exist_ok=True)
    update_state(project,"contact_sheets","RUNNING")
    for a in idx.get("assets",[]):
        if a.get("media_kind")!="video": continue
        if not args.all and not a.get("needs_visual_inspection"): continue
        src=project/a["path"]; dst=out/(Path(a["path"]).stem+".jpg")
        dur=float(a.get("duration") or 9); interval=max(dur/3,0.5)
        vf=f"fps=1/{interval},scale=640:-2,tile=3x1"
        cmd=["ffmpeg","-y","-i",str(src),"-vf",vf,"-frames:v","1",str(dst)]
        subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
    update_state(project,"contact_sheets","COMPLETED")
    print(out)

if __name__=="__main__": main()

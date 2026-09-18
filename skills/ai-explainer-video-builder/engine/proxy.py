#!/usr/bin/env python3
from pathlib import Path
import argparse, subprocess
from common import read_json, update_state

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--height",type=int,default=540); args=ap.parse_args(); project=Path(args.project).expanduser().resolve()
    manifest=read_json(project/"config/project_manifest.json"); outdir=project/"config/proxies"; outdir.mkdir(parents=True,exist_ok=True)
    update_state(project,"proxy","RUNNING")
    count=0
    for group in manifest.get("groups",{}).values():
        for a in group:
            if a.get("media_kind")!="video": continue
            src=project/a["path"]; dst=outdir/(Path(a["path"]).stem+"_proxy.mp4")
            subprocess.run(["ffmpeg","-y","-i",str(src),"-vf",f"scale=-2:{args.height}","-c:v","libx264","-preset","veryfast","-crf","28","-an",str(dst)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=600); count+=1
    update_state(project,"proxy","COMPLETED",f"{count} proxies"); print(outdir)

if __name__=="__main__": main()

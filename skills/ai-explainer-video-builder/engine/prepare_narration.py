#!/usr/bin/env python3
from pathlib import Path
import argparse, json, subprocess, tempfile
from common import read_json, update_state

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); args=ap.parse_args(); project=Path(args.project).expanduser().resolve()
    manifest=read_json(project/"config/project_manifest.json"); primary=manifest["primary_source"]; out=project/"output/03_audio/narration.wav"; out.parent.mkdir(parents=True,exist_ok=True)
    update_state(project,"prepare_narration","RUNNING")
    if primary["type"]=="script":
        update_state(project,"prepare_narration","WAITING_USER","Script primary requires TTS/voice provider before deterministic render")
        print("Script primary: narration generation requires an available TTS/authorized voice-clone capability."); return
    src=project/primary["path"]; ranges=read_json(project/"content_analysis/narration_keep_ranges.json").get("ranges",[])
    if not ranges:
        raise SystemExit("No narration keep ranges. Run compile_plan.py first.")
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); parts=[]
        for i,r in enumerate(ranges,1):
            p=td/f"part_{i:04d}.wav"; dur=max(.05,float(r["source_end"])-float(r["source_start"]))
            cmd=["ffmpeg","-y","-ss",str(r["source_start"]),"-t",str(dur),"-i",str(src),"-vn","-ac","1","-ar","48000","-c:a","pcm_s16le",str(p)]
            subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180); parts.append(p)
        lst=td/"concat.txt"; lst.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts),encoding="utf-8")
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c:a","pcm_s16le",str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=300)
    update_state(project,"prepare_narration","COMPLETED"); print(out)

if __name__=="__main__": main()

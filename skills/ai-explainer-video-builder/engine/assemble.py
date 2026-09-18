#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil, subprocess, tempfile
from common import read_json, load_profile, update_state

def run(cmd,timeout=1200):
    return subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)

def escape_subtitle_path(p:Path):
    s=p.resolve().as_posix().replace("'","\\'")
    if len(s)>1 and s[1]==':': s=s[0]+"\\:"+s[2:]
    return s

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); args=ap.parse_args(); project=Path(args.project).expanduser().resolve()
    profile=load_profile(project); fps=int(profile.get("output",{}).get("fps",30)); clips=sorted((project/"output/02_timeline_clips").glob("*.mp4"))
    if not clips: raise SystemExit("No timeline clips. Run render_slots.py first.")
    finaldir=project/"output/01_final"; finaldir.mkdir(parents=True,exist_ok=True); update_state(project,"assemble","RUNNING")
    visual=finaldir/"_visual_concat.mp4"; no_sub=finaldir/"final_no_subtitles.mp4"; master=finaldir/"final_master.mp4"
    with tempfile.TemporaryDirectory() as td:
        lst=Path(td)/"concat.txt"; lst.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in clips),encoding="utf-8")
        run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-an","-r",str(fps),"-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",str(visual)])
    narration=project/"output/03_audio/narration.wav"; bgms=sorted((project/"07_background_music").glob("*")); bgm=bgms[0] if bgms else None
    if narration.exists():
        if bgm and bgm.is_file():
            run(["ffmpeg","-y","-i",str(visual),"-i",str(narration),"-stream_loop","-1","-i",str(bgm),"-filter_complex","[1:a]volume=1.0[n];[2:a]volume=0.09[b];[n][b]amix=inputs=2:duration=first:dropout_transition=2[a]","-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest",str(no_sub)])
        else:
            run(["ffmpeg","-y","-i",str(visual),"-i",str(narration),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-shortest",str(no_sub)])
    else:
        shutil.copy2(visual,no_sub)
    srt=project/"output/04_subtitles/subtitles.srt"
    if srt.exists() and srt.stat().st_size>0:
        try:
            run(["ffmpeg","-y","-i",str(no_sub),"-vf",f"subtitles='{escape_subtitle_path(srt)}'","-c:v","libx264","-crf","18","-preset","medium","-c:a","copy",str(master)])
        except Exception:
            shutil.copy2(no_sub,master)
    else: shutil.copy2(no_sub,master)
    visual.unlink(missing_ok=True); update_state(project,"assemble","COMPLETED"); print(master)

if __name__=="__main__": main()

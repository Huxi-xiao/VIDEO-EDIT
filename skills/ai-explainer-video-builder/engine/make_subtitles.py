#!/usr/bin/env python3
from pathlib import Path
import argparse
from common import read_json

def stamp(s):
    ms=int(round(float(s)*1000)); h=ms//3600000; ms%=3600000; m=ms//60000; ms%=60000; sec=ms//1000; ms%=1000
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); args=ap.parse_args(); project=Path(args.project).expanduser().resolve()
    slots=read_json(project/"output/07_editing_data/timeline.json").get("slots",[]); out=project/"output/04_subtitles/subtitles.srt"; out.parent.mkdir(parents=True,exist_ok=True)
    lines=[]; n=1
    for s in slots:
        text=(s.get("transcript") or "").strip()
        if not text: continue
        lines += [str(n),f"{stamp(s['start'])} --> {stamp(s['end'])}",text,""]; n+=1
    out.write_text("\n".join(lines),encoding="utf-8"); print(out)

if __name__=="__main__": main()

#!/usr/bin/env python3
from pathlib import Path
import argparse, re, subprocess
from common import write_json

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("input"); ap.add_argument("--noise",default="-35dB"); ap.add_argument("--duration",type=float,default=.6); ap.add_argument("--output",default="silence.json"); args=ap.parse_args()
    p=subprocess.run(["ffmpeg","-i",args.input,"-af",f"silencedetect=noise={args.noise}:d={args.duration}","-f","null","-"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    starts=[float(x) for x in re.findall(r"silence_start: ([0-9.]+)",p.stderr)]; ends=[float(x) for x in re.findall(r"silence_end: ([0-9.]+)",p.stderr)]
    items=[]
    for i,s in enumerate(starts): items.append({"start":s,"end":ends[i] if i<len(ends) else None})
    write_json(Path(args.output),{"silences":items}); print(args.output)

if __name__=="__main__": main()

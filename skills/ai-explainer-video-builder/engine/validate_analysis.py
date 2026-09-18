#!/usr/bin/env python3
from pathlib import Path
import argparse
from common import read_json

ALLOWED_VISUAL={"AROLL","SCREEN","MEDIA","SLIDE","HAMMER","MOTION","AI_IMAGE"}
ALLOWED_STAGE={"BEFORE","ACTION","PROCESS","RESULT","AFTER","UNKNOWN"}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); args=ap.parse_args()
    project=Path(args.project).expanduser().resolve(); path=project/"content_analysis/master_analysis.json"
    data=read_json(path); errors=[]
    if not data.get("project"): errors.append("missing project")
    if not isinstance(data.get("sections"),list) or not data.get("sections"): errors.append("sections missing/empty")
    prev=-1.0
    for i,s in enumerate(data.get("sections",[]),1):
        tag=f"section[{i}]"
        for k in ["id","source_start","source_end","keep","content_type","importance","transcript","visual"]:
            if k not in s: errors.append(f"{tag}: missing {k}")
        try:
            a=float(s.get("source_start",0)); b=float(s.get("source_end",0))
            if b<=a: errors.append(f"{tag}: source_end <= source_start")
            if a<prev-0.01: errors.append(f"{tag}: sections not ordered")
            prev=a
        except Exception: errors.append(f"{tag}: bad timestamps")
        v=s.get("visual",{})
        if v.get("preferred_type") not in ALLOWED_VISUAL: errors.append(f"{tag}: invalid visual type")
        q=v.get("match_query",{})
        if q.get("stage","UNKNOWN") not in ALLOWED_STAGE: errors.append(f"{tag}: invalid stage")
        if s.get("importance") not in {"A","B","C"}: errors.append(f"{tag}: invalid importance")
    if errors:
        print("INVALID MASTER ANALYSIS")
        for e in errors: print("-",e)
        raise SystemExit(2)
    print(f"OK: {len(data['sections'])} sections")

if __name__=="__main__": main()

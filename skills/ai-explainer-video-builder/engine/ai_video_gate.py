#!/usr/bin/env python3
"""Approval ledger only. Never calls a video generation provider."""
from pathlib import Path
import argparse, time
from common import read_json, write_json

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--slot",required=True); ap.add_argument("--action",choices=["request","approve","reject","fallback"],required=True); ap.add_argument("--prompt",default=""); ap.add_argument("--duration",type=float); ap.add_argument("--provider",default="unknown"); ap.add_argument("--estimated-cost",default="unknown"); ap.add_argument("--fallback",default="ai_image_motion"); args=ap.parse_args()
    project=Path(args.project).expanduser().resolve(); path=project/"config/ai_video_approvals.json"; data=read_json(path,{"requests":{}}); r=data.setdefault("requests",{}).setdefault(args.slot,{})
    now=time.strftime("%Y-%m-%dT%H:%M:%S")
    if args.action=="request": r.update({"status":"WAITING_USER","prompt":args.prompt,"duration":args.duration,"provider":args.provider,"estimated_cost":args.estimated_cost,"fallback":args.fallback,"updated_at":now})
    elif args.action=="approve": r.update({"status":"APPROVED","approved_at":now})
    elif args.action=="reject": r.update({"status":"REJECTED","updated_at":now})
    else: r.update({"status":"FALLBACK","fallback":args.fallback,"updated_at":now})
    write_json(path,data); print(r)

if __name__=="__main__": main()

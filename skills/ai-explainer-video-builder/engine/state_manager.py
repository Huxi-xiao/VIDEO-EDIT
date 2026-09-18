#!/usr/bin/env python3
from pathlib import Path
import argparse
from common import read_json, update_state

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--task"); ap.add_argument("--status"); ap.add_argument("--note",default=""); ap.add_argument("--list",action="store_true"); args=ap.parse_args(); project=Path(args.project).expanduser().resolve()
    if args.list:
        import json; print(json.dumps(read_json(project/"config/workflow_state.json"),ensure_ascii=False,indent=2)); return
    if not args.task or not args.status: raise SystemExit("--task and --status required")
    update_state(project,args.task,args.status,args.note)

if __name__=="__main__": main()

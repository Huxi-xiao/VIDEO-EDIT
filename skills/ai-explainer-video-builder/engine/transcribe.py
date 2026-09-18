#!/usr/bin/env python3
from pathlib import Path
import argparse, json, shutil, subprocess
from common import read_json, write_json, update_state

def primary_path(project):
    m=read_json(project/"config/project_manifest.json")
    p=m["primary_source"]
    return p["type"], project/p["path"]

def from_faster_whisper(src, model_name):
    from faster_whisper import WhisperModel
    model=WhisperModel(model_name, device="auto", compute_type="auto")
    segs, info=model.transcribe(str(src), vad_filter=True)
    out=[]
    for s in segs: out.append({"start":round(s.start,3),"end":round(s.end,3),"text":s.text.strip()})
    return {"language":getattr(info,"language",None),"segments":out}

def from_cli(src, outdir, model_name):
    outdir.mkdir(parents=True,exist_ok=True)
    subprocess.run(["whisper",str(src),"--model",model_name,"--output_dir",str(outdir),"--output_format","json"],check=True)
    data=json.loads((outdir/(src.stem+".json")).read_text(encoding="utf-8"))
    return {"language":data.get("language"),"segments":[{"start":s["start"],"end":s["end"],"text":s["text"].strip()} for s in data.get("segments",[])]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--model",default="small"); args=ap.parse_args()
    project=Path(args.project).expanduser().resolve(); typ,src=primary_path(project)
    if typ=="script":
        text=src.read_text(encoding="utf-8",errors="ignore")
        write_json(project/"content_analysis/transcript.json",{"language":"unknown","segments":[],"script":text})
        print("Script primary: transcript.json created without timestamps."); return
    update_state(project,"transcribe","RUNNING")
    try:
        try: result=from_faster_whisper(src,args.model)
        except Exception:
            if not shutil.which("whisper"): raise
            result=from_cli(src, project/"content_analysis/whisper_tmp", args.model)
        write_json(project/"content_analysis/transcript.json",result)
        md=[]
        for s in result["segments"]: md.append(f"[{s['start']:.3f}-{s['end']:.3f}] {s['text']}")
        (project/"content_analysis/transcript_raw.md").write_text("\n".join(md),encoding="utf-8")
        packet=read_json(project/"config/analysis_packet.json")
        packet["transcript_file"]="content_analysis/transcript.json"
        packet["transcript_segments"]=result["segments"]
        write_json(project/"config/analysis_packet.json",packet)
        update_state(project,"transcribe","COMPLETED")
        print(project/"content_analysis/transcript.json")
    except Exception as exc:
        update_state(project,"transcribe","FAILED",str(exc)); raise

if __name__=="__main__": main()

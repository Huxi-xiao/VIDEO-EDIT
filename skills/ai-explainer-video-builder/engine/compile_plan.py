#!/usr/bin/env python3
from pathlib import Path
import argparse, csv, json
from common import read_json, write_json, update_state

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); args=ap.parse_args()
    project=Path(args.project).expanduser().resolve(); analysis=read_json(project/"content_analysis/master_analysis.json")
    update_state(project,"compile_plan","RUNNING")
    timeline=[]; t=0.0; slot=1
    keep_ranges=[]
    for s in analysis.get("sections",[]):
        if not s.get("keep",True): continue
        a=float(s.get("source_start",0)); b=float(s.get("source_end",a)); dur=max(0.1,b-a)
        v=s.get("visual",{})
        item={
            "slot":slot,"section_id":s.get("id"),"start":round(t,3),"end":round(t+dur,3),"duration":round(dur,3),
            "source_start":a,"source_end":b,"content_type":s.get("content_type"),"importance":s.get("importance"),
            "transcript":s.get("transcript", ""),"visual_type":v.get("preferred_type","AROLL"),
            "layout":v.get("layout") or "statement_left","headline":v.get("headline") or s.get("concept", ""),
            "body":v.get("body",[]),"density":v.get("density","medium"),"motion":v.get("motion","Fade"),
            "asset_path":v.get("matched_asset_path"),"match_score":v.get("match_score"),
            "ai_image_prompt":v.get("ai_image_prompt","")
        }
        timeline.append(item); keep_ranges.append({"source_start":a,"source_end":b,"output_start":round(t,3),"output_end":round(t+dur,3)})
        t += dur; slot += 1
    outdir=project/"output/07_editing_data"; outdir.mkdir(parents=True,exist_ok=True)
    write_json(outdir/"timeline.json",{"duration":round(t,3),"slots":timeline})
    write_json(project/"visual_plan/visual_slots.json",{"duration":round(t,3),"slots":timeline})
    write_json(project/"content_analysis/narration_keep_ranges.json",{"ranges":keep_ranges})
    with (outdir/"timeline.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(["slot","start","end","duration","visual_type","asset_path","headline","transcript"])
        for x in timeline: w.writerow([x["slot"],x["start"],x["end"],x["duration"],x["visual_type"],x.get("asset_path") or "",x.get("headline") or "",x.get("transcript") or ""])
    md=["# Storyboard",""]
    for x in timeline:
        md += [f"## {x['slot']:03d} · {x['visual_type']} · {x['start']:.2f}-{x['end']:.2f}s",f"- 口播：{x['transcript']}",f"- 画面：{x.get('headline') or '-'}",f"- 素材：{x.get('asset_path') or 'generated/programmatic'}",""]
    (outdir/"storyboard.md").write_text("\n".join(md),encoding="utf-8")
    update_state(project,"compile_plan","COMPLETED"); print(outdir/"timeline.json")

if __name__=="__main__": main()

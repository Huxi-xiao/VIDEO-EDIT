#!/usr/bin/env python3
from pathlib import Path
import argparse, math, re
from common import read_json, write_json, load_profile, update_state

def norm(s): return (s or "").lower().strip()

def features(text):
    s=norm(text)
    words=set(re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]",s))
    zh="".join(re.findall(r"[\u4e00-\u9fff]",s))
    bigrams={zh[i:i+2] for i in range(max(0,len(zh)-1))}
    return words|bigrams

def sim(a,b):
    A=features(a); B=features(b)
    if not A or not B: return 0.0
    return len(A&B)/math.sqrt(len(A)*len(B))

def merged_assets(project, analysis):
    base=read_json(project/"config/asset_index.base.json").get("assets",[])
    annotations={x.get("path"):x for x in analysis.get("asset_annotations",[])}
    out=[]
    for a in base:
        z=dict(a); z.update(annotations.get(a["path"],{})); out.append(z)
    return out

def suitability(preferred, asset):
    fk=asset.get("folder_kind")
    if preferred=="SCREEN": return 1.0 if fk=="screen_recording" else 0.2
    if preferred=="MEDIA": return 1.0 if fk in {"image","extra_video"} else 0.4
    return 0.5

def score(section, asset, weights, previous_order=None):
    q=section.get("visual",{}).get("match_query",{})
    filename=" ".join(asset.get("tokens",[]))+" "+asset.get("filename","")
    qtxt=" ".join([q.get("action",""),q.get("object",""),q.get("software","")]+q.get("keywords",[]))
    atxt=" ".join([asset.get("label",""),asset.get("action",""),asset.get("object",""),asset.get("software","")]+asset.get("keywords",[]))
    filename_score=sim(qtxt,filename)
    semantic_score=sim(qtxt,atxt or filename)
    qs=q.get("stage","UNKNOWN"); ast=asset.get("stage",asset.get("stage_hint","UNKNOWN"))
    stage_score=1.0 if qs!="UNKNOWN" and qs==ast else (0.55 if qs=="UNKNOWN" or ast=="UNKNOWN" else 0.0)
    media_score=suitability(section.get("visual",{}).get("preferred_type"),asset)
    if previous_order is None: seq=0.6
    else:
        diff=asset.get("order",0)-previous_order
        seq=1.0 if diff>=0 and diff<=3 else (0.5 if diff>=0 else 0.15)
    total=(weights["filename"]*filename_score+weights["semantic"]*semantic_score+weights["stage"]*stage_score+
           weights["media_type"]*media_score+weights["sequence"]*seq)
    return round(total,4), {"filename":round(filename_score,3),"semantic":round(semantic_score,3),"stage":stage_score,"media_type":media_score,"sequence":seq}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); args=ap.parse_args()
    project=Path(args.project).expanduser().resolve(); analysis_path=project/"content_analysis/master_analysis.json"
    analysis=read_json(analysis_path); profile=load_profile(project); cfg=profile.get("matching",{})
    weights=cfg.get("weights",{"filename":.3,"semantic":.3,"stage":.2,"media_type":.1,"sequence":.1}); threshold=float(cfg.get("minimum_score",.65))
    assets=merged_assets(project,analysis); previous_order=None
    update_state(project,"semantic_match","RUNNING")
    results=[]
    for s in analysis.get("sections",[]):
        v=s.get("visual",{}); pref=v.get("preferred_type")
        result={"section_id":s.get("id"),"preferred_type":pref,"match":None}
        if pref in {"SCREEN","MEDIA"}:
            candidates=[]
            for a in assets:
                sc,detail=score(s,a,weights,previous_order)
                candidates.append((sc,a,detail))
            candidates.sort(key=lambda x:x[0],reverse=True)
            if candidates and candidates[0][0]>=threshold:
                sc,a,detail=candidates[0]; previous_order=a.get("order")
                result["match"]={"path":a["path"],"score":sc,"detail":detail,"stage":a.get("stage",a.get("stage_hint"))}
                v["matched_asset_path"]=a["path"]; v["match_score"]=sc
            else:
                v["matched_asset_path"]=None; v["match_score"]=candidates[0][0] if candidates else 0
                v["fallback_reason"]="No user asset exceeded semantic threshold"
                v["preferred_type"]="MOTION" if s.get("content_type") in {"STEP","COMPARISON","DEMO"} else "SLIDE"
        results.append(result)
    write_json(analysis_path,analysis); write_json(project/"content_analysis/asset_match.json",{"threshold":threshold,"results":results})
    update_state(project,"semantic_match","COMPLETED")
    print(project/"content_analysis/asset_match.json")

if __name__=="__main__": main()

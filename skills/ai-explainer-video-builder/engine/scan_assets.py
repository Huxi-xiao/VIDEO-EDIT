#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys, time
from common import ffprobe, duration_seconds, write_json, update_state, load_profile

FOLDERS = {
    "primary_video":"01_primary/video", "primary_audio":"01_primary/audio", "primary_script":"01_primary/script",
    "screen_recording":"02_screen_recordings", "image":"03_images", "extra_video":"04_extra_videos",
    "reference":"05_references", "brand_asset":"06_brand_assets", "background_music":"07_background_music",
    "sound_effect":"08_sound_effects", "voice_reference":"09_voice_reference"
}
VIDEO={".mp4",".mov",".mkv",".avi",".webm",".m4v"}; AUDIO={".wav",".mp3",".m4a",".aac",".flac",".ogg"}
IMAGE={".png",".jpg",".jpeg",".webp",".gif",".svg"}; SCRIPT={".txt",".md",".rtf"}
STAGE_HINTS = {
    "BEFORE":["before","之前","原来","旧"], "RESULT":["result","结果","完成","输出","最终","成功"],
    "AFTER":["after","之后"], "ACTION":["action","点击","上传","输入","打开","选择","拖入","生成","操作"],
    "PROCESS":["process","处理中","加载","等待","过程"]
}

def clean_tokens(name):
    stem = Path(name).stem.lower()
    parts = re.split(r"[\s_\-\.]+", stem)
    return [p for p in parts if p and not p.isdigit()]

def infer_stage(name):
    low=name.lower()
    for stage, hints in STAGE_HINTS.items():
        if any(h.lower() in low for h in hints): return stage
    return "UNKNOWN"

def media_kind(path):
    s=path.suffix.lower()
    if s in VIDEO: return "video"
    if s in AUDIO: return "audio"
    if s in IMAGE: return "image"
    if s in SCRIPT: return "script"
    return "other"

def record(root, folder_kind, path, order):
    meta = ffprobe(path) if media_kind(path) in {"video","audio"} else {}
    return {
        "id": f"A{order:03d}", "path": str(path.relative_to(root)).replace("\\","/"), "folder_kind": folder_kind,
        "media_kind": media_kind(path), "filename": path.name, "tokens": clean_tokens(path.name),
        "stage_hint": infer_stage(path.name), "duration": duration_seconds(meta), "probe": meta,
        "order": order, "needs_visual_inspection": len(clean_tokens(path.name)) < 2
    }

def choose_primary(groups):
    for key, typ in [("primary_video","video"),("primary_audio","audio"),("primary_script","script")]:
        if groups.get(key): return {"type":typ,"path":groups[key][0]["path"]}
    return None

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); args=ap.parse_args()
    root=Path(args.project).expanduser().resolve()
    if not root.exists(): raise SystemExit("Project not found")
    update_state(root,"scan_assets","RUNNING")
    groups={}; order=1
    for kind, rel in FOLDERS.items():
        items=[]; p=root/rel
        if p.exists():
            for f in sorted(x for x in p.rglob("*") if x.is_file()):
                items.append(record(root,kind,f,order)); order += 1
        groups[kind]=items
    primary=choose_primary(groups)
    if not primary:
        update_state(root,"scan_assets","FAILED","No primary source")
        raise SystemExit("No primary narrative source. Add video, audio, or script.")
    manifest={"project":root.name,"scanned_at":time.strftime("%Y-%m-%dT%H:%M:%S"),"primary_source":primary,"groups":groups}
    assets=[]
    for k in ["screen_recording","image","extra_video"]: assets.extend(groups[k])
    profile=load_profile(root)
    base_index={"project":root.name,"assets":assets,"matching":profile.get("matching",{})}
    packet={
        "project":root.name,"primary":primary,
        "supporting_assets":[{k:a[k] for k in ["id","path","folder_kind","media_kind","filename","tokens","stage_hint","duration","order","needs_visual_inspection"]} for a in assets],
        "instructions":"Use filenames first. Only inspect assets where needs_visual_inspection=true or semantics remain ambiguous. Master Analysis must be one semantic pass."
    }
    write_json(root/"config/project_manifest.json",manifest)
    write_json(root/"config/asset_index.base.json",base_index)
    write_json(root/"config/analysis_packet.json",packet)
    update_state(root,"scan_assets","COMPLETED")
    print(root/"config/analysis_packet.json")

if __name__=="__main__": main()

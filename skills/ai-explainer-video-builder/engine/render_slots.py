#!/usr/bin/env python3
from pathlib import Path
import argparse, json, os, re, shutil, subprocess, tempfile
from common import read_json, load_profile, find_skill_root, update_state, ffprobe

VIDEO_EXT={".mp4",".mov",".mkv",".avi",".webm",".m4v"}
IMAGE_EXT={".png",".jpg",".jpeg",".webp"}

def slug(s):
    s=(s or "slot").strip().replace(" ","_")
    return re.sub(r"[^\w\-\u4e00-\u9fff]+","",s)[:32] or "slot"

def run(cmd, timeout=600):
    return subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)

def standard_vf(w,h,fps):
    return f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,fps={fps},format=yuv420p"

def render_video(src,dst,dur,w,h,fps,start=0):
    cmd=["ffmpeg","-y","-ss",str(max(0,start)),"-stream_loop","-1","-i",str(src),"-t",str(dur),"-an","-vf",standard_vf(w,h,fps),"-c:v","libx264","-preset","medium","-crf","18",str(dst)]
    run(cmd,timeout=max(180,int(dur*12+90)))

def render_image(src,dst,dur,w,h,fps):
    frames=max(1,int(dur*fps));
    vf=(f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"zoompan=z='min(zoom+0.00035,1.055)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={fps},format=yuv420p")
    run(["ffmpeg","-y","-loop","1","-i",str(src),"-t",str(dur),"-an","-vf",vf,"-c:v","libx264","-crf","18",str(dst)],timeout=max(180,int(dur*12+90)))

def find_font():
    candidates=[
        "C:/Windows/Fonts/msyh.ttc","C:/Windows/Fonts/msyhbd.ttc",
        "/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc","/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for p in candidates:
        if Path(p).exists(): return p
    return None

def fallback_card(slot,dst,dur,w,h,fps,tokens):
    try:
        from PIL import Image, ImageDraw, ImageFont
        bg=tokens.get("background","#F7F7F5"); fg=tokens.get("text_primary","#111111"); sec=tokens.get("text_secondary","#696969")
        im=Image.new("RGB",(w,h),bg); d=ImageDraw.Draw(im); fp=find_font()
        head=slot.get("headline") or " "; body=slot.get("body") or []
        size=180 if slot.get("visual_type")=="HAMMER" else 78
        font=ImageFont.truetype(fp,size) if fp else ImageFont.load_default(); small=ImageFont.truetype(fp,38) if fp else ImageFont.load_default()
        if slot.get("visual_type")=="HAMMER":
            bb=d.textbbox((0,0),head,font=font); x=(w-(bb[2]-bb[0]))/2; y=(h-(bb[3]-bb[1]))/2-20; d.text((x,y),head,font=font,fill=fg)
            if body:
                bb2=d.textbbox((0,0),body[0],font=small); d.text(((w-(bb2[2]-bb2[0]))/2,y+230),body[0],font=small,fill=sec)
        else:
            d.text((160,300),head,font=font,fill=fg)
            yy=430
            for line in body[:4]: d.text((165,yy),line,font=small,fill=sec); yy+=70
        png=dst.with_suffix(".fallback.png"); im.save(png); render_image(png,dst,dur,w,h,fps); png.unlink(missing_ok=True)
    except Exception:
        run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=0xF7F7F5:s={w}x{h}:r={fps}","-t",str(dur),"-an","-c:v","libx264","-pix_fmt","yuv420p",str(dst)],timeout=120)

def render_remotion(slot,dst,dur,w,h,fps,tokens,renderer):
    frames=max(1,int(round(dur*fps)))
    props={"visualType":slot.get("visual_type","SLIDE"),"layout":slot.get("layout") or "statement_left","headline":slot.get("headline") or "", "body":slot.get("body") or [], "tokens":tokens}
    with tempfile.NamedTemporaryFile("w",suffix=".json",delete=False,encoding="utf-8") as f:
        json.dump(props,f,ensure_ascii=False); prop_path=f.name
    try:
        cmd=["npx","remotion","render","src/index.tsx","VisualSlot",str(dst),f"--props={prop_path}",f"--frames=0-{frames-1}","--codec=h264","--pixel-format=yuv420p","--overwrite"]
        subprocess.run(cmd,cwd=renderer,check=True,timeout=max(240,int(dur*20+120)),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    finally:
        Path(prop_path).unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project"); args=ap.parse_args(); project=Path(args.project).expanduser().resolve()
    profile=load_profile(project); outcfg=profile.get("output",{}); w=int(outcfg.get("width",1920)); h=int(outcfg.get("height",1080)); fps=int(outcfg.get("fps",30))
    timeline=read_json(project/"output/07_editing_data/timeline.json").get("slots",[]); manifest=read_json(project/"config/project_manifest.json"); primary=project/manifest["primary_source"]["path"]
    theme=profile.get("visual",{}).get("design_system","light_minimal"); token_file="design_tokens.dark.json" if theme=="dark_tech" else "design_tokens.light.json"; tokens=read_json(find_skill_root()/"config"/token_file)
    renderer=find_skill_root()/"renderer"; remotion_ready=shutil.which("npx") is not None and (renderer/"node_modules").exists()
    outdir=project/"output/02_timeline_clips"; outdir.mkdir(parents=True,exist_ok=True); exceptions=[]
    update_state(project,"render_slots","RUNNING")
    for slot in timeline:
        n=int(slot["slot"]); typ=slot.get("visual_type","SLIDE"); name=f"{n:03d}_{typ}_{slug(slot.get('headline') or slot.get('content_type'))}.mp4"; dst=outdir/name
        if dst.exists() and dst.stat().st_size>4096: continue
        dur=float(slot.get("duration",1)); ok=False; last=""
        for attempt in range(2):
            try:
                if typ=="AROLL" and manifest["primary_source"]["type"]=="video":
                    render_video(primary,dst,dur,w,h,fps,float(slot.get("source_start",0)))
                elif typ in {"SCREEN","MEDIA"} and slot.get("asset_path"):
                    src=project/slot["asset_path"]
                    if src.suffix.lower() in VIDEO_EXT: render_video(src,dst,dur,w,h,fps,0)
                    elif src.suffix.lower() in IMAGE_EXT: render_image(src,dst,dur,w,h,fps)
                    else: raise RuntimeError(f"Unsupported media {src}")
                elif typ=="AI_IMAGE":
                    candidates=list((project/"generated_assets/ai_images").glob(f"{n:03d}*"))
                    if not candidates: raise RuntimeError("AI image asset missing")
                    render_image(candidates[0],dst,dur,w,h,fps)
                else:
                    if not remotion_ready: raise RuntimeError("Remotion dependencies not installed")
                    render_remotion(slot,dst,dur,w,h,fps,tokens,renderer)
                ok=True; break
            except Exception as exc: last=str(exc)
        if not ok:
            fallback_card(slot,dst,dur,w,h,fps,tokens)
            exceptions.append({"slot":n,"planned":typ,"fallback":"STATIC_CARD","reason":last})
    report=project/"output/07_editing_data/exception_report.md"; lines=["# Exception Report",""]
    if not exceptions: lines.append("No slot fallbacks were required.")
    for e in exceptions: lines += [f"## Slot {e['slot']:03d}",f"- planned: {e['planned']}",f"- fallback: {e['fallback']}",f"- reason: {e['reason']}",""]
    report.write_text("\n".join(lines),encoding="utf-8")
    update_state(project,"render_slots","COMPLETED",f"fallbacks={len(exceptions)}"); print(outdir)

if __name__=="__main__": main()

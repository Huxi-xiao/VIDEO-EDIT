from __future__ import annotations
import json, os, subprocess, time, shlex
from pathlib import Path
from typing import Any

STATES = {"PENDING","RUNNING","COMPLETED","FAILED","SKIPPED","WAITING_USER","INTERRUPTED"}


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run(cmd, timeout=600, check=True, capture=True):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    return subprocess.run(
        cmd,
        timeout=timeout,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def ffprobe(path: Path):
    try:
        p = run([
            "ffprobe","-v","error","-show_entries",
            "format=duration:stream=index,codec_type,width,height,r_frame_rate,sample_rate,channels",
            "-of","json", str(path)
        ], timeout=60)
        return json.loads(p.stdout)
    except Exception as exc:
        return {"error": str(exc)}


def duration_seconds(meta: dict) -> float | None:
    try:
        return float(meta.get("format", {}).get("duration"))
    except Exception:
        return None


def update_state(project: Path, task: str, status: str, note: str = ""):
    assert status in STATES
    path = project / "config" / "workflow_state.json"
    data = read_json(path, {"version":2,"tasks":{}})
    data.setdefault("tasks", {})[task] = {
        "status": status,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "note": note,
    }
    write_json(path, data)


def find_skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_profile(project: Path) -> dict:
    project_profile = project / "config" / "rule_profile.json"
    if project_profile.exists():
        return read_json(project_profile)
    return read_json(find_skill_root() / "config" / "default_profile.json")

"""Local video analyze runtime."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_ROOT = REPO_ROOT / "shared"
sys.path.insert(0, str(SHARED_ROOT))

from artifacts import artifacts_for_run  # noqa: E402


def _run_json(cmd: list[str]) -> dict:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def ffprobe_duration(video_path: Path) -> float:
    payload = _run_json(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(video_path),
        ]
    )
    return float(payload["format"]["duration"])


def extract_cover(video_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            str(output_path),
        ],
        check=True,
    )


def extract_frames(video_path: Path, frames_dir: Path, interval: float = 1.0) -> list[Path]:
    frames_dir.mkdir(parents=True, exist_ok=True)
    pattern = frames_dir / "frame_%04d.jpg"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video_path),
            "-vf",
            f"fps=1/{interval}",
            str(pattern),
        ],
        check=True,
    )
    return sorted(frames_dir.glob("frame_*.jpg"))


def build_contact_sheet(frame_paths: list[Path], output_path: Path, cols: int = 3) -> None:
    if not frame_paths:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = min(len(frame_paths), cols * cols)
    selected = frame_paths[:count]
    rows = (count + cols - 1) // cols
    inputs: list[str] = []
    for frame in selected:
        inputs.extend(["-i", str(frame)])
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            *inputs,
            "-filter_complex",
            f"tile={cols}x{rows}",
            "-frames:v",
            "1",
            str(output_path),
        ],
        check=True,
    )


def parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", text.strip())
    segments: list[dict] = []
    seq = 1
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        time_line = lines[1] if "-->" in lines[1] else lines[0]
        content_lines = lines[2:] if "-->" in lines[1] else lines[1:]
        if "-->" not in time_line:
            continue
        start_text, end_text = [part.strip() for part in time_line.split("-->")]
        segments.append(
            {
                "sequence": seq,
                "start": _srt_time_to_seconds(start_text),
                "end": _srt_time_to_seconds(end_text),
                "content": " ".join(content_lines).strip(),
            }
        )
        seq += 1
    return segments


def _srt_time_to_seconds(value: str) -> float:
    hh, mm, rest = value.replace(",", ".").split(":")
    ss, *frac = rest.split(".")
    seconds = int(hh) * 3600 + int(mm) * 60 + int(ss)
    if frac:
        seconds += float("0." + frac[0])
    return round(seconds, 3)


def parse_plain_transcript(path: Path, duration: float) -> list[dict]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not lines:
        return []
    step = duration / max(len(lines), 1)
    segments = []
    for index, line in enumerate(lines, start=1):
        start = round((index - 1) * step, 3)
        end = round(index * step, 3)
        segments.append({"sequence": index, "start": start, "end": end, "content": line})
    return segments


def build_scenes(duration: float, segments: list[dict], frame_paths: list[Path]) -> list[dict]:
    if segments:
        return [
            {
                "sequence": segment["sequence"],
                "start": segment["start"],
                "end": segment["end"],
                "title": segment["content"][:80] or f"Scene {segment['sequence']}",
                "shot_type": "talking head / product demo",
            }
            for segment in segments
        ]

    if not frame_paths:
        return [
            {
                "sequence": 1,
                "start": 0.0,
                "end": round(duration, 3),
                "title": "Full clip",
                "shot_type": "unknown",
            }
        ]

    interval = duration / max(len(frame_paths), 1)
    scenes = []
    for index, frame in enumerate(frame_paths, start=1):
        scenes.append(
            {
                "sequence": index,
                "start": round((index - 1) * interval, 3),
                "end": round(index * interval, 3),
                "title": f"Frame {index}",
                "shot_type": "inferred from extracted frame",
                "frame_path": str(frame),
            }
        )
    return scenes


def run_analyze_video(
    *,
    video_path: Path,
    run_id: str,
    skill_dir: Path,
    transcript_path: Path | None = None,
    platform: str = "local",
    source_url: str | None = None,
) -> dict:
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    artifacts = artifacts_for_run(skill_dir, run_id)
    artifacts.ensure()

    duration = ffprobe_duration(video_path)
    cover_path = artifacts.root / "vision" / "cover.jpg"
    frames_dir = artifacts.root / "vision" / "frames"
    contact_sheet_path = artifacts.root / "vision" / "contact_sheet.jpg"

    extract_cover(video_path, cover_path)
    frame_paths = extract_frames(video_path, frames_dir, interval=1.0)
    if frame_paths:
        try:
            build_contact_sheet(frame_paths[:9], contact_sheet_path)
        except subprocess.CalledProcessError:
            contact_sheet_path = None

    segments: list[dict] = []
    if transcript_path:
        if transcript_path.suffix.lower() == ".srt":
            segments = parse_srt(transcript_path)
        else:
            segments = parse_plain_transcript(transcript_path, duration)

    scenes = build_scenes(duration, segments, frame_paths)

    artifacts.write_json(
        "input/video_details.json",
        {
            "source_url": source_url,
            "local_video_path": str(video_path.resolve()),
            "cover_path": str(cover_path),
            "duration": duration,
            "platform": platform,
            "stats": {"duration_sec": duration},
        },
    )
    artifacts.write_json("transcript/transcript.json", {"segments": segments})
    artifacts.write_text(
        "transcript/transcript.txt",
        "\n".join(segment.get("content", "") for segment in segments),
    )
    artifacts.write_json("vision/vision.json", {"scenes": scenes})

    result = {
        "run_id": run_id,
        "skill": "nv-analyze-video",
        "platform": platform,
        "video": {
            "source_url": source_url,
            "local_video_path": str(video_path.resolve()),
            "duration": duration,
            "cover_path": str(cover_path),
            "contact_sheet_path": str(contact_sheet_path) if contact_sheet_path else None,
            "stats": {"duration_sec": duration},
        },
        "transcript": {
            "segments": segments,
            "segments_count": len(segments),
            "files": {"json": "transcript/transcript.json", "txt": "transcript/transcript.txt"},
        },
        "vision": {
            "scenes": scenes,
            "files": {
                "json": "vision/vision.json",
                "cover": "vision/cover.jpg",
                "contact_sheet": "vision/contact_sheet.jpg" if contact_sheet_path else None,
            },
        },
        "response": {
            "content": "Local analyze complete.",
            "suggestions": [
                "Produce timestamped original script",
                "Produce storyboard table",
                "Offer next steps: rewrite / AI script / conversion logic",
            ],
        },
    }
    artifacts.write_json("outputs/result.json", result)
    return {"run_id": run_id, "artifacts_dir": str(artifacts.root), "result": result}

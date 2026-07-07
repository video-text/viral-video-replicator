#!/usr/bin/env python3
"""Burn one-word-at-a-time captions onto a generated clip."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path


def ass_time(seconds: float) -> str:
    seconds = max(seconds, 0.0)
    hh = int(seconds // 3600)
    mm = int((seconds % 3600) // 60)
    ss = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        ss += 1
        cs = 0
    return f"{hh}:{mm:02d}:{ss:02d}.{cs:02d}"


def escape_ass(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def split_words(text: str) -> list[str]:
    return [item for item in re.split(r"\s+", text.strip()) if item]


def timeline_from_words(words: list[str], start: float, word_duration: float) -> list[dict]:
    rows = []
    for index, word in enumerate(words):
        item_start = round(start + index * word_duration, 3)
        item_end = round(item_start + word_duration, 3)
        rows.append({"start": item_start, "end": item_end, "word": word, "position": "center-lower"})
    return rows


def timeline_from_csv(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            word = (row.get("word") or row.get("caption") or "").strip()
            if not word:
                continue
            rows.append(
                {
                    "start": float(row.get("start") or 0),
                    "end": float(row.get("end") or 0),
                    "word": word,
                    "position": (row.get("position") or "center-lower").strip(),
                }
            )
    return rows


def alignment_for(position: str) -> int:
    normalized = position.lower().replace("_", "-")
    if normalized in {"center", "middle", "center-middle"}:
        return 5
    if normalized in {"center-upper", "top-center", "upper-center"}:
        return 8
    if normalized in {"left-lower", "bottom-left"}:
        return 1
    if normalized in {"right-lower", "bottom-right"}:
        return 3
    return 2


def write_ass(
    *,
    path: Path,
    rows: list[dict],
    width: int,
    height: int,
    font_size: int,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,Arial,{font_size},&H00FFFFFF,&H00FFFFFF,&H80000000,&H66000000,-1,0,0,0,100,100,0,0,1,2,1,2,24,24,156,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for row in rows:
        alignment = alignment_for(str(row.get("position") or "center-lower"))
        word = escape_ass(str(row["word"]).upper())
        text = f"{{\\an{alignment}}}{word}"
        lines.append(
            f"Dialogue: 0,{ass_time(float(row['start']))},{ass_time(float(row['end']))},Word,,0,0,0,,{text}\n"
        )
    path.write_text("".join(lines), encoding="utf-8")
    return path


def ffprobe_size(video_path: Path) -> tuple[int, int]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=s=x:p=0",
            str(video_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    width, height = result.stdout.strip().split("x")
    return int(width), int(height)


def burn_captions(input_video: Path, ass_path: Path, output_video: Path) -> Path:
    output_video.parent.mkdir(parents=True, exist_ok=True)
    ass_filter = str(ass_path).replace("\\", "/").replace(":", "\\:")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_video),
            "-vf",
            f"ass='{ass_filter}'",
            "-c:a",
            "copy",
            str(output_video),
        ],
        check=True,
    )
    return output_video


def main() -> int:
    parser = argparse.ArgumentParser(description="Burn one-word-per-beat captions onto a generated video")
    parser.add_argument("--input_video", required=True)
    parser.add_argument("--output_video", required=True)
    parser.add_argument("--timeline_csv", help="CSV with start,end,word,position columns")
    parser.add_argument("--words", help="Whitespace-separated words to distribute evenly")
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--word_duration", type=float, default=0.25)
    parser.add_argument("--font_size", type=int, default=38)
    parser.add_argument("--ass_path")
    args = parser.parse_args()

    if not args.timeline_csv and not args.words:
        parser.error("Provide --timeline_csv or --words")

    input_video = Path(args.input_video)
    output_video = Path(args.output_video)
    rows = (
        timeline_from_csv(Path(args.timeline_csv))
        if args.timeline_csv
        else timeline_from_words(split_words(args.words or ""), args.start, args.word_duration)
    )
    if not rows:
        raise RuntimeError("Caption timeline is empty")

    width, height = ffprobe_size(input_video)
    ass_path = Path(args.ass_path) if args.ass_path else output_video.with_suffix(".ass")
    write_ass(path=ass_path, rows=rows, width=width, height=height, font_size=args.font_size)
    burn_captions(input_video, ass_path, output_video)
    print(f"wrote {output_video}")
    print(f"ass {ass_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

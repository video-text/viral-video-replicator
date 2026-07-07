#!/usr/bin/env python3
"""CLI for nv-analyze-video."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
LIB_ROOT = SKILL_ROOT / "lib"
sys.path.insert(0, str(LIB_ROOT))

from analyze_video import run_analyze_video  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a local reference video")
    parser.add_argument("--video_path", required=True, help="Local video file path")
    parser.add_argument("--run_id", required=True, help="Run identifier")
    parser.add_argument("--transcript_path", help="Optional .srt or plain transcript")
    parser.add_argument("--source_url", help="Optional original TikTok/Douyin URL")
    parser.add_argument("--platform", default="local", help="Platform label")
    parser.add_argument("--exact_remix", action="store_true", help="Extract dense frames for exact visual/caption remix")
    parser.add_argument("--exact_fps", type=float, default=4.0, help="Frame sampling rate for --exact_remix")
    args = parser.parse_args()

    result = run_analyze_video(
        video_path=Path(args.video_path),
        run_id=args.run_id,
        skill_dir=SKILL_ROOT,
        transcript_path=Path(args.transcript_path) if args.transcript_path else None,
        platform=args.platform,
        source_url=args.source_url,
        exact_remix=args.exact_remix,
        exact_fps=args.exact_fps,
    )
    print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

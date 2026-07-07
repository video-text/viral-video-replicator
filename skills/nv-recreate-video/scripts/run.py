#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "lib"))

from recreate_video import run_recreate_video  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_path", required=True)
    parser.add_argument("--run_id", required=True)
    parser.add_argument("--transcript_path")
    parser.add_argument("--source_url")
    parser.add_argument("--product_name")
    parser.add_argument("--product_image")
    parser.add_argument("--person_image")
    parser.add_argument("--angle")
    parser.add_argument("--brand")
    parser.add_argument("--style")
    args = parser.parse_args()

    result = run_recreate_video(
        video_path=Path(args.video_path),
        run_id=args.run_id,
        skill_dir=SKILL_ROOT,
        transcript_path=Path(args.transcript_path) if args.transcript_path else None,
        source_url=args.source_url,
        product_name=args.product_name,
        product_image=Path(args.product_image) if args.product_image else None,
        person_image=Path(args.person_image) if args.person_image else None,
        angle=args.angle,
        brand=args.brand,
        style=args.style,
    )
    print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

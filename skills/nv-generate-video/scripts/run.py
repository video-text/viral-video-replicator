#!/usr/bin/env python3
"""CLI for nv-generate-video."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
LIB_ROOT = SKILL_ROOT / "lib"
sys.path.insert(0, str(LIB_ROOT))

from generate_video import run_generate_video, run_generate_video_status  # noqa: E402


def confirm_generation(args: argparse.Namespace) -> bool:
    print(f"About to generate video via {args.provider or '(default provider)'}.")
    print(f"- provider: {args.provider or '(default)'}")
    print(f"- model: {args.model or '(default)'}")
    print(f"- orientation: {args.orientation or '(default)'}")
    print(f"- seconds: {args.seconds or '(default)'}")
    print(f"- definition: {args.definition or '(default)'}")
    if args.reference_images:
        print(f"- reference_images: {args.reference_images}")
    print(f"- prompt (first 120 chars): {args.prompt[:120]}")
    answer = input("Confirm to start generation? (yes/no): ").strip().lower()
    return answer in {"y", "yes"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a video through Higgsfield or APIMart")
    parser.add_argument("--run_id", required=True)
    parser.add_argument("--prompt")
    parser.add_argument("--task_id")
    parser.add_argument("--provider", choices=["higgsfield", "apimart"])
    parser.add_argument("--model")
    parser.add_argument("--orientation")
    parser.add_argument("--seconds", type=int)
    parser.add_argument("--definition")
    parser.add_argument("--reference_images")
    parser.add_argument("--timeout_sec", type=int, default=900)
    parser.add_argument("--poll_interval", type=int, default=5)
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--no_download", action="store_true")
    args = parser.parse_args()

    if not args.prompt and not args.task_id:
        parser.error("Provide --prompt or --task_id")

    reference_images = [item.strip() for item in args.reference_images.split(",")] if args.reference_images else []

    if args.task_id:
        result = run_generate_video_status(
            task_id=args.task_id,
            run_id=args.run_id,
            skill_dir=SKILL_ROOT,
            provider=args.provider,
            model=args.model,
            wait=args.wait,
            poll_interval=args.poll_interval,
            timeout_sec=args.timeout_sec,
            download=not args.no_download,
        )
        print(json.dumps({"ok": True, **result}, ensure_ascii=False))
        return 0 if result.get("video_url") else 1

    if not args.yes and not confirm_generation(args):
        print("Canceled.")
        return 2

    result = run_generate_video(
        prompt=args.prompt,
        run_id=args.run_id,
        skill_dir=SKILL_ROOT,
        provider=args.provider,
        model=args.model,
        orientation=args.orientation,
        seconds=args.seconds,
        definition=args.definition,
        reference_images=reference_images,
        poll_interval=args.poll_interval,
        timeout_sec=args.timeout_sec,
        download=not args.no_download,
    )
    print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    return 0 if result.get("video_url") else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

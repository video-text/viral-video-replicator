"""Higgsfield CLI adapter for nv-generate-video."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from apimart_client import download_file
from capabilities import VideoModel


def ensure_higgsfield_cli() -> str:
    executable = shutil.which("higgsfield")
    if not executable:
        raise RuntimeError(
            "Missing Higgsfield CLI. Install it with `npm install -g @higgsfield/cli`, "
            "then run `higgsfield auth login`."
        )
    return executable


def _flag_name(name: str) -> str:
    return "--" + name.replace("_", "-")


def _append_value(args: list[str], flag: str, value: object) -> None:
    if value is None:
        return
    args.extend([flag, str(value).lower() if isinstance(value, bool) else str(value)])


def _append_reference_args(args: list[str], selected: VideoModel, reference_images: list[str]) -> None:
    if not reference_images or not selected.cli_reference_flag:
        return

    if selected.cli_reference_flag == "image":
        for item in reference_images:
            args.extend(["--image", item])
        return

    if selected.cli_reference_flag == "start-image":
        args.extend(["--start-image", reference_images[0]])
        if len(reference_images) > 1:
            args.extend(["--end-image", reference_images[1]])
        return

    for item in reference_images:
        args.extend([_flag_name(selected.cli_reference_flag), item])


def _parse_json_output(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return {}
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        for line in reversed(stripped.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    raise RuntimeError(f"Higgsfield CLI did not return JSON: {stripped[:500]}")


def _run_json(args: list[str], timeout_sec: int | None = None) -> Any:
    executable = ensure_higgsfield_cli()
    completed = subprocess.run(
        [executable, *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"Higgsfield CLI failed: {message}")
    return _parse_json_output(completed.stdout)


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def extract_job_id(payload: Any) -> str | None:
    if isinstance(payload, str):
        return payload
    for item in _walk(payload):
        for key in ("job_id", "id", "request_id"):
            value = item.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def extract_video_url(payload: Any) -> str | None:
    preferred = ("result_url", "video_url", "download_url", "url")
    for item in _walk(payload):
        for key in preferred:
            value = item.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
        for key in ("videos", "video", "result", "outputs"):
            value = item.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
    return None


def build_create_args(
    *,
    selected: VideoModel,
    prompt: str,
    orientation: str,
    seconds: int,
    definition: str,
    reference_images: list[str],
    wait: bool,
    poll_interval: int,
    timeout_sec: int,
) -> list[str]:
    args = [
        "generate",
        "create",
        selected.id,
        "--prompt",
        prompt,
        "--aspect-ratio",
        orientation,
        "--duration",
        str(seconds),
    ]
    if selected.cli_definition_flag:
        args.extend([_flag_name(selected.cli_definition_flag), definition])
    for key, value in (selected.cli_extra_args or {}).items():
        _append_value(args, _flag_name(key), value)
    _append_reference_args(args, selected, reference_images)
    if wait:
        args.extend(["--wait", "--wait-timeout", f"{timeout_sec}s", "--wait-interval", f"{poll_interval}s"])
    args.extend(["--json", "--no-color"])
    return args


def submit_higgsfield_video(
    *,
    selected: VideoModel,
    prompt: str,
    orientation: str,
    seconds: int,
    definition: str,
    reference_images: list[str],
    poll_interval: int,
    timeout_sec: int,
) -> tuple[str | None, str | None, Any]:
    payload = _run_json(
        build_create_args(
            selected=selected,
            prompt=prompt,
            orientation=orientation,
            seconds=seconds,
            definition=definition,
            reference_images=reference_images,
            wait=True,
            poll_interval=poll_interval,
            timeout_sec=timeout_sec,
        ),
        timeout_sec=timeout_sec + 60,
    )
    return extract_job_id(payload), extract_video_url(payload), payload


def get_higgsfield_video_status(
    *,
    job_id: str,
    wait: bool,
    poll_interval: int,
    timeout_sec: int,
) -> tuple[str | None, Any]:
    command = "wait" if wait else "get"
    args = ["generate", command, job_id, "--json", "--no-color"]
    if wait:
        args.extend(["--wait-timeout", f"{timeout_sec}s", "--wait-interval", f"{poll_interval}s"])
    payload = _run_json(args, timeout_sec=timeout_sec + 60 if wait else 120)
    return extract_video_url(payload), payload


__all__ = [
    "download_file",
    "extract_job_id",
    "extract_video_url",
    "get_higgsfield_video_status",
    "submit_higgsfield_video",
]

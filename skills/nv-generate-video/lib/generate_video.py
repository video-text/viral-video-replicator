"""Video generation runtime."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_ROOT = REPO_ROOT / "shared"
sys.path.insert(0, str(SHARED_ROOT))

from apimart_bridge import (  # noqa: E402
    build_video_payload,
    download_file,
    extract_video_urls,
    get_task_status,
    load_api_key,
    poll_task,
    submit_video_task,
    upload_image,
)
from artifacts import artifacts_for_run  # noqa: E402
from capabilities import default_provider, resolve_video_request  # noqa: E402
from higgsfield_cli import get_higgsfield_video_status, submit_higgsfield_video  # noqa: E402


def _persist_result(artifacts, result: dict, title: str = "Video Generate Result") -> None:
    artifacts.write_json("outputs/result.json", result)
    artifacts.write_text(
        "outputs/result.md",
        "\n".join(
            [
                f"# {title}",
                "",
                f"- run_id: `{result.get('run_id')}`",
                f"- model: `{result.get('model')}`",
                f"- status: `{result.get('status')}`",
                f"- task_id: `{result.get('task_id')}`",
                f"- video_url: {result.get('video_url') or '(missing)'}",
                f"- local_video_path: {result.get('local_video_path') or '(missing)'}",
                "",
            ]
        ),
    )


def run_generate_video(
    *,
    prompt: str,
    run_id: str,
    skill_dir: Path,
    provider: str | None = None,
    model: str | None = None,
    orientation: str | None = None,
    seconds: int | None = None,
    definition: str | None = None,
    reference_images: list[str] | None = None,
    poll_interval: int = 5,
    timeout_sec: int = 900,
    download: bool = True,
) -> dict:
    final_provider = provider or default_provider()
    selected = resolve_video_request(
        provider=final_provider,
        model=model,
        orientation=orientation,
        seconds=seconds,
        definition=definition,
        reference_images=reference_images,
    )
    final_orientation = orientation or selected.default_orientation
    final_seconds = int(seconds if seconds is not None else selected.default_seconds)
    final_definition = definition or selected.default_definition
    final_model = model or selected.id

    if final_provider == "higgsfield":
        artifacts = artifacts_for_run(skill_dir, run_id)
        artifacts.ensure()
        task_id, video_url, task_data = submit_higgsfield_video(
            selected=selected,
            prompt=prompt,
            orientation=final_orientation,
            seconds=final_seconds,
            definition=final_definition,
            reference_images=reference_images or [],
            poll_interval=poll_interval,
            timeout_sec=timeout_sec,
        )
        local_video_path = None
        if download and video_url:
            local_video_path = artifacts.root / "outputs" / "generated.mp4"
            download_file(video_url, local_video_path)
        result = {
            "run_id": run_id,
            "task_id": task_id,
            "status": "succeeded" if video_url else "failed",
            "provider": final_provider,
            "model": final_model,
            "orientation": final_orientation,
            "seconds": final_seconds,
            "definition": final_definition,
            "video_url": video_url,
            "local_video_path": str(local_video_path) if local_video_path else None,
            "raw": {"task": task_data},
            "error": None if video_url else {"message": "No video URL in Higgsfield result"},
        }
        _persist_result(artifacts, result)
        return {
            "run_id": run_id,
            "artifacts_dir": str(artifacts.root),
            "task_id": task_id,
            "status": result["status"],
            "video_url": video_url,
            "local_video_path": result["local_video_path"],
        }

    api_key = load_api_key()
    image_urls = []
    if reference_images:
        for item in reference_images:
            image_urls.append(upload_image(api_key, Path(item)))

    body = build_video_payload(
        model_id=final_model,
        prompt=prompt,
        orientation=final_orientation,
        seconds=final_seconds,
        definition=final_definition,
        image_urls=image_urls or None,
    )

    artifacts = artifacts_for_run(skill_dir, run_id)
    artifacts.ensure()
    task_id = submit_video_task(api_key, body)

    initial = {
        "run_id": run_id,
        "task_id": task_id,
        "status": "submitted",
        "provider": final_provider,
        "model": final_model,
        "orientation": final_orientation,
        "seconds": final_seconds,
        "definition": final_definition,
        "video_url": None,
        "local_video_path": None,
        "raw": {"submit": body},
        "error": None,
    }
    _persist_result(artifacts, initial)

    task_data = poll_task(api_key, task_id, poll_interval=poll_interval, max_wait=timeout_sec)
    video_urls = extract_video_urls(task_data)
    video_url = video_urls[0] if video_urls else None
    local_video_path = None
    if download and video_url:
        local_video_path = artifacts.root / "outputs" / "generated.mp4"
        download_file(video_url, local_video_path)

    result = {
        "run_id": run_id,
        "task_id": task_id,
        "status": "succeeded" if video_url else "failed",
        "provider": final_provider,
        "model": final_model,
        "orientation": final_orientation,
        "seconds": final_seconds,
        "definition": final_definition,
        "video_url": video_url,
        "local_video_path": str(local_video_path) if local_video_path else None,
        "raw": {"submit": body, "task": task_data},
        "error": None if video_url else {"message": "No video URL in task result"},
    }
    _persist_result(artifacts, result)
    return {
        "run_id": run_id,
        "artifacts_dir": str(artifacts.root),
        "task_id": task_id,
        "status": result["status"],
        "video_url": video_url,
        "local_video_path": result["local_video_path"],
    }


def run_generate_video_status(
    *,
    task_id: str,
    run_id: str,
    skill_dir: Path,
    provider: str | None = None,
    model: str | None = None,
    wait: bool = False,
    poll_interval: int = 5,
    timeout_sec: int = 900,
    download: bool = True,
) -> dict:
    final_provider = provider or default_provider()
    artifacts = artifacts_for_run(skill_dir, run_id)
    artifacts.ensure()

    if final_provider == "higgsfield":
        video_url, task_data = get_higgsfield_video_status(
            job_id=task_id,
            wait=wait,
            poll_interval=poll_interval,
            timeout_sec=timeout_sec,
        )
        local_video_path = None
        if download and video_url:
            local_video_path = artifacts.root / "outputs" / "generated.mp4"
            download_file(video_url, local_video_path)
        result = {
            "run_id": run_id,
            "task_id": task_id,
            "status": "succeeded" if video_url else "pending",
            "provider": final_provider,
            "model": model,
            "video_url": video_url,
            "local_video_path": str(local_video_path) if local_video_path else None,
            "raw": {"task": task_data},
            "error": None,
        }
        _persist_result(artifacts, result, title="Video Generate Status")
        return {
            "run_id": run_id,
            "artifacts_dir": str(artifacts.root),
            "task_id": task_id,
            "status": result["status"],
            "video_url": video_url,
            "local_video_path": result["local_video_path"],
        }

    api_key = load_api_key()
    task_data = poll_task(api_key, task_id, poll_interval=poll_interval, max_wait=timeout_sec) if wait else get_task_status(api_key, task_id)
    video_urls = extract_video_urls(task_data)
    video_url = video_urls[0] if video_urls else None
    local_video_path = None
    if download and video_url:
        local_video_path = artifacts.root / "outputs" / "generated.mp4"
        download_file(video_url, local_video_path)
    result = {
        "run_id": run_id,
        "task_id": task_id,
        "status": "succeeded" if video_url else task_data.get("status", "pending"),
        "provider": final_provider,
        "model": model,
        "video_url": video_url,
        "local_video_path": str(local_video_path) if local_video_path else None,
        "raw": {"task": task_data},
        "error": None,
    }
    _persist_result(artifacts, result, title="Video Generate Status")
    return {
        "run_id": run_id,
        "artifacts_dir": str(artifacts.root),
        "task_id": task_id,
        "status": result["status"],
        "video_url": video_url,
        "local_video_path": result["local_video_path"],
    }

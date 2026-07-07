"""APIMart payload builder for nv-generate-video."""

from __future__ import annotations

from .apimart_client import (
    download_file,
    extract_video_urls,
    get_task_status,
    load_api_key,
    poll_task,
    submit_video_task,
    upload_image,
)


def build_video_payload(
    *,
    model_id: str,
    prompt: str,
    orientation: str,
    seconds: int,
    definition: str,
    image_urls: list[str] | None = None,
) -> dict:
    body: dict = {
        "model": model_id,
        "prompt": prompt,
        "duration": seconds,
        "aspect_ratio": orientation,
    }
    if model_id.startswith("doubao-seedance"):
        body["resolution"] = definition
    elif model_id.startswith("kling"):
        body["mode"] = "std"
        body["watermark"] = False
        if image_urls:
            body["image_urls"] = image_urls
    elif model_id.startswith("grok"):
        body["size"] = orientation
        body["quality"] = definition
    elif model_id.startswith("pixverse"):
        body["size"] = orientation
        body["resolution"] = definition
    elif model_id.startswith("minimax"):
        body["resolution"] = definition
    else:
        body["resolution"] = definition
    if image_urls and "image_urls" not in body:
        body["image_urls"] = image_urls
    return body

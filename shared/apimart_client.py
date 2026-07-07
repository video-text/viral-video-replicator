"""Standalone APIMart client for Codex skill installs."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests

BASE_URL = "https://api.apimart.ai"


def load_api_key() -> str:
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("HIGGSFIELD_API_KEY=") and "your-" not in line:
                os.environ.setdefault("HIGGSFIELD_API_KEY", line.split("=", 1)[1].strip())

    api_key = os.environ.get("HIGGSFIELD_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing HIGGSFIELD_API_KEY. Set env var or add it to .env")
    return api_key


def auth_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def request_with_retry(method: str, url: str, *, retries: int = 5, **kwargs) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except (
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 15))
            else:
                raise
    if last_error:
        raise last_error
    raise RuntimeError(f"Request failed: {method} {url}")


def upload_image(api_key: str, image_path: Path) -> str:
    with image_path.open("rb") as handle:
        response = request_with_retry(
            "POST",
            f"{BASE_URL}/v1/uploads/images",
            headers=auth_headers(api_key),
            files={"file": (image_path.name, handle)},
            timeout=120,
        )
    payload = response.json()
    url = payload.get("url") or (payload.get("data") or {}).get("url")
    if not url:
        raise RuntimeError(f"Upload response missing url: {payload}")
    return url


def submit_video_task(api_key: str, body: dict) -> str:
    response = request_with_retry(
        "POST",
        f"{BASE_URL}/v1/videos/generations",
        headers={**auth_headers(api_key), "Content-Type": "application/json"},
        json=body,
        timeout=120,
    )
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(json.dumps(payload["error"], ensure_ascii=False))
    data = payload.get("data")
    if isinstance(data, list) and data:
        task_id = data[0].get("task_id")
    elif isinstance(data, dict):
        task_id = data.get("task_id") or data.get("id")
    else:
        task_id = payload.get("task_id")
    if not task_id:
        raise RuntimeError(f"Submit response missing task_id: {payload}")
    return task_id


def poll_task(api_key: str, task_id: str, poll_interval: int = 5, max_wait: int = 900) -> dict:
    deadline = time.time() + max_wait
    while time.time() < deadline:
        response = request_with_retry(
            "GET",
            f"{BASE_URL}/v1/tasks/{task_id}",
            headers=auth_headers(api_key),
            params={"language": "zh"},
            timeout=60,
        )
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(json.dumps(payload["error"], ensure_ascii=False))
        data = payload.get("data", payload)
        status = data.get("status", "unknown")
        if status == "completed":
            return data
        if status in {"failed", "cancelled"}:
            raise RuntimeError(f"Task {status}: {json.dumps(data.get('error') or data, ensure_ascii=False)}")
        time.sleep(poll_interval)
    raise TimeoutError(f"Task {task_id} not completed within {max_wait}s")


def get_task_status(api_key: str, task_id: str) -> dict:
    response = request_with_retry(
        "GET",
        f"{BASE_URL}/v1/tasks/{task_id}",
        headers=auth_headers(api_key),
        params={"language": "zh"},
        timeout=60,
    )
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(str(payload["error"]))
    return payload.get("data", payload)


def extract_video_urls(task_data: dict) -> list[str]:
    videos = (task_data.get("result") or {}).get("videos") or []
    urls: list[str] = []
    for item in videos:
        if isinstance(item, str):
            urls.append(item)
            continue
        url = item.get("url")
        if isinstance(url, list):
            urls.extend(url)
        elif isinstance(url, str):
            urls.append(url)
    return urls


def download_file(url: str, output_path: Path, retries: int = 5) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        try:
            response = request_with_retry("GET", url, stream=True, timeout=300, retries=3)
            with output_path.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
            return output_path
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            output_path.unlink(missing_ok=True)
            if attempt >= retries:
                raise
            time.sleep(min(2**attempt, 15))
    return output_path

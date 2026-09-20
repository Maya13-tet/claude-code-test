#!/usr/bin/env python3
"""CLI: generate a short video from a text prompt via an external text-to-video API."""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.environ.get("VIDEO_API_BASE_URL", "https://api.kie.ai")
API_KEY = os.environ.get("VIDEO_API_KEY", "")
MODEL = "bytedance/seedance-2-fast"

POLL_INITIAL_INTERVAL_SECONDS = 3
POLL_MAX_INTERVAL_SECONDS = 30
POLL_TIMEOUT_SECONDS = 900
PENDING_STATES = {"waiting", "queuing", "generating"}


def submit_generation(prompt: str, duration: int) -> str:
    """Submit a text-to-video job to KIE (Bytedance Seedance 2.0 Fast) and return the task id."""
    response = requests.post(
        f"{API_BASE_URL}/api/v1/jobs/createTask",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "input": {"prompt": prompt, "duration": duration}},
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    if body.get("code") != 200:
        raise RuntimeError(f"Task creation failed: {body.get('msg', 'unknown error')}")
    return body["data"]["taskId"]


def poll_status(task_id: str) -> str:
    """Poll KIE's "Get Task Details" endpoint until the job finishes and return the video URL."""
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    interval = POLL_INITIAL_INTERVAL_SECONDS
    while time.monotonic() < deadline:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/jobs/recordInfo",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"taskId": task_id},
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()
        if body.get("code") != 200:
            raise RuntimeError(f"Status query failed: {body.get('msg', 'unknown error')}")
        data = body["data"]
        state = data.get("state")
        if state == "success":
            result = json.loads(data["resultJson"])
            return result["resultUrls"][0]
        if state == "fail":
            raise RuntimeError(f"Generation failed ({data.get('failCode')}): {data.get('failMsg', 'unknown error')}")
        if state not in PENDING_STATES:
            raise RuntimeError(f"Unexpected task state: {state}")
        time.sleep(interval)
        interval = min(interval * 2, POLL_MAX_INTERVAL_SECONDS)
    raise TimeoutError(f"Generation did not complete within {POLL_TIMEOUT_SECONDS}s")


def download_result(video_url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(video_url, stream=True, timeout=60)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def generate_video(prompt: str, duration: int, output_path: Path) -> Path:
    if not API_BASE_URL or not API_KEY:
        raise RuntimeError(
            "VIDEO_API_BASE_URL / VIDEO_API_KEY are not set. Copy .env.example to .env and fill them in."
        )
    job_id = submit_generation(prompt, duration)
    video_url = poll_status(job_id)
    download_result(video_url, output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a short video from a text prompt.")
    parser.add_argument("prompt", help="Text description of the video to generate")
    parser.add_argument("--duration", type=int, default=15, help="Video duration in seconds (default: 15)")
    parser.add_argument("--output", type=Path, default=Path("out/video.mp4"), help="Output file path")
    args = parser.parse_args()

    try:
        path = generate_video(args.prompt, args.duration, args.output)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Video saved to {path}")


if __name__ == "__main__":
    main()

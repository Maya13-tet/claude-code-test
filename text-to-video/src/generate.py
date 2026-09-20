#!/usr/bin/env python3
"""CLI: generate a short video from a text prompt via an external text-to-video API."""
import argparse
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.environ.get("VIDEO_API_BASE_URL", "")
API_KEY = os.environ.get("VIDEO_API_KEY", "")

POLL_INTERVAL_SECONDS = 5
POLL_TIMEOUT_SECONDS = 600


def submit_generation(prompt: str, duration: int) -> str:
    """Submit a generation job to the provider and return a job id.

    Replace this with the provider's actual "create generation" endpoint.
    """
    response = requests.post(
        f"{API_BASE_URL}/v1/generations",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"prompt": prompt, "duration_seconds": duration},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["id"]


def poll_status(job_id: str) -> str:
    """Poll until the job finishes and return the resulting video URL.

    Replace this with the provider's actual "get generation status" endpoint.
    """
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        response = requests.get(
            f"{API_BASE_URL}/v1/generations/{job_id}",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        if status == "completed":
            return data["video_url"]
        if status == "failed":
            raise RuntimeError(f"Generation failed: {data.get('error', 'unknown error')}")
        time.sleep(POLL_INTERVAL_SECONDS)
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

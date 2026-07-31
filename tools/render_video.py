from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = os.getenv("VIDEO_URL", "http://127.0.0.1:8000/video.html?autoplay=1&record=1")
OUT_DIR = Path(os.getenv("VIDEO_OUT_DIR", "build/video-raw"))
OUT_FILE = Path(os.getenv("VIDEO_WEBM", "build/scripture-everywhere.webm"))
TIMELINE_SECONDS = 179


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(OUT_DIR),
            record_video_size={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_function(
            "[...document.querySelectorAll('.scene')].reduce((n,s)=>n+Number(s.dataset.duration),0) === 179"
        )
        page.wait_for_function("document.body.classList.contains('record-mode')")
        if page.locator(".bottom").is_visible() or page.locator(".timer").is_visible():
            raise RuntimeError("Recording controls are visible in presentation mode")
        video = page.video
        page.wait_for_timeout((TIMELINE_SECONDS + 1) * 1000)
        page.close()
        if video is None:
            raise RuntimeError("Playwright did not create a video object")
        video.save_as(str(OUT_FILE))
        context.close()
        browser.close()
    if not OUT_FILE.exists() or OUT_FILE.stat().st_size == 0:
        raise RuntimeError("Recorded video file is missing or empty")
    print(f"Recorded clean {TIMELINE_SECONDS}-second presentation to {OUT_FILE} ({OUT_FILE.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

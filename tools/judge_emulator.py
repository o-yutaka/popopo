from __future__ import annotations

import asyncio
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

BASE_URL = os.getenv("JUDGE_BASE_URL", "http://127.0.0.1:8000/")
OUT = Path(os.getenv("JUDGE_AUDIT_OUT", "build/judge-emulator"))


@dataclass(frozen=True)
class Device:
    name: str
    width: int
    height: int
    mobile: bool = False
    touch: bool = False
    scale: float = 1.0
    reduced_motion: str = "no-preference"
    user_agent: str | None = None


@dataclass
class Finding:
    severity: str
    device: str
    page: str
    message: str


@dataclass
class DeviceResult:
    device: str
    page_title: str = ""
    viewport: dict[str, int] = field(default_factory=dict)
    body_width: int = 0
    scroll_width: int = 0
    links_checked: int = 0
    buttons_exercised: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


DEVICES = [
    Device("desktop", 1440, 900),
    Device(
        "iphone-portrait",
        393,
        852,
        mobile=True,
        touch=True,
        scale=3,
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 "
            "Mobile/15E148 Safari/604.1"
        ),
    ),
    Device(
        "iphone-landscape",
        852,
        393,
        mobile=True,
        touch=True,
        scale=3,
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 "
            "Mobile/15E148 Safari/604.1"
        ),
    ),
    Device("ipad", 820, 1180, mobile=True, touch=True, scale=2),
    Device("reduced-motion", 1440, 900, reduced_motion="reduce"),
]


def probe_local_url(url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    base = urlparse(BASE_URL)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != base.netloc:
        return True, "external"
    try:
        request = Request(url, method="GET", headers={"User-Agent": "judge-emulator/1.0"})
        with urlopen(request, timeout=5) as response:
            code = int(response.status)
        return 200 <= code < 400, str(code)
    except Exception as exc:  # pragma: no cover - reported in artifact
        return False, str(exc)


async def add_runtime_observers(page: Page, result: DeviceResult, page_name: str) -> None:
    page.on(
        "pageerror",
        lambda exc: result.findings.append(
            Finding("error", result.device, page_name, f"JavaScript exception: {exc}")
        ),
    )

    def on_console(message: Any) -> None:
        if message.type == "error":
            text = message.text
            if "live-api-evidence.json" not in text:
                result.findings.append(
                    Finding("error", result.device, page_name, f"Console error: {text}")
                )

    page.on("console", on_console)

    def on_request_failed(request: Any) -> None:
        if "live-api-evidence.json" not in request.url:
            failure = request.failure or "unknown failure"
            result.findings.append(
                Finding(
                    "error",
                    result.device,
                    page_name,
                    f"Request failed: {request.url} ({failure})",
                )
            )

    page.on("requestfailed", on_request_failed)


async def screenshot(page: Page, result: DeviceResult, name: str, *, full_page: bool = True) -> None:
    path = OUT / result.device / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(path), full_page=full_page, animations="disabled")
    result.screenshots.append(str(path.relative_to(OUT)))


async def exercise_buttons(page: Page, result: DeviceResult) -> None:
    buttons = page.locator("button:visible")
    count = min(await buttons.count(), 16)
    labels: list[str] = []
    for index in range(count):
        await page.goto(BASE_URL, wait_until="networkidle")
        current = page.locator("button:visible").nth(index)
        if not await current.is_visible() or not await current.is_enabled():
            continue
        label = ((await current.inner_text()).strip() or await current.get_attribute("aria-label") or f"button-{index}")[:80]
        try:
            await current.click(timeout=3000)
            await page.wait_for_timeout(250)
            labels.append(label)
        except Exception as exc:
            result.findings.append(
                Finding("error", result.device, "index", f"Button failed: {label}: {exc}")
            )
    result.buttons_exercised = labels


async def audit_index(context: BrowserContext, device: Device) -> DeviceResult:
    result = DeviceResult(device=device.name, viewport={"width": device.width, "height": device.height})
    page = await context.new_page()
    await add_runtime_observers(page, result, "index")
    response = await page.goto(BASE_URL, wait_until="networkidle")
    if response is None or response.status >= 400:
        result.findings.append(
            Finding("error", device.name, "index", f"Initial page HTTP failure: {getattr(response, 'status', None)}")
        )
        await page.close()
        return result

    result.page_title = await page.title()
    if "Scripture Everywhere" not in result.page_title:
        result.findings.append(Finding("error", device.name, "index", f"Unexpected title: {result.page_title!r}"))

    h1 = page.locator("h1:visible")
    if await h1.count() == 0:
        result.findings.append(Finding("error", device.name, "index", "No visible H1"))

    dimensions = await page.evaluate(
        """() => ({
          bodyWidth: document.body.getBoundingClientRect().width,
          scrollWidth: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth),
          viewport: window.innerWidth
        })"""
    )
    result.body_width = round(dimensions["bodyWidth"])
    result.scroll_width = int(dimensions["scrollWidth"])
    if result.scroll_width > int(dimensions["viewport"]) + 2:
        result.findings.append(
            Finding(
                "error",
                device.name,
                "index",
                f"Horizontal overflow: scrollWidth={result.scroll_width}, viewport={dimensions['viewport']}",
            )
        )

    hrefs = await page.locator("a[href]").evaluate_all("els => els.map(e => e.href)")
    for href in sorted(set(hrefs)):
        parsed = urlparse(href)
        if parsed.scheme in {"mailto", "tel", "javascript"} or href.endswith("#"):
            continue
        ok, detail = probe_local_url(href)
        result.links_checked += 1
        if not ok:
            result.findings.append(Finding("error", device.name, "index", f"Broken local link: {href} ({detail})"))

    await screenshot(page, result, "index-full")
    await exercise_buttons(page, result)
    await page.close()
    return result


async def audit_video(context: BrowserContext, result: DeviceResult) -> None:
    page = await context.new_page()
    await add_runtime_observers(page, result, "video")
    video_url = urljoin(BASE_URL, "video.html?record=1")
    response = await page.goto(video_url, wait_until="networkidle")
    if response is None or response.status >= 400:
        result.findings.append(Finding("error", result.device, "video", "video.html unavailable"))
        await page.close()
        return

    audit = await page.evaluate(
        """() => ({
          total: [...document.querySelectorAll('.scene')].reduce((n,s)=>n+Number(s.dataset.duration),0),
          scenes: document.querySelectorAll('.scene').length,
          recordMode: document.body.classList.contains('record-mode'),
          timer: getComputedStyle(document.querySelector('.timer')).display,
          bottom: getComputedStyle(document.querySelector('.bottom')).display,
          progress: getComputedStyle(document.querySelector('.progress')).display,
          scrollWidth: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth),
          viewport: window.innerWidth
        })"""
    )
    if audit["total"] != 179 or audit["scenes"] != 10:
        result.findings.append(Finding("error", result.device, "video", f"Timeline mismatch: {audit}"))
    if not audit["recordMode"] or any(audit[key] != "none" for key in ("timer", "bottom", "progress")):
        result.findings.append(Finding("error", result.device, "video", f"Recording UI is visible: {audit}"))
    if audit["scrollWidth"] > audit["viewport"] + 2:
        result.findings.append(Finding("error", result.device, "video", f"Horizontal overflow: {audit}"))

    scenes = page.locator(".scene")
    for index in range(await scenes.count()):
        await page.evaluate(
            """index => document.querySelectorAll('.scene').forEach((scene, i) => scene.classList.toggle('active', i === index))""",
            index,
        )
        await page.wait_for_timeout(150)
        await screenshot(page, result, f"video-scene-{index + 1:02d}", full_page=False)
    await page.close()


async def run_device(browser: Browser, device: Device) -> DeviceResult:
    context = await browser.new_context(
        viewport={"width": device.width, "height": device.height},
        is_mobile=device.mobile,
        has_touch=device.touch,
        device_scale_factor=device.scale,
        reduced_motion=device.reduced_motion,
        user_agent=device.user_agent,
        locale="en-US",
        timezone_id="Asia/Tokyo",
        color_scheme="dark",
    )
    result = await audit_index(context, device)
    await audit_video(context, result)
    await context.close()
    return result


def render_html(results: list[DeviceResult]) -> str:
    cards: list[str] = []
    for result in results:
        status = "PASS" if not any(f.severity == "error" for f in result.findings) else "FAIL"
        shots = "".join(
            f'<a href="{path}"><img src="{path}" alt="{path}" loading="lazy"></a>'
            for path in result.screenshots
        )
        findings = "".join(f"<li><b>{f.severity.upper()}</b> {f.page}: {f.message}</li>" for f in result.findings) or "<li>None</li>"
        cards.append(
            f"""<section><h2>{result.device} — {status}</h2>
            <p>Viewport {result.viewport['width']}×{result.viewport['height']} · links {result.links_checked} · buttons {len(result.buttons_exercised)}</p>
            <ul>{findings}</ul><div class="shots">{shots}</div></section>"""
        )
    return """<!doctype html><meta charset="utf-8"><title>Judge Emulator Audit</title>
    <style>body{font-family:system-ui;margin:24px;background:#0b1511;color:#eef8ef}section{padding:20px;margin:20px 0;background:#15251e;border-radius:18px}img{width:280px;max-height:220px;object-fit:contain;background:#fff;margin:6px;border-radius:8px}.shots{display:flex;flex-wrap:wrap}li{margin:6px 0}</style>
    <h1>Scripture Everywhere AI — Judge Emulator</h1>""" + "".join(cards)


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        results = [await run_device(browser, device) for device in DEVICES]
        await browser.close()

    payload = {
        "base_url": BASE_URL,
        "devices": [
            {
                **asdict(result),
                "findings": [asdict(finding) for finding in result.findings],
            }
            for result in results
        ],
    }
    (OUT / "audit.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT / "index.html").write_text(render_html(results), encoding="utf-8")

    errors = [finding for result in results for finding in result.findings if finding.severity == "error"]
    print(json.dumps({"devices": len(results), "errors": len(errors)}, indent=2))
    for finding in errors:
        print(f"ERROR [{finding.device}/{finding.page}] {finding.message}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

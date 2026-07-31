from __future__ import annotations

import asyncio
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urlparse
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


IPHONE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 "
    "Mobile/15E148 Safari/604.1"
)
DEVICES = [
    Device("desktop", 1440, 900),
    Device("iphone-portrait", 393, 852, True, True, 3, user_agent=IPHONE_UA),
    Device("iphone-landscape", 852, 393, True, True, 3, user_agent=IPHONE_UA),
    Device("ipad", 820, 1180, True, True, 2),
    Device("reduced-motion", 1440, 900, reduced_motion="reduce"),
]


def probe_local_url(url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    base = urlparse(BASE_URL)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != base.netloc:
        return True, "external"
    try:
        request = Request(url, method="GET", headers={"User-Agent": "judge-emulator/2.0"})
        with urlopen(request, timeout=5) as response:
            code = int(response.status)
        return 200 <= code < 400, str(code)
    except Exception as exc:  # surfaced in audit artifact
        return False, str(exc)


def add_finding(result: DeviceResult, page_name: str, message: str) -> None:
    finding = Finding("error", result.device, page_name, message)
    if finding not in result.findings:
        result.findings.append(finding)


async def add_runtime_observers(page: Page, result: DeviceResult, page_name: str) -> None:
    page.on("pageerror", lambda exc: add_finding(result, page_name, f"JavaScript exception: {exc}"))

    def on_console(message) -> None:
        if message.type == "error":
            add_finding(result, page_name, f"Console error: {message.text}")

    def on_request_failed(request) -> None:
        add_finding(
            result,
            page_name,
            f"Request failed: {request.url} ({request.failure or 'unknown failure'})",
        )

    def on_response(response) -> None:
        if response.status >= 400:
            add_finding(result, page_name, f"HTTP {response.status}: {response.url}")

    page.on("console", on_console)
    page.on("requestfailed", on_request_failed)
    page.on("response", on_response)


async def screenshot(page: Page, result: DeviceResult, name: str, *, full_page: bool) -> None:
    path = OUT / result.device / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(path), full_page=full_page, animations="disabled")
    result.screenshots.append(str(path.relative_to(OUT)))


async def assert_no_horizontal_overflow(page: Page, result: DeviceResult, page_name: str) -> None:
    values = await page.evaluate(
        """() => ({
          viewport: innerWidth,
          scrollWidth: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth)
        })"""
    )
    result.scroll_width = int(values["scrollWidth"])
    if values["scrollWidth"] > values["viewport"] + 2:
        add_finding(result, page_name, f"Horizontal overflow: {values}")


async def exercise_buttons(page: Page, result: DeviceResult) -> None:
    await page.goto(BASE_URL, wait_until="networkidle")
    count = min(await page.locator("button:visible").count(), 16)
    labels: list[str] = []
    for index in range(count):
        await page.goto(BASE_URL, wait_until="networkidle")
        button = page.locator("button:visible").nth(index)
        if not await button.is_visible() or not await button.is_enabled():
            continue
        label = ((await button.inner_text()).strip() or f"button-{index}")[:80]
        try:
            await button.click(timeout=3000)
            await page.wait_for_timeout(200)
            labels.append(label)
        except Exception as exc:
            add_finding(result, "index", f"Button failed: {label}: {exc}")
    result.buttons_exercised = labels


async def audit_index(context: BrowserContext, device: Device) -> DeviceResult:
    result = DeviceResult(device=device.name, viewport={"width": device.width, "height": device.height})
    page = await context.new_page()
    await add_runtime_observers(page, result, "index")
    response = await page.goto(BASE_URL, wait_until="networkidle")
    if response is None or response.status >= 400:
        add_finding(result, "index", f"Initial HTTP failure: {getattr(response, 'status', None)}")
        await page.close()
        return result

    result.page_title = await page.title()
    if "Scripture Everywhere" not in result.page_title:
        add_finding(result, "index", f"Unexpected title: {result.page_title!r}")
    if await page.locator("h1:visible").count() == 0:
        add_finding(result, "index", "No visible H1")

    result.body_width = round(await page.evaluate("document.body.getBoundingClientRect().width"))
    await assert_no_horizontal_overflow(page, result, "index")

    hrefs = await page.locator("a[href]").evaluate_all("els => els.map(e => e.href)")
    for href in sorted(set(hrefs)):
        parsed = urlparse(href)
        if parsed.scheme in {"mailto", "tel", "javascript"} or href.endswith("#"):
            continue
        ok, detail = probe_local_url(href)
        result.links_checked += 1
        if not ok:
            add_finding(result, "index", f"Broken local link: {href} ({detail})")

    await screenshot(page, result, "index-full", full_page=True)
    await exercise_buttons(page, result)
    await page.close()
    return result


async def active_scene_bounds(page: Page) -> dict[str, float]:
    return await page.evaluate(
        """() => {
          const active = document.querySelector('.scene.active');
          const rects = [...active.querySelectorAll('*')]
            .filter(el => {
              const style = getComputedStyle(el);
              const rect = el.getBoundingClientRect();
              return style.display !== 'none' && style.visibility !== 'hidden'
                && rect.width > 0 && rect.height > 0;
            })
            .map(el => el.getBoundingClientRect());
          if (!rects.length) {
            const rect = active.getBoundingClientRect();
            rects.push(rect);
          }
          return {
            viewportWidth: innerWidth,
            viewportHeight: innerHeight,
            minLeft: Math.min(...rects.map(r => r.left)),
            maxRight: Math.max(...rects.map(r => r.right)),
            minTop: Math.min(...rects.map(r => r.top)),
            maxBottom: Math.max(...rects.map(r => r.bottom))
          };
        }"""
    )


async def audit_video(context: BrowserContext, result: DeviceResult) -> None:
    page = await context.new_page()
    await add_runtime_observers(page, result, "video")
    response = await page.goto(f"{BASE_URL}video.html?record=1", wait_until="networkidle")
    if response is None or response.status >= 400:
        add_finding(result, "video", "video.html unavailable")
        await page.close()
        return

    contract = await page.evaluate(
        """() => ({
          total: [...document.querySelectorAll('.scene')].reduce((n,s)=>n+Number(s.dataset.duration),0),
          scenes: document.querySelectorAll('.scene').length,
          recordMode: document.body.classList.contains('record-mode'),
          timer: getComputedStyle(document.querySelector('.timer')).display,
          bottom: getComputedStyle(document.querySelector('.bottom')).display,
          progress: getComputedStyle(document.querySelector('.progress')).display
        })"""
    )
    if contract["total"] != 179 or contract["scenes"] != 10:
        add_finding(result, "video", f"Timeline mismatch: {contract}")
    if not contract["recordMode"] or any(contract[key] != "none" for key in ("timer", "bottom", "progress")):
        add_finding(result, "video", f"Recording UI visible: {contract}")
    await assert_no_horizontal_overflow(page, result, "video")

    scenes = page.locator(".scene")
    for index in range(await scenes.count()):
        await page.evaluate(
            "i => document.querySelectorAll('.scene').forEach((s,n)=>s.classList.toggle('active',n===i))",
            index,
        )
        await page.wait_for_timeout(120)
        bounds = await active_scene_bounds(page)
        tolerance = 2
        if (
            bounds["minLeft"] < -tolerance
            or bounds["maxRight"] > bounds["viewportWidth"] + tolerance
            or bounds["minTop"] < -tolerance
            or bounds["maxBottom"] > bounds["viewportHeight"] + tolerance
        ):
            add_finding(result, "video", f"Scene {index + 1} clipped: {bounds}")
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
        failed = any(f.severity == "error" for f in result.findings)
        shots = "".join(
            f'<a href="{path}"><img src="{path}" alt="{path}" loading="lazy"></a>'
            for path in result.screenshots
        )
        findings = "".join(
            f"<li><b>{f.severity.upper()}</b> {f.page}: {f.message}</li>"
            for f in result.findings
        ) or "<li>None</li>"
        cards.append(
            f"<section><h2>{result.device} — {'FAIL' if failed else 'PASS'}</h2>"
            f"<p>Viewport {result.viewport['width']}×{result.viewport['height']} · "
            f"links {result.links_checked} · buttons {len(result.buttons_exercised)}</p>"
            f"<ul>{findings}</ul><div class='shots'>{shots}</div></section>"
        )
    return (
        "<!doctype html><meta charset='utf-8'><title>Judge Emulator Audit</title>"
        "<style>body{font-family:system-ui;margin:24px;background:#0b1511;color:#eef8ef}"
        "section{padding:20px;margin:20px 0;background:#15251e;border-radius:18px}"
        "img{width:280px;max-height:220px;object-fit:contain;background:#fff;margin:6px;border-radius:8px}"
        ".shots{display:flex;flex-wrap:wrap}li{margin:6px 0}</style>"
        "<h1>Scripture Everywhere AI — Judge Emulator</h1>" + "".join(cards)
    )


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        results = [await run_device(browser, device) for device in DEVICES]
        await browser.close()

    payload = {
        "base_url": BASE_URL,
        "devices": [
            {**asdict(result), "findings": [asdict(f) for f in result.findings]}
            for result in results
        ],
    }
    (OUT / "audit.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT / "index.html").write_text(render_html(results), encoding="utf-8")

    errors = [f for result in results for f in result.findings if f.severity == "error"]
    print(json.dumps({"devices": len(results), "errors": len(errors)}, indent=2))
    for finding in errors:
        print(f"ERROR [{finding.device}/{finding.page}] {finding.message}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

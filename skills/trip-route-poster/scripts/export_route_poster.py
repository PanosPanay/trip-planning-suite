#!/usr/bin/env python3
import argparse
import asyncio
import contextlib
import functools
import http.server
import threading
from pathlib import Path

from playwright.async_api import async_playwright


@contextlib.contextmanager
def local_server(root):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        thread.join(timeout=5)


async def capture(browser, base_url, layout, width, height, scale, output):
    page = await browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)
    diagnostics = []
    page.on("console", lambda message: diagnostics.append(f"console {message.type}: {message.text}") if message.type == "error" else None)
    page.on("pageerror", lambda error: diagnostics.append(f"page error: {error}"))
    page.on("requestfailed", lambda request: diagnostics.append(f"request failed: {request.url} ({request.failure})"))
    await page.goto(f"{base_url}?layout={layout}&capture=1", wait_until="domcontentloaded")
    try:
        await page.wait_for_function("document.documentElement.dataset.posterReady === 'true'", timeout=45000)
    except Exception as error:
        details = "\n".join(diagnostics[-12:]) or "no browser diagnostics captured"
        raise RuntimeError(f"Poster HTML did not become ready for {layout}:\n{details}") from error
    await page.wait_for_timeout(1200)
    await page.locator("#poster").screenshot(path=str(output), scale="device")
    await page.close()


async def export(project, scale, layouts):
    output = project / "screenshots"
    output.mkdir(parents=True, exist_ok=True)
    with local_server(project) as port:
        base = f"http://127.0.0.1:{port}/maps/route-poster.html"
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            if "landscape" in layouts:
                await capture(browser, base, "landscape", 1920, 1350, scale, output / "route-poster-landscape-ultra-hd.png")
            if "portrait" in layouts:
                await capture(browser, base, "portrait", 1440, 2200, scale, output / "route-poster-portrait-ultra-hd.png")
            await browser.close()


def main():
    parser = argparse.ArgumentParser(description="Export approved editable route-poster HTML to high-resolution PNG files.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--approved", action="store_true", help="Confirm that the user approved the current HTML layout for screenshot export.")
    parser.add_argument("--scale", type=int, default=2)
    parser.add_argument("--layouts", default="landscape,portrait")
    args = parser.parse_args()
    if not args.approved:
        raise SystemExit("Refusing to export: review the HTML with the user first, then pass --approved.")
    if args.scale < 2:
        raise SystemExit("High-resolution export requires --scale 2 or higher.")
    project = args.project.expanduser().resolve()
    asyncio.run(export(project, args.scale, {item.strip() for item in args.layouts.split(",")}))
    print(project / "screenshots")


if __name__ == "__main__":
    main()

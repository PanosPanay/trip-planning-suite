#!/usr/bin/env python3
import argparse
import asyncio
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

from playwright.async_api import async_playwright


PRICE_KEYS = ("price", "amount", "salePrice", "displayPrice", "lowPrice", "minPrice", "avgPrice")
NAME_KEYS = ("hotelName", "name", "title")


def iter_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def first_text(node, keys):
    for key, value in node.items():
        if any(token.lower() in str(key).lower() for token in keys) and isinstance(value, str) and value.strip():
            return re.sub(r"\s+", " ", value).strip()
    return ""


def find_price(node):
    values = []
    for key, value in node.items():
        if not any(token.lower() in str(key).lower() for token in PRICE_KEYS) or isinstance(value, bool):
            continue
        if isinstance(value, (int, float)) and 50 <= value <= 100000:
            values.append(int(value))
        elif isinstance(value, str):
            match = re.search(r"([1-9]\d{1,5})", value)
            if match and 50 <= int(match.group(1)) <= 100000:
                values.append(int(match.group(1)))
    return min(values) if values else None


def terms(value):
    return [item for item in re.split(r"[,，/、\s]+", value) if item]


def json_candidates(payloads, includes):
    found = {}
    for payload in payloads:
        for node in iter_dicts(payload):
            name = first_text(node, NAME_KEYS)
            if not name or (includes and not any(term in name for term in includes)):
                continue
            item = {"name": name, "priceCandidate": find_price(node), "raw": json.dumps(node, ensure_ascii=False)[:1400]}
            old = found.get(name)
            if old is None or (item["priceCandidate"] and not old["priceCandidate"]):
                found[name] = item
    return sorted(found.values(), key=lambda item: (item["priceCandidate"] is None, item["priceCandidate"] or 999999, item["name"]))


def text_candidates(body, includes):
    lines = [re.sub(r"\s+", " ", line).strip() for line in body.splitlines() if line.strip()]
    found = []
    for index, line in enumerate(lines):
        if not any(token in line for token in ("酒店", "民宿", "客栈", "庄园", "山庄", "隐宿")):
            continue
        context = " | ".join(lines[index:index + 28])
        if includes and not any(term in context for term in includes):
            continue
        price = re.search(r"(?:¥|￥)\s*([1-9]\d{1,5})", context)
        score = re.search(r"([4-5]\.\d)\s*分", context)
        year = re.search(r"(20[2-9]\d)\s*(?:年)?(?:开业|装修|新开业)", context)
        found.append({"headline": line, "priceCandidate": int(price.group(1)) if price else None, "score": score.group(1) if score else None, "year": year.group(1) if year else None, "context": context[:1000]})
    return found


async def run(args):
    profile = args.profile.expanduser().resolve()
    profile.mkdir(parents=True, exist_ok=True)
    payloads, bodies = [], []
    async with async_playwright() as playwright:
        context = await playwright.chromium.launch_persistent_context(
            str(profile), headless=not args.headed, viewport={"width": 1365, "height": 900}, locale="zh-CN"
        )
        page = context.pages[0] if context.pages else await context.new_page()
        if args.login_only:
            await page.goto("https://hotels.ctrip.com/", wait_until="domcontentloaded", timeout=45000)
            print("Log in in the opened Ctrip browser, then press Enter here to close it.", flush=True)
            await asyncio.to_thread(input)
            await context.close()
            return None

        async def capture(response):
            if "json" not in response.headers.get("content-type", "").lower():
                return
            if not any(token in response.url.lower() for token in ("hotel", "ctrip", "search")):
                return
            try:
                payloads.append(await response.json())
            except Exception:
                pass

        page.on("response", lambda response: asyncio.create_task(capture(response)))
        url = (
            "https://hotels.ctrip.com/hotels/list?"
            f"city={quote(args.city)}&checkin={args.checkin}&checkout={args.checkout}"
            f"&keyword={quote(args.keyword)}&adults={args.adults}&children=0&rooms={args.rooms}"
        )
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(args.wait_ms)
        for _ in range(args.scrolls):
            await page.mouse.wheel(0, 900)
            await page.wait_for_timeout(700)
        bodies.append(await page.locator("body").inner_text(timeout=8000))
        await context.close()

    include_terms = terms(args.include or args.keyword)
    return {
        "query": {"city": args.city, "keyword": args.keyword, "checkin": args.checkin, "checkout": args.checkout, "rooms": args.rooms, "adults": args.adults, "include": include_terms},
        "warning": "Candidates require room-page verification for exact bed type, room count, total price, and cancellation.",
        "jsonCandidates": json_candidates(payloads, include_terms)[:args.limit],
        "textCandidates": text_candidates("\n".join(bodies), include_terms)[:args.limit],
    }


def main():
    parser = argparse.ArgumentParser(description="Discover current Ctrip hotel candidates using a reusable private browser profile.")
    parser.add_argument("--city", default="2")
    parser.add_argument("--keyword", default="")
    parser.add_argument("--include", default="")
    parser.add_argument("--checkin", default="")
    parser.add_argument("--checkout", default="")
    parser.add_argument("--rooms", type=int, default=1)
    parser.add_argument("--adults", type=int, default=2)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--scrolls", type=int, default=6)
    parser.add_argument("--wait-ms", type=int, default=10000)
    parser.add_argument("--profile", type=Path, default=Path.home() / ".codex" / "browser-profiles" / "ctrip-hotel")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--login-only", action="store_true")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    if not args.login_only and (not args.keyword or not args.checkin or not args.checkout):
        parser.error("--keyword, --checkin, and --checkout are required unless --login-only is used")
    result = asyncio.run(run(args))
    if result is None:
        return
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Query Ctrip flight prices and sort candidates from low to high.

The script uses Playwright to load Ctrip's flight results page. Ctrip's
internal APIs change frequently, so extraction combines JSON response scanning
with rendered text heuristics.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Any, Iterable
from urllib.parse import urlencode


CITY_CODES = {
    "北京": "BJS",
    "上海": "SHA",
    "广州": "CAN",
    "深圳": "SZX",
    "珠海": "ZUH",
    "澳门": "MFM",
    "香港": "HKG",
    "昆明": "KMG",
    "大理": "DLU",
    "丽江": "LJG",
    "香格里拉": "DIG",
    "迪庆": "DIG",
    "西双版纳": "JHG",
    "成都": "CTU",
    "成都天府": "TFU",
    "重庆": "CKG",
    "杭州": "HGH",
    "南京": "NKG",
    "武汉": "WUH",
    "长沙": "CSX",
    "厦门": "XMN",
    "福州": "FOC",
    "海口": "HAK",
    "三亚": "SYX",
    "西安": "SIA",
    "郑州": "CGO",
    "贵阳": "KWE",
    "南宁": "NNG",
    "桂林": "KWL",
    "青岛": "TAO",
    "济南": "TNA",
    "天津": "TSN",
    "沈阳": "SHE",
    "大连": "DLC",
    "哈尔滨": "HRB",
    "长春": "CGQ",
    "乌鲁木齐": "URC",
    "兰州": "LHW",
    "银川": "INC",
    "呼和浩特": "HET",
    "太原": "TYN",
    "石家庄": "SJW",
    "合肥": "HFE",
    "南昌": "KHN",
    "宁波": "NGB",
    "温州": "WNZ",
    "泉州": "JJN",
    "揭阳": "SWA",
    "汕头": "SWA",
    "湛江": "ZHA",
    "惠州": "HUZ",
}

PRICE_KEYS = (
    "price",
    "adultPrice",
    "childPrice",
    "salesPrice",
    "salePrice",
    "totalPrice",
    "amount",
    "fare",
    "ticketPrice",
    "displayPrice",
)
CONTEXT_KEY_HINTS = (
    "airline",
    "airlineName",
    "flightNo",
    "flightNumber",
    "craftType",
    "departure",
    "arrival",
    "depart",
    "arrive",
    "airport",
    "portName",
    "route",
    "time",
)


@dataclass(frozen=True)
class FlightPrice:
    price: int
    currency: str
    summary: str
    source: str
    airline: str = ""
    flight_no: str = ""
    depart_time: str = ""
    arrive_time: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query Ctrip flight prices for one-way or round-trip routes."
    )
    parser.add_argument("origin", help="Origin city name or airport/city code, e.g. 深圳 or SZX")
    parser.add_argument("destination", help="Destination city name or airport/city code, e.g. 丽江 or LJG")
    parser.add_argument("depart_date", help="Departure date in YYYY-MM-DD format")
    parser.add_argument("--return-date", help="Return date in YYYY-MM-DD format")
    parser.add_argument("--limit", type=int, default=15, help="Maximum rows to print")
    parser.add_argument("--timeout-ms", type=int, default=45000, help="Page timeout in milliseconds")
    parser.add_argument("--show-browser", action="store_true", help="Run Chromium headed for manual inspection")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser.parse_args()


def normalize_code(value: str) -> str:
    cleaned = value.strip()
    if re.fullmatch(r"[A-Za-z]{3}", cleaned):
        return cleaned.upper()
    if cleaned in CITY_CODES:
        return CITY_CODES[cleaned]
    raise SystemExit(
        f"Cannot resolve city '{value}'. Use a three-letter airport/city code such as SZX, ZUH, LJG, DLU, DIG, or KMG."
    )


def validate_date(value: str, field: str) -> None:
    try:
        dt.date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"{field} must be YYYY-MM-DD, got {value!r}.") from exc


def build_ctrip_url(origin_code: str, destination_code: str, depart_date: str, return_date: str | None) -> str:
    route_kind = "roundtrip" if return_date else "oneway"
    route = f"{route_kind}/{origin_code.upper()}-{destination_code.upper()}"
    params = {"date": f"{depart_date},{return_date}" if return_date else depart_date, "sortByPrice": "true"}
    return f"https://flights.ctrip.com/itinerary/{route}?{urlencode(params)}"


def coerce_price(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        price = int(round(float(value)))
    elif isinstance(value, str):
        match = re.search(r"(?:￥|¥|CNY|RMB)?\s*([1-9]\d{1,5})(?:\.\d+)?", value, re.I)
        if not match:
            return None
        price = int(match.group(1))
    else:
        return None
    if 50 <= price <= 50000:
        return price
    return None


def iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for item in value:
            yield from iter_dicts(item)


def compact_strings(value: Any, max_items: int = 16) -> list[str]:
    strings: list[str] = []

    def walk(item: Any) -> None:
        if len(strings) >= max_items:
            return
        if isinstance(item, str):
            text = re.sub(r"\s+", " ", item).strip()
            if 1 < len(text) <= 80 and not re.fullmatch(r"\d+", text):
                strings.append(text)
        elif isinstance(item, dict):
            for key, child in item.items():
                if any(hint.lower() in str(key).lower() for hint in CONTEXT_KEY_HINTS):
                    walk(child)
        elif isinstance(item, list):
            for child in item[:8]:
                walk(child)

    walk(value)
    return list(dict.fromkeys(strings))


def first_string_by_key(data: dict[str, Any], key_patterns: tuple[str, ...]) -> str:
    lowered = tuple(pattern.lower() for pattern in key_patterns)
    for key, value in data.items():
        if any(pattern in str(key).lower() for pattern in lowered):
            if isinstance(value, str) and value.strip():
                return re.sub(r"\s+", " ", value).strip()
    return ""


def extract_from_json(payload: Any) -> list[FlightPrice]:
    results: list[FlightPrice] = []
    results.extend(extract_structured_flights(payload))
    for node in iter_dicts(payload):
        if "flightSegments" in node and "priceList" in node:
            continue
        prices = []
        for key, value in node.items():
            if any(price_key.lower() in str(key).lower() for price_key in PRICE_KEYS):
                price = coerce_price(value)
                if price is not None:
                    prices.append(price)
        if not prices:
            continue
        context = compact_strings(node)
        if not context:
            continue
        summary = " | ".join(context[:8])
        if len(summary) < 4:
            continue
        results.append(
            FlightPrice(
                price=min(prices),
                currency="CNY",
                summary=summary,
                source="network-json",
                airline=first_string_by_key(node, ("airline", "carrier")),
                flight_no=first_string_by_key(node, ("flightno", "flightnumber")),
                depart_time=first_string_by_key(node, ("departtime", "departuretime", "deptime")),
                arrive_time=first_string_by_key(node, ("arrivetime", "arrivaltime", "arrtime")),
            )
        )
    return results


def extract_structured_flights(payload: Any) -> list[FlightPrice]:
    results: list[FlightPrice] = []
    for node in iter_dicts(payload):
        segments = node.get("flightSegments")
        price_list = node.get("priceList")
        if not isinstance(segments, list) or not isinstance(price_list, list):
            continue
        flights: list[dict[str, Any]] = []
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            for flight in segment.get("flightList", []):
                if isinstance(flight, dict):
                    flights.append(flight)
        if not flights:
            continue
        prices = [
            price
            for price_node in price_list
            for key in ("adultPrice", "price", "totalPrice", "salePrice")
            for price in [coerce_price(price_node.get(key) if isinstance(price_node, dict) else None)]
            if price is not None
        ]
        if not prices:
            continue
        first = flights[0]
        last = flights[-1]
        flight_numbers = []
        airlines = []
        for flight in flights:
            flight_no = str(flight.get("operateFlightNo") or flight.get("flightNo") or "").strip()
            airline = str(flight.get("operateAirlineName") or flight.get("marketAirlineName") or "").strip()
            if flight_no:
                flight_numbers.append(flight_no)
            if airline:
                airlines.append(airline)
        depart_time = str(first.get("departureDateTime") or "").strip()
        arrive_time = str(last.get("arrivalDateTime") or "").strip()
        depart_airport = "".join(
            str(first.get(key) or "") for key in ("departureAirportName", "departureTerminal")
        ).strip()
        arrive_airport = "".join(
            str(last.get(key) or "") for key in ("arrivalAirportName", "arrivalTerminal")
        ).strip()
        transfer_count = sum(int(seg.get("transferCount") or 0) for seg in segments if isinstance(seg, dict))
        summary = " | ".join(
            part
            for part in (
                " / ".join(dict.fromkeys(airlines)),
                " + ".join(dict.fromkeys(flight_numbers)),
                f"{first.get('departureCityName', '')} {depart_airport}",
                depart_time,
                f"{last.get('arrivalCityName', '')} {arrive_airport}",
                arrive_time,
                "直飞" if transfer_count == 0 and len(flights) == 1 else f"中转/经停 {max(transfer_count, len(flights) - 1)} 次",
            )
            if part and part.strip()
        )
        results.append(
            FlightPrice(
                price=min(prices),
                currency="CNY",
                summary=summary,
                source="batchSearch-json",
                airline=" / ".join(dict.fromkeys(airlines)),
                flight_no=" + ".join(dict.fromkeys(flight_numbers)),
                depart_time=depart_time,
                arrive_time=arrive_time,
            )
        )
    return results


def extract_from_text(text: str) -> list[FlightPrice]:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    results: list[FlightPrice] = []
    for index, line in enumerate(lines):
        for match in re.finditer(r"(?:￥|¥)\s*([1-9]\d{1,5})|([1-9]\d{1,5})\s*元", line):
            price = coerce_price(match.group(1) or match.group(2))
            if price is None:
                continue
            window = lines[max(0, index - 5) : min(len(lines), index + 6)]
            summary = " | ".join(window)
            if not re.search(r"航|机场|起飞|到达|直飞|中转|¥|￥|元|:", summary):
                continue
            results.append(
                FlightPrice(
                    price=price,
                    currency="CNY",
                    summary=summary[:500],
                    source="rendered-text",
                )
            )
    return results


def dedupe_and_sort(items: Iterable[FlightPrice]) -> list[FlightPrice]:
    best: dict[tuple[int, str, str, str], FlightPrice] = {}
    for item in items:
        key = (
            item.price,
            item.flight_no.lower(),
            item.depart_time.lower(),
            re.sub(r"\s+", "", item.summary[:80]).lower(),
        )
        current = best.get(key)
        if current is None or score_item(item) > score_item(current):
            best[key] = item
    return sorted(best.values(), key=lambda item: (item.price, -score_item(item), item.summary))


AIRPORT_HINTS = {
    "SZX": ("深圳", "宝安"),
    "ZUH": ("珠海", "金湾", "莲洲"),
    "LJG": ("丽江", "三义"),
    "DLU": ("大理", "凤仪"),
    "DIG": ("香格里拉", "迪庆"),
    "KMG": ("昆明", "长水"),
}


def route_terms(original_value: str, code: str) -> tuple[str, ...]:
    terms = [code.upper(), code.lower()]
    if not re.fullmatch(r"[A-Za-z]{3}", original_value.strip()):
        terms.append(original_value.strip())
    terms.extend(AIRPORT_HINTS.get(code.upper(), ()))
    return tuple(term for term in dict.fromkeys(terms) if term)


def filter_relevant_results(
    items: Iterable[FlightPrice],
    origin_terms: tuple[str, ...],
    destination_terms: tuple[str, ...],
    origin_code: str,
    destination_code: str,
) -> list[FlightPrice]:
    filtered = []
    origin_airport_terms = AIRPORT_HINTS.get(origin_code.upper(), ())[1:]
    destination_airport_terms = AIRPORT_HINTS.get(destination_code.upper(), ())[1:]
    for item in items:
        haystack = " ".join(
            part for part in (item.summary, item.airline, item.flight_no, item.depart_time, item.arrive_time) if part
        )
        has_origin = any(term in haystack for term in origin_terms)
        has_destination = any(term in haystack for term in destination_terms)
        has_flight_no = bool(re.search(r"[A-Z0-9]{2}\d{3,4}", haystack))
        has_both_airports = any(term in haystack for term in origin_airport_terms) and any(
            term in haystack for term in destination_airport_terms
        )
        if item.source == "rendered-text":
            has_flight_context = has_flight_no or has_both_airports
        else:
            has_flight_context = bool(item.flight_no or item.airline or has_flight_no or has_both_airports)
        if has_origin and has_destination and has_flight_context:
            filtered.append(item)
    return filtered


def score_item(item: FlightPrice) -> int:
    score = 0
    for value in (item.airline, item.flight_no, item.depart_time, item.arrive_time):
        if value:
            score += 2
    if item.source == "network-json":
        score += 2
    score += min(len(item.summary) // 80, 5)
    return score


async def query_with_playwright(url: str, timeout_ms: int, show_browser: bool) -> tuple[str, list[Any]]:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is required. Install with: python3 -m pip install playwright && python3 -m playwright install chromium"
        ) from exc

    captured_json: list[Any] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=not show_browser)
        context = await browser.new_context(
            locale="zh-CN",
            viewport={"width": 1365, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        async def capture_response(response: Any) -> None:
            request_url = response.url.lower()
            if not any(token in request_url for token in ("flight", "ctrip", "search", "batch")):
                return
            content_type = response.headers.get("content-type", "").lower()
            if "json" not in content_type and "javascript" not in content_type and "text" not in content_type:
                return
            try:
                payload = await response.json()
            except Exception:
                return
            captured_json.append(payload)

        page.on("response", lambda response: asyncio.create_task(capture_response(response)))
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout_ms // 2)
        except Exception:
            pass
        for _ in range(4):
            await page.mouse.wheel(0, 900)
            await page.wait_for_timeout(900)
        try:
            body_text = await page.locator("body").inner_text(timeout=5000)
        except Exception:
            body_text = ""
        await browser.close()
    return body_text, captured_json


def print_table(results: list[FlightPrice], limit: int) -> None:
    if not results:
        print("No flight prices were extracted. Try --show-browser to inspect whether Ctrip blocked the page or changed its layout.")
        return
    rows = results[:limit]
    print(f"{'Rank':>4}  {'Price':>8}  {'Source':<13}  Details")
    print("-" * 96)
    for rank, item in enumerate(rows, 1):
        detail_parts = [
            part
            for part in (item.airline, item.flight_no, item.depart_time, item.arrive_time, item.summary)
            if part
        ]
        details = " | ".join(detail_parts)
        details = re.sub(r"\s+", " ", details).strip()
        if len(details) > 150:
            details = details[:147] + "..."
        print(f"{rank:>4}  ¥{item.price:>7}  {item.source:<13}  {details}")


async def main() -> int:
    args = parse_args()
    validate_date(args.depart_date, "depart_date")
    if args.return_date:
        validate_date(args.return_date, "--return-date")
    origin_code = normalize_code(args.origin)
    destination_code = normalize_code(args.destination)
    url = build_ctrip_url(origin_code, destination_code, args.depart_date, args.return_date)

    body_text, payloads = await query_with_playwright(url, args.timeout_ms, args.show_browser)
    results: list[FlightPrice] = []
    for payload in payloads:
        results.extend(extract_from_json(payload))
    results.extend(extract_from_text(body_text))
    results = filter_relevant_results(
        results,
        route_terms(args.origin, origin_code),
        route_terms(args.destination, destination_code),
        origin_code,
        destination_code,
    )
    sorted_results = dedupe_and_sort(results)

    metadata = {
        "origin": args.origin,
        "origin_code": origin_code,
        "destination": args.destination,
        "destination_code": destination_code,
        "depart_date": args.depart_date,
        "return_date": args.return_date,
        "trip_type": "round-trip" if args.return_date else "one-way",
        "queried_url": url,
        "result_count": len(sorted_results),
    }

    if args.json:
        print(json.dumps({"metadata": metadata, "results": [asdict(item) for item in sorted_results[: args.limit]]}, ensure_ascii=False, indent=2))
    else:
        print(
            f"Ctrip {metadata['trip_type']} query: {origin_code} -> {destination_code}, "
            f"depart {args.depart_date}"
            + (f", return {args.return_date}" if args.return_date else "")
        )
        print(f"URL: {url}")
        print_table(sorted_results, args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

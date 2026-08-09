#!/usr/bin/env python3
import argparse
import asyncio
import html
import re
import shutil
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright


def require_command(name):
    if not shutil.which(name):
        raise SystemExit(f"Missing required command: {name}")


def markdown_fragment(source):
    result = subprocess.run(
        ["pandoc", "--from=gfm", "--to=html5", "--wrap=none", str(source)],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def extract_title(source, explicit):
    if explicit:
        return explicit
    match = re.search(r"^#\s+(.+)$", source.read_text(encoding="utf-8"), re.M)
    return match.group(1).strip() if match else source.stem


def prepare_fragment(fragment):
    fragment = re.sub(r"^<h1\b[^>]*>.*?</h1>\s*", "", fragment, count=1, flags=re.S)
    fragment = re.sub(r"<h3([^>]*)>", r'<h3\1 class="day-heading">', fragment)
    summary = re.search(
        r'(<h2[^>]*>(?:[^<]*(?:行程汇总|Trip summary)[^<]*)</h2>.*?)(?=<h2\b|\Z)',
        fragment,
        re.S | re.I,
    )
    if summary:
        block = f'<section class="summary-page">{summary.group(1)}</section>'
        fragment = fragment[: summary.start()] + block + fragment[summary.end() :]
    fragment = re.sub(
        r'<h2[^>]*>\s*(?:每日行程|详细行程|Detailed itinerary|Daily itinerary)\s*</h2>\s*',
        "",
        fragment,
        flags=re.I,
    )
    return f'<main class="markdown-body">{fragment}</main>'


def build_html(title, content, poster):
    poster_section = ""
    if poster:
        poster_section = (
            '<section class="route-page">'
            f'<img src="{html.escape(poster.resolve().as_uri())}" alt="{html.escape(title)} route poster">'
            '<p>实线为默认路线，虚线为天气或条件触发的备选路线。详细安排以正文为准。</p>'
            '</section>'
        )
    escaped = html.escape(title)
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{escaped}</title>
<style>
:root{{--ink:#17272d;--teal:#153f47;--gold:#d29a2e;--line:#d6ddd9;--soft:#f3f5f2}}
*{{box-sizing:border-box}}@page{{size:A4 portrait;margin:15mm 15mm 18mm}}@page landscape{{size:A4 landscape;margin:12mm 13mm 16mm}}
html,body{{margin:0;color:var(--ink);font-family:"PingFang SC","Microsoft YaHei",sans-serif;font-size:10pt;line-height:1.58}}
a{{color:#176d73;text-decoration:none;overflow-wrap:anywhere}}.cover{{min-height:252mm;padding:20mm 16mm;page-break-after:always;background:#f7f5ef;border-top:10mm solid var(--teal);display:flex;flex-direction:column}}
.cover h1{{margin:30mm 0 8mm;color:var(--teal);font-size:30pt;line-height:1.15}}.cover p{{font-size:12pt;color:#53656a}}.cover .rule{{margin-top:auto;border-top:1mm solid var(--gold);padding-top:5mm;font-size:9pt}}
.route-page{{page:landscape;page-break-after:always;break-inside:avoid}}.route-page img{{display:block;max-width:100%;max-height:174mm;margin:0 auto;border:.25mm solid var(--line)}}.route-page p{{font-size:8.5pt;color:#5e6a6f}}
.markdown-body>h2{{break-before:page;margin:0 0 5mm;padding-bottom:3mm;color:var(--teal);font-size:19pt;border-bottom:1mm solid var(--gold)}}
h3{{margin:7mm 0 3mm;color:#245a61;font-size:14pt;break-after:avoid}}h3.day-heading{{break-before:page;margin-top:0;padding:4mm 5mm;color:white;background:var(--teal);border-left:2mm solid var(--gold)}}h4{{color:#a95232;break-after:avoid}}
p{{margin:0 0 3mm;orphans:3;widows:3}}ul,ol{{margin:2mm 0 4mm;padding-left:6mm}}li{{margin-bottom:1.5mm;break-inside:avoid}}
table{{width:100%;margin:4mm 0 6mm;border-collapse:collapse;table-layout:fixed;font-size:8.4pt}}thead{{display:table-header-group}}tr{{break-inside:avoid}}th{{padding:2.5mm;color:white;background:var(--teal);border:.25mm solid #b9c6c2;text-align:left}}td{{padding:2.4mm;vertical-align:top;border:.25mm solid #cfd8d4;overflow-wrap:anywhere}}tbody tr:nth-child(even) td{{background:var(--soft)}}
blockquote{{margin:4mm 0;padding:3mm 5mm;background:var(--soft);border-left:1.2mm solid #2e7d62}}.summary-page{{page:landscape;page-break-before:always;page-break-after:always}}.summary-page h2{{margin:0 0 4mm;color:var(--teal);font-size:20pt;border-bottom:1mm solid var(--gold)}}.summary-page table{{font-size:7.3pt;line-height:1.35}}
</style></head><body><section class="cover"><h1>{escaped}</h1><p>可执行旅行计划 · 路线、住宿、预约、费用与风险汇总</p><p class="rule">本文件由已确认的行程 Markdown 生成；实时价格、天气、路况和政策请在出发前复核。</p></section>{poster_section}{content}</body></html>"""


async def export_pdf(html_path, pdf_path, title):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(html_path.resolve().as_uri(), wait_until="load")
        await page.emulate_media(media="print")
        await page.pdf(
            path=str(pdf_path),
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=(
                '<div style="width:100%;font-size:8px;color:#66757a;padding:0 15mm;display:flex;justify-content:space-between">'
                f'<span>{html.escape(title)}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
            ),
        )
        await browser.close()


def main():
    parser = argparse.ArgumentParser(description="Export canonical trip Markdown and approved route poster to a shareable PDF.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--source", default="docs/itinerary.md")
    parser.add_argument("--poster", default=None)
    parser.add_argument("--output", default="output/pdf/itinerary-share.pdf")
    parser.add_argument("--title")
    args = parser.parse_args()
    require_command("pandoc")
    require_command("pdftoppm")
    project = args.project.expanduser().resolve()
    source = project / args.source
    poster = project / args.poster if args.poster else None
    if not source.exists():
        raise SystemExit(f"Missing itinerary Markdown: {source}")
    if poster and not poster.exists():
        raise SystemExit(f"Missing approved route poster: {poster}")
    title = extract_title(source, args.title)
    temp = project / "tmp" / "pdf"
    preview = project / "tmp" / "pdf-preview"
    output = project / args.output
    temp.mkdir(parents=True, exist_ok=True)
    preview.mkdir(parents=True, exist_ok=True)
    for old_page in preview.glob("page-*.png"):
        old_page.unlink()
    output.parent.mkdir(parents=True, exist_ok=True)
    html_path = temp / "itinerary-share.html"
    html_path.write_text(build_html(title, prepare_fragment(markdown_fragment(source)), poster), encoding="utf-8")
    asyncio.run(export_pdf(html_path, output, title))
    prefix = preview / "page"
    subprocess.run(["pdftoppm", "-png", "-r", "150", str(output), str(prefix)], check=True)
    print(output)
    print(preview)


if __name__ == "__main__":
    main()

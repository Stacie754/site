#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright", "httpx"]
# ///
"""
Debug: check login status + directly call user_posted API + inspect page HTML.
"""

import asyncio
import json
import re
from pathlib import Path

import httpx
from playwright.async_api import async_playwright

USER_ID = "6327f4ba000000002303bee1"
PROFILE_URL = f"https://www.xiaohongshu.com/user/profile/{USER_ID}"
COOKIE_FILE = Path("/home/qihang/repos/staice-site/scripts/xhs_cookies.txt")

COOKIE_STR = COOKIE_FILE.read_text(encoding="utf-8").strip()

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "origin": "https://www.xiaohongshu.com",
    "referer": "https://www.xiaohongshu.com/",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "cookie": COOKIE_STR,
    "x-s": "",
    "x-t": "",
}


def direct_api_test():
    """Try calling user_posted API directly with httpx."""
    print("\n=== Direct API test (httpx) ===")

    # 1. Check login status
    resp = httpx.get(
        "https://edith.xiaohongshu.com/api/sns/web/v2/user/me",
        headers=HEADERS,
        follow_redirects=True,
    )
    print(f"user/me status: {resp.status_code}")
    try:
        data = resp.json()
        print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
    except Exception:
        print(resp.text[:500])

    # 2. Try user_posted
    print("\n--- user_posted ---")
    resp2 = httpx.get(
        "https://edith.xiaohongshu.com/api/sns/web/v1/user_posted",
        params={"num": 30, "cursor": "", "user_id": USER_ID, "image_formats": "jpg,webp,avif"},
        headers=HEADERS,
        follow_redirects=True,
    )
    print(f"user_posted status: {resp2.status_code}")
    try:
        data2 = resp2.json()
        print(json.dumps(data2, ensure_ascii=False, indent=2)[:2000])
    except Exception:
        print(resp2.text[:500])


def load_cookies(path):
    raw = path.read_text(encoding="utf-8").strip().replace("\n", "; ").replace("\r", "")
    pairs = [p.strip() for p in raw.split(";") if "=" in p.strip()]
    cookies = []
    for pair in pairs:
        name, _, value = pair.partition("=")
        if name.strip():
            cookies.append({"name": name.strip(), "value": value.strip(),
                            "domain": ".xiaohongshu.com", "path": "/"})
    return cookies


async def playwright_test():
    """Check what the page actually looks like after load."""
    print("\n=== Playwright page content check ===")
    cookies = load_cookies(COOKIE_FILE)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
        )
        # Add cookies to all relevant domains
        await context.add_cookies(cookies)
        for c in cookies:
            await context.add_cookies([{**c, "domain": "edith.xiaohongshu.com"}])

        intercepted = []
        async def on_resp(resp):
            if "edith.xiaohongshu.com/api" in resp.url:
                intercepted.append(resp.url)
                if "user/me" in resp.url:
                    try:
                        body = await resp.json()
                        print(f"\nuser/me response: {json.dumps(body, ensure_ascii=False)[:500]}")
                    except Exception:
                        pass

        page = await context.new_page()
        page.on("response", on_resp)

        await page.goto(PROFILE_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        # Get visible text on page
        body_text = await page.inner_text("body")
        print(f"\nPage body text (first 1000 chars):\n{body_text[:1000]}")

        # Look for note IDs in raw HTML
        html = await page.content()
        note_ids = re.findall(r'"id":\s*"([a-f0-9]{24})"', html)
        print(f"\nNote IDs in HTML: {note_ids[:10]}")

        # Any links with /explore/
        links = await page.query_selector_all("a[href*='/explore/']")
        print(f"Explore links: {len(links)}")

        print(f"\nAll edith API calls: {len(intercepted)}")
        for u in intercepted:
            print(f"  {u[:100]}")

        await browser.close()


if __name__ == "__main__":
    direct_api_test()
    asyncio.run(playwright_test())

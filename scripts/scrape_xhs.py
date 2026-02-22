#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright",
# ]
# ///
"""
Xiaohongshu profile scraper.

1. Scroll profile page to load all note cards
2. Extract note IDs from DOM links
3. Click each note (from profile) in sequence, capturing feed API + comments
4. Save each note as markdown

Usage:
  1. Put your cookies in scripts/xhs_cookies.txt
  2. uv run scripts/scrape_xhs.py
"""

import asyncio
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright

USER_ID = "6327f4ba000000002303bee1"
PROFILE_URL = f"https://www.xiaohongshu.com/user/profile/{USER_ID}"
OUTPUT_DIR = Path("/home/qihang/repos/staice-site/reference/red-posts")
COOKIE_FILE = Path("/home/qihang/repos/staice-site/scripts/xhs_cookies.txt")


def sanitize_filename(text: str, max_len: int = 50) -> str:
    safe = re.sub(r'[<>:"/\\|?*\n\r\t]', "", text)
    safe = safe.strip()[:max_len]
    return safe or "untitled"


def load_cookies(path: Path) -> list[dict]:
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8").strip().replace("\n", "; ").replace("\r", "")
    pairs = [p.strip() for p in raw.split(";") if "=" in p.strip()]
    cookies = []
    for pair in pairs:
        name, _, value = pair.partition("=")
        if name.strip():
            cookies.append(
                {"name": name.strip(), "value": value.strip(),
                 "domain": ".xiaohongshu.com", "path": "/"}
            )
    return cookies


def clean_desc(desc: str) -> str:
    desc = re.sub(r"#[^#\[\]]+\[话题\]#?", "", desc)
    return desc.strip()


class XHSScraper:
    def __init__(self):
        self.feed_data: dict[str, dict] = {}
        self.comments: dict[str, list] = {}

    async def on_response(self, response):
        url = response.url
        try:
            if "/api/sns/web/v1/feed" in url:
                data = await response.json()
                if data.get("success") and data.get("data"):
                    for item in data["data"].get("items", []):
                        nc = item.get("note_card", {})
                        nid = nc.get("note_id") or item.get("id", "")
                        if nid and nc:
                            self.feed_data[nid] = nc

            elif "/api/sns/web/v2/comment/page" in url:
                data = await response.json()
                if data.get("success") and data.get("data"):
                    comments = data["data"].get("comments", [])
                    m = re.search(r"note_id=([^&]+)", url)
                    if m:
                        nid = m.group(1)
                        self.comments.setdefault(nid, []).extend(comments)

            elif "/api/sns/web/v2/comment/sub/page" in url:
                data = await response.json()
                if data.get("success") and data.get("data"):
                    sub = data["data"].get("comments", [])
                    m = re.search(r"note_id=([^&]+)", url)
                    if m:
                        nid = m.group(1)
                        self.comments.setdefault(nid, []).extend(sub)
        except Exception:
            pass

    def extract_comments(self, note_id: str) -> list[dict]:
        result = []
        for c in self.comments.get(note_id, []):
            author = c.get("user_info", {}).get("nickname", "匿名")
            text = c.get("content", "").strip()
            if text:
                result.append({"author": author, "text": text})
            for sub in c.get("sub_comments", []):
                sa = sub.get("user_info", {}).get("nickname", "匿名")
                st = sub.get("content", "").strip()
                if st:
                    result.append({"author": f"  ↳ {sa}", "text": st})
        return result

    def save_markdown(self, index: int, note_id: str, title: str, desc: str,
                      comments: list[dict]) -> Path:
        title = title or f"post_{index}"
        fname = f"{index:03d}_{sanitize_filename(title)}.md"
        fpath = OUTPUT_DIR / fname
        url = f"https://www.xiaohongshu.com/explore/{note_id}"

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**来源**: {url}\n\n")
            f.write("---\n\n")
            if desc:
                f.write("## 正文\n\n")
                f.write(clean_desc(desc))
                f.write("\n\n")
            else:
                f.write("## 正文\n\n*(未获取到文字内容)*\n\n")
            if comments:
                f.write("---\n\n")
                f.write(f"## 评论（共 {len(comments)} 条）\n\n")
                for c in comments:
                    f.write(f"**{c['author']}**: {c['text']}\n\n")
            else:
                f.write("---\n\n## 评论\n\n*(无评论或未能加载)*\n\n")

        return fpath


async def collect_note_ids(page) -> list[dict]:
    """Extract all unique note IDs and titles from profile page DOM."""
    # Use JavaScript to get all note info at once
    notes = await page.evaluate("""
        () => {
            const items = document.querySelectorAll('section.note-item');
            const results = [];
            const seen = new Set();
            for (const item of items) {
                const link = item.querySelector('a[href*="/explore/"]');
                if (!link) continue;
                const href = link.getAttribute('href') || '';
                const match = href.match(/\\/explore\\/([a-f0-9]{24})/);
                if (!match) continue;
                const noteId = match[1];
                if (seen.has(noteId)) continue;
                seen.add(noteId);
                // Get title from the item text
                const titleEl = item.querySelector('.title, [class*=title]');
                const title = titleEl ? titleEl.textContent.trim() : item.textContent.trim().split('\\n')[0];
                results.push({noteId, title: title.substring(0, 80)});
            }
            return results;
        }
    """)
    return notes


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cookies = load_cookies(COOKIE_FILE)
    if not cookies:
        print(f"[!] No cookies found at {COOKIE_FILE}")
        sys.exit(1)

    print(f"[+] Loaded {len(cookies)} cookies")
    scraper = XHSScraper()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled",
                  "--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
        )
        await context.add_cookies(cookies)

        page = await context.new_page()
        page.on("response", scraper.on_response)

        print(f"[+] Opening profile: {PROFILE_URL}")
        await page.goto(PROFILE_URL, wait_until="domcontentloaded")
        await asyncio.sleep(4)

        page_title = await page.title()
        print(f"    Page title: {page_title}")
        if "登录" in page_title or "login" in page_title.lower():
            print("[!] Login page — cookies invalid/expired.")
            sys.exit(1)

        # Phase 1: Scroll to load all note cards
        print("\n--- Phase 1: Loading all note cards ---")
        prev_count = 0
        stall = 0
        while stall < 5:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            notes = await collect_note_ids(page)
            cur_count = len(notes)
            if cur_count == prev_count:
                stall += 1
            else:
                stall = 0
            prev_count = cur_count
            print(f"  unique notes: {cur_count}")

        all_notes = await collect_note_ids(page)
        total = len(all_notes)
        print(f"\n[+] Found {total} unique notes\n")

        if total == 0:
            print("[!] No notes found. Check profile page.")
            await browser.close()
            sys.exit(1)

        # Phase 2: For each note, click from profile to open modal
        print("--- Phase 2: Scraping each note ---")

        for idx, note_info in enumerate(all_notes, 1):
            note_id = note_info["noteId"]
            title_preview = note_info["title"]

            print(f"\n[{idx}/{total}] {title_preview[:50]}")

            # Navigate back to profile if needed
            if "/user/profile/" not in page.url:
                await page.goto(PROFILE_URL, wait_until="domcontentloaded")
                await asyncio.sleep(3)

            # Find and click the specific note by its href
            clicked = False
            try:
                link = await page.query_selector(f'a[href*="/explore/{note_id}"]')
                if link:
                    await link.scroll_into_view_if_needed()
                    await asyncio.sleep(0.3)
                    await link.click()
                    await asyncio.sleep(3.5)
                    clicked = True
            except Exception as e:
                print(f"  Click failed: {e}")

            if not clicked:
                # Fallback: try scrolling to find it
                for scroll_try in range(10):
                    await page.evaluate("window.scrollBy(0, 500)")
                    await asyncio.sleep(0.5)
                    link = await page.query_selector(f'a[href*="/explore/{note_id}"]')
                    if link:
                        try:
                            await link.scroll_into_view_if_needed()
                            await asyncio.sleep(0.3)
                            await link.click()
                            await asyncio.sleep(3.5)
                            clicked = True
                            break
                        except Exception:
                            pass
                if not clicked:
                    print(f"  Could not click note, skipping")
                    continue

            # Scroll modal to load comments
            for _ in range(5):
                try:
                    await page.evaluate("""
                        const containers = document.querySelectorAll(
                            '[class*="detail"], [class*="content"], [class*="scroller"]'
                        );
                        for (const c of containers) {
                            if (c.scrollHeight > c.clientHeight + 50) {
                                c.scrollTop = c.scrollHeight;
                            }
                        }
                    """)
                except Exception:
                    pass
                await page.keyboard.press("End")
                await asyncio.sleep(1.2)

            # Extract content from API data
            title = ""
            desc = ""
            if note_id in scraper.feed_data:
                nc = scraper.feed_data[note_id]
                title = nc.get("title", "")
                desc = nc.get("desc", "")

            if not title:
                title = title_preview

            comments = scraper.extract_comments(note_id)

            print(f"  desc={len(desc)}c comments={len(comments)}")

            fpath = scraper.save_markdown(idx, note_id, title, desc, comments)
            print(f"  -> {fpath.name}")

            # Close modal / navigate back
            try:
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.5)
                if "/explore/" in page.url:
                    await page.go_back()
                    await asyncio.sleep(1.5)
            except Exception:
                pass

            await asyncio.sleep(0.5)

        print(f"\n[+] Done! Saved {total} posts to {OUTPUT_DIR}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

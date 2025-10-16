import argparse, asyncio, requests, xml.etree.ElementTree as ET
from trafilatura import extract
from src.utils import clean_text, chunk_text, write_jsonl, ensure_dir
from playwright.async_api import async_playwright

# --- load sitemap or url list ---
def parse_sitemap(sitemap_url: str):
    import time

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    urls = []
    tries = 0
    while tries < 3:
        try:
            print(f"[FETCH] Loading sitemap: {sitemap_url}")
            r = requests.get(sitemap_url, headers=headers, timeout=30)
            if r.status_code == 200:
                root = ET.fromstring(r.text)
                ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
                for loc in root.findall(".//sm:url/sm:loc", ns):
                    loc_text = loc.text.strip()
                    if loc_text:
                        urls.append(loc_text)
                print(f"[OK] Found {len(urls)} URLs in sitemap.")
                return urls
            else:
                print(f"⚠️ Got HTTP {r.status_code}. Retrying...")
        except Exception as e:
            print(f"⚠️ Error fetching sitemap: {e}. Retrying...")
        tries += 1
        time.sleep(2)

    print("❌ Failed to fetch sitemap after 3 tries.")
    return []

# --- dynamic JS rendering ---
async def get_rendered_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()
        return html

async def scrape_urls(urls, out, max_tokens, overlap):
    rows = []
    for u in urls:
        print(f"[SCRAPE] {u}")
        try:
            html = await get_rendered_html(u)
            txt = extract(html, include_comments=False, include_images=False)
            cleaned = clean_text(txt)
            for i, chunk in enumerate(chunk_text(cleaned, max_tokens, overlap)):
                rows.append({"id": f"{u}#chunk-{i}", "source": u, "text": chunk})
        except Exception as e:
            print(f"⚠️ Failed to scrape {u}: {e}")
    ensure_dir("data")
    write_jsonl(out, rows)
    print(f"[DONE] wrote {len(rows)} chunks to {out}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", nargs="*")
    parser.add_argument("--sitemap")
    parser.add_argument("--out", default="data/chunks.jsonl")
    parser.add_argument("--max_tokens", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=120)
    args = parser.parse_args()

    urls = []
    if args.urls:
        urls.extend(args.urls)
    if args.sitemap:
        urls.extend(parse_sitemap(args.sitemap))
    if not urls:
        raise SystemExit("❌ Please provide --urls or --sitemap")

    asyncio.run(scrape_urls(sorted(set(urls)), args.out, args.max_tokens, args.overlap))

if __name__ == "__main__":
    main()

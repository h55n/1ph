"""
test_scraping_methods.py - Test 4 scraping methods and compare quality.
Tests each method against a known hackathon URL and scores the output.
"""
import httpx
import time
from bs4 import BeautifulSoup
import json

TEST_URL = "https://unstop.com/hackathons/smart-india-hackathon-2024-government-of-india-1233627"

# ─── Method 1: Jina Reader (Cloud-rendered Markdown) ─────────────────────────
def method_jina(url: str) -> dict:
    """Uses Jina AI reader to get JavaScript-rendered markdown. Free."""
    start = time.time()
    try:
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            r = client.get(f"https://r.jina.ai/{url}", headers={"X-Return-Format": "markdown"})
        elapsed = time.time() - start
        text = r.text[:5000]
        return {
            "method": "Jina Reader",
            "cost": "Free",
            "time_s": round(elapsed, 2),
            "length": len(r.text),
            "status": r.status_code,
            "preview": text[:500],
            "js_rendered": True,
            "score": 8 if r.status_code == 200 and len(r.text) > 500 else 2
        }
    except Exception as e:
        return {"method": "Jina Reader", "error": str(e), "score": 0}


# ─── Method 2: Raw httpx + BeautifulSoup (Static HTML) ───────────────────────
def method_httpx_bs4(url: str) -> dict:
    """Direct HTTP fetch + BeautifulSoup parsing. Free, fast, fails on SPA."""
    start = time.time()
    try:
        with httpx.Client(timeout=15, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as client:
            r = client.get(url)
        elapsed = time.time() - start
        soup = BeautifulSoup(r.text, "html.parser")
        # Remove scripts and styles
        for tag in soup(["script", "style", "noscript"]): tag.decompose()
        text = soup.get_text(separator=" ", strip=True)[:5000]
        return {
            "method": "httpx + BeautifulSoup",
            "cost": "Free",
            "time_s": round(elapsed, 2),
            "length": len(text),
            "status": r.status_code,
            "preview": text[:500],
            "js_rendered": False,
            "score": 5 if r.status_code == 200 and len(text) > 200 else 1
        }
    except Exception as e:
        return {"method": "httpx + BeautifulSoup", "error": str(e), "score": 0}


# ─── Method 3: Playwright Headless Browser (JS Rendered) ─────────────────────
def method_playwright(url: str) -> dict:
    """Full headless Chromium browser. Accurate but slow and heavy."""
    start = time.time()
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)  # Wait for JS to run
            text = page.inner_text("body")[:5000]
            browser.close()
        elapsed = time.time() - start
        return {
            "method": "Playwright (Chromium)",
            "cost": "Free (self-hosted, heavy)",
            "time_s": round(elapsed, 2),
            "length": len(text),
            "status": 200,
            "preview": text[:500],
            "js_rendered": True,
            "score": 9 if len(text) > 500 else 3
        }
    except ImportError:
        return {"method": "Playwright", "error": "playwright not installed (pip install playwright)", "score": 0, "time_s": 0}
    except Exception as e:
        elapsed = time.time() - start
        return {"method": "Playwright (Chromium)", "error": str(e), "score": 0, "time_s": round(elapsed, 2)}


# ─── Method 4: ScrapingAnt / ScrapeNinja API (Cloud Anti-Bot) ────────────────
def method_scrapeninja(url: str) -> dict:
    """
    Uses ScrapeNinja free tier (uses JS execution, bypasses Cloudflare).
    Free tier: 1000 req/month. No key needed for basic usage.
    Alternative: https://scrapeninja.net
    """
    start = time.time()
    try:
        # ScrapeNinja API - free tier available
        api_url = "https://scrapeninja.net/api/scrape"
        with httpx.Client(timeout=25) as client:
            r = client.post(api_url, json={
                "url": url,
                "retryNum": 1,
                "geo": "us",
                "js": True,
            }, headers={"x-api-key": "demo"})  # demo key for testing
        elapsed = time.time() - start
        
        if r.status_code == 200:
            data = r.json()
            body = data.get("body", "")
            soup = BeautifulSoup(body, "html.parser")
            for tag in soup(["script", "style"]): tag.decompose()
            text = soup.get_text(" ", strip=True)[:5000]
            return {
                "method": "ScrapeNinja API",
                "cost": "~$0.001/req (free tier available)",
                "time_s": round(elapsed, 2),
                "length": len(text),
                "status": r.status_code,
                "preview": text[:500],
                "js_rendered": True,
                "score": 7 if len(text) > 200 else 2
            }
        else:
            return {"method": "ScrapeNinja API", "status": r.status_code, "error": r.text[:200], "score": 1, "time_s": round(elapsed, 2)}
    except Exception as e:
        return {"method": "ScrapeNinja API", "error": str(e), "score": 0, "time_s": round(time.time() - start, 2)}


# ─── Run all tests ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Testing 4 scraping methods on: {TEST_URL}\n{'='*70}")
    
    results = []
    for method_fn in [method_jina, method_httpx_bs4, method_playwright, method_scrapeninja]:
        print(f"\nTesting: {method_fn.__name__}...")
        result = method_fn(TEST_URL)
        results.append(result)
        print(f"  Status: {result.get('status', 'N/A')} | Time: {result.get('time_s', '?')}s | Length: {result.get('length', 0):,} chars | Score: {result.get('score', 0)}/10")
        if "error" in result:
            print(f"  ERROR: {result['error']}")
        else:
            print(f"  Preview: {result.get('preview', '')[:200]!r}")
    
    print(f"\n{'='*70}")
    print("WINNER RECOMMENDATION:")
    best = max(results, key=lambda x: x.get("score", 0))
    print(f"  {best['method']} — Score: {best.get('score', 0)}/10")
    print(f"  Cost: {best.get('cost', '?')} | Time: {best.get('time_s', '?')}s")
    print(f"\nFor production: Jina Reader is recommended as it is free, cloud-hosted,")
    print(f"handles JS rendering, and requires zero infrastructure overhead.")

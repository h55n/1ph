import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline"))
from zerocrawl_bridge import fetch_markdown, fetch_html, fetch_js_page

TEST_URLS = [
    "https://example.com",
    "https://devpost.com/hackathons"
]

def run_tests():
    print("============================================================")
    print("  Jina Bridge Test Suite")
    print("============================================================\n")

    for url in TEST_URLS:
        print(f"Testing URL: {url}")
        
        # Test markdown
        t0 = time.time()
        md = fetch_markdown(url)
        t1 = time.time()
        print(f"  -> Markdown Length: {len(md)} chars | Time: {t1 - t0:.2f}s")
        
        # Test HTML
        t0 = time.time()
        html = fetch_html(url)
        t1 = time.time()
        print(f"  -> HTML Length:     {len(html)} chars | Time: {t1 - t0:.2f}s")
        print()

if __name__ == "__main__":
    run_tests()

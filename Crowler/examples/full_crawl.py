#!/usr/bin/env python3
"""Full site crawl — recursively scrape all pages under a domain."""
import asyncio
from zerocrawl import crawl
from zerocrawl.models import CrawlOptions

async def main():
    url = "https://example.com"
    count = 0
    
    print(f"Crawling {url}...")
    async for result in crawl(url, max_pages=20, max_depth=2, concurrency=3):
        count += 1
        print(f"  [{count:3d}] {result.status:8} {result.mode:10} {result.url}")
        if result.metadata.title:
            print(f"        Title: {result.metadata.title}")
    
    print(f"\nCrawled {count} pages total.")

if __name__ == "__main__":
    asyncio.run(main())

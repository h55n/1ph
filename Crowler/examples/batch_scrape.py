#!/usr/bin/env python3
"""Batch scraping multiple URLs with progress tracking."""
import asyncio
from zerocrawl import batch_scrape
from zerocrawl.models import ScrapeOptions

URLS = [
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
]

async def main():
    print(f"Submitting batch of {len(URLS)} URLs...")
    job = await batch_scrape(URLS, options=ScrapeOptions(mode="fast"), concurrency=3)
    print(f"Job ID: {job.id}")

    # Poll until complete
    while True:
        status = await job.get_status()
        print(f"Progress: {status.completed}/{status.total} done, {status.failed} failed")
        if status.status == "completed":
            break
        await asyncio.sleep(1)

    # Get results
    results = await job.get_results()
    for r in results:
        print(f"  {r.status:8} {r.url} — {r.content.word_count} words")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""Basic single-URL scrape — the simplest possible usage."""
import asyncio
from zerocrawl import scrape

async def main():
    # One line to scrape any URL
    result = await scrape("https://example.com")
    
    print(f"Status:     {result.status}")
    print(f"Mode:       {result.mode}")
    print(f"Timing:     {result.timing_ms}ms")
    print(f"Title:      {result.metadata.title}")
    print(f"Words:      {result.content.word_count}")
    print()
    print("=== Markdown Content (first 500 chars) ===")
    print(result.content.markdown[:500])

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""Extract structured data using rule-based extraction (no AI needed)."""
import asyncio
from zerocrawl import scrape

async def main():
    # Scrape a page with Schema.org markup
    result = await scrape("https://schema.org/Product")
    
    print("=== Schema.org Data ===")
    for item in result.structured.schema_org[:3]:
        print(f"  Type: {item.get('@type', 'Unknown')}")
        print(f"  Name: {item.get('name', 'N/A')}")
        print()

    print("=== Open Graph ===")
    for k, v in list(result.structured.open_graph.items())[:5]:
        print(f"  {k}: {v}")

    print()
    print("=== Patterns Detected ===")
    print(f"  Emails:  {result.structured.patterns.emails}")
    print(f"  Phones:  {result.structured.patterns.phones}")
    print(f"  Prices:  {result.structured.patterns.prices}")

    print()
    print("=== Links ===")
    print(f"  Internal: {len(result.structured.links.internal)}")
    print(f"  External: {len(result.structured.links.external)}")
    print(f"  Downloads:{len(result.structured.links.downloads)}")

if __name__ == "__main__":
    asyncio.run(main())

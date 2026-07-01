#!/usr/bin/env python3
"""AI-powered extraction using local Ollama — zero cost, fully offline."""
import asyncio
from zerocrawl import scrape
from zerocrawl.ai.ollama import OllamaExtractor

async def main():
    # Define what you want to extract
    schema = {
        "title": "string",
        "description": "string", 
        "main_topic": "string",
        "has_contact_info": "boolean",
    }

    extractor = OllamaExtractor(model="llama3.1:8b")
    
    result = await scrape(
        "https://example.com",
        ai_extractor=extractor,
        ai_schema=schema,
    )

    print(f"Status: {result.status}")
    print(f"Title:  {result.metadata.title}")
    print()
    if result.ai_extracted:
        print("=== AI Extracted ===")
        import json
        print(json.dumps(result.ai_extracted, indent=2))
    elif result.ai_error:
        print(f"AI Error: {result.ai_error}")
        print("(Ollama must be running: `ollama serve` and `ollama pull llama3.1:8b`)")

if __name__ == "__main__":
    asyncio.run(main())

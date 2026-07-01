# 🕷️ ZeroCrawl

> Zero-cost, plug-and-play web scraping engine.  
> One function call. No paid APIs. No infrastructure. Runs on your laptop.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Quick Start

```bash
pip install zerocrawl
playwright install firefox   # for browser mode (JS-rendered pages)
```

```python
import asyncio
from zerocrawl import scrape

result = asyncio.run(scrape("https://example.com"))
print(result.content.markdown)      # Clean markdown
print(result.metadata.title)        # Page title
print(result.structured.schema_org) # Structured data
```

Synchronous (no async):
```python
from zerocrawl import scrape_sync
result = scrape_sync("https://example.com")
```

---

## Features

- **Three fetch modes** — automatically escalates from fast HTTP → headless browser → aggressive human simulation
- **TLS fingerprint mimicry** — `curl_cffi` makes requests that look like real Chrome/Firefox/Safari
- **Camoufox integration** — hardened Firefox with canvas, WebGL, audio fingerprint randomisation
- **Rule-based extraction** — Schema.org JSON-LD, Open Graph, tables, links, images, patterns — no AI required
- **Optional AI layer** — plug in Ollama (free/local), OpenAI, Anthropic, or Gemini
- **Batch job queue** — SQLite-backed, async workers, webhook callbacks, result caching
- **Full site crawler** — sitemap.xml parsing, URL deduplication, configurable depth/scope
- **REST API** — FastAPI server at `localhost:8765`, Firecrawl-compatible endpoint design
- **CLI** — `zerocrawl scrape`, `zerocrawl crawl`, `zerocrawl batch`, `zerocrawl serve`

---

## The Three-Mode Engine

| Mode | Technology | Speed | Coverage |
|------|-----------|-------|----------|
| `fast` | `curl_cffi` TLS spoof | 2–10s | ~65% of web |
| `browser` | Playwright + Camoufox | 15–60s | ~90% of web |
| `aggressive` | Browser + human simulation | 30–120s | ~99% of web |

Mode is selected automatically. Override with `mode="browser"`.

---

## API Reference

### `scrape(url, ...)`
```python
result = await scrape(
    url="https://example.com",
    mode="auto",            # auto | fast | browser | aggressive
    timeout=60,
    screenshot=False,
    proxy=None,
    cache_ttl=3600,
    force_refresh=False,
    ai_extractor=None,      # Optional AI plugin
    ai_schema=None,         # {"field": "type", ...}
)
```

### `ScrapeResult` fields
```python
result.status              # "success" | "partial" | "failed"
result.mode                # "fast" | "browser" | "aggressive"
result.timing_ms           # Total time in ms

result.content.markdown    # Main content as Markdown
result.content.html        # Cleaned HTML
result.content.text        # Plain text
result.content.word_count  # Word count

result.metadata.title
result.metadata.description
result.metadata.author
result.metadata.published_date  # ISO 8601
result.metadata.language

result.structured.schema_org    # List of Schema.org objects
result.structured.open_graph    # OG tag dict
result.structured.tables        # List of table → list of row dicts
result.structured.links.internal
result.structured.links.external
result.structured.links.pagination
result.structured.links.downloads
result.structured.images        # List of ImageItem
result.structured.patterns.emails
result.structured.patterns.phones
result.structured.patterns.prices   # [{"amount": 9.99, "currency": "USD"}]
result.structured.patterns.dates

result.ai_extracted        # Optional dict from AI extractor
result.ai_error            # Error message if AI failed
```

### `crawl(url, ...)`
```python
async for result in crawl("https://example.com", max_pages=100, max_depth=3):
    print(result.url, result.content.word_count)
```

### `map_urls(url)`
```python
urls = await map_urls("https://example.com")  # Uses sitemap.xml + link extraction
```

### `batch_scrape(urls, ...)`
```python
job = await batch_scrape(["https://a.com", "https://b.com"], concurrency=5)
status = await job.get_status()     # JobStatus
results = await job.get_results()   # list[ScrapeResult]
```

---

## REST API

```bash
zerocrawl serve --port 8765
```

```bash
# Scrape
curl -X POST http://localhost:8765/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Batch
curl -X POST http://localhost:8765/batch/scrape \
  -d '{"urls": ["https://a.com", "https://b.com"]}'

# Map
curl -X POST http://localhost:8765/map \
  -d '{"url": "https://example.com"}'

# Health
curl http://localhost:8765/health
```

---

## CLI

```bash
zerocrawl scrape https://example.com
zerocrawl scrape https://example.com --format json --output result.json
zerocrawl scrape https://example.com --mode browser
zerocrawl map https://example.com
zerocrawl crawl https://example.com --max-pages 50 --output ./results/
zerocrawl batch urls.txt --output ./results/ --concurrency 5
zerocrawl serve --port 8765
zerocrawl cache --stats
zerocrawl cache --clear
zerocrawl stats
```

---

## Optional AI Extraction

```python
from zerocrawl import scrape
from zerocrawl.ai.ollama import OllamaExtractor  # Free, local

result = await scrape(
    "https://example.com/product",
    ai_extractor=OllamaExtractor(model="llama3.1:8b"),
    ai_schema={"name": "string", "price": "number", "in_stock": "boolean"}
)
print(result.ai_extracted)
```

Supported providers: `OllamaExtractor` (free), `OpenAIExtractor`, `AnthropicExtractor`, `GeminiExtractor`.

---

## Configuration

Create a `.env` file or set environment variables with `ZEROCRAWL_` prefix:

```env
ZEROCRAWL_BROWSER_POOL_SIZE=1
ZEROCRAWL_DEFAULT_MODE=auto
ZEROCRAWL_DELAY_MEAN_SECONDS=2.0
ZEROCRAWL_REQUESTS_PER_SECOND_PER_DOMAIN=1.0
ZEROCRAWL_OLLAMA_HOST=http://localhost:11434
ZEROCRAWL_LOG_LEVEL=INFO
```

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/unit/ -v            # Unit tests (no network)
pytest tests/integration/ -v     # Integration tests (requires network)
```

---

## Philosophy

1. **Zero cost** — Every dependency is free and open source. No paid proxy services, no paid APIs.
2. **Plug and play** — One function call handles everything underneath.
3. **AI is optional** — Rule-based extraction is complete and useful alone.
4. **Actually works** — Handles JS-rendered pages, Cloudflare-protected sites, dynamic content.

---

## License

MIT License — see [LICENSE](LICENSE).

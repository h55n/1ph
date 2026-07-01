"""
ZeroCrawl — Command Line Interface
All CLI commands: scrape, crawl, map, batch, serve, cache, stats.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.table import Table

app = typer.Typer(
    name="zerocrawl",
    help="🕷️  ZeroCrawl — Zero-cost, plug-and-play web scraping engine.",
    rich_markup_mode="rich",
)
console = Console()


def _run(coro):
    """Run an async coroutine from a sync context."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ──────────────────────────────────────────────────────────────────────────────
# zerocrawl scrape <url>
# ──────────────────────────────────────────────────────────────────────────────
@app.command("scrape")
def scrape_cmd(
    url: str = typer.Argument(..., help="URL to scrape"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format: markdown|json|html|text"),
    mode: str = typer.Option("auto", "--mode", "-m", help="Fetch mode: auto|fast|browser|aggressive"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save result to file"),
    screenshot: bool = typer.Option(False, "--screenshot", "-s", help="Capture screenshot"),
    timeout: int = typer.Option(60, "--timeout", "-t", help="Request timeout in seconds"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache"),
    no_robots: bool = typer.Option(False, "--no-robots", help="Ignore robots.txt"),
    impersonate: str = typer.Option("chrome120", "--impersonate", help="Browser TLS profile"),
):
    """Scrape a single URL and output the result."""
    from zerocrawl.models import ScrapeOptions
    from zerocrawl.engine.orchestrator import get_orchestrator

    options = ScrapeOptions(
        mode=mode,  # type: ignore
        screenshot=screenshot,
        timeout=timeout,
        force_refresh=no_cache,
        respect_robots_txt=not no_robots,
        impersonate=impersonate,  # type: ignore
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]Scraping {url}...", total=None)
        orchestrator = get_orchestrator()
        result = _run(orchestrator.scrape(url, options))
        progress.remove_task(task)

    if result.status == "failed":
        console.print(f"[red]✗ Scrape failed:[/red] {result.error}")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Scraped in {result.timing_ms}ms via [bold]{result.mode}[/bold] mode")

    # Format output
    if format == "markdown":
        content = result.content.markdown
    elif format == "json":
        content = result.to_json()
    elif format == "html":
        content = result.content.html
    elif format == "text":
        content = result.content.text
    else:
        content = result.content.markdown

    if output:
        output.write_text(content, encoding="utf-8")
        console.print(f"[green]Saved to[/green] {output}")
    else:
        if format == "json":
            console.print(Syntax(content, "json", theme="monokai"))
        elif format == "markdown":
            console.print(Panel(content[:3000] + ("..." if len(content) > 3000 else ""),
                                title=result.metadata.title or url, border_style="cyan"))
        else:
            console.print(content)


# ──────────────────────────────────────────────────────────────────────────────
# zerocrawl map <url>
# ──────────────────────────────────────────────────────────────────────────────
@app.command("map")
def map_cmd(
    url: str = typer.Argument(..., help="URL to map"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save URL list to file"),
    no_sitemap: bool = typer.Option(False, "--no-sitemap", help="Skip sitemap.xml"),
):
    """Discover all URLs under a domain without scraping their content."""
    from zerocrawl.crawl.sitemap import fetch_sitemap_urls
    from zerocrawl.engine.orchestrator import get_orchestrator
    from zerocrawl.extraction.links import classify_links
    from zerocrawl.models import ScrapeOptions

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task(f"[cyan]Mapping {url}...", total=None)

        if not no_sitemap:
            urls = _run(fetch_sitemap_urls(url))
        else:
            urls = []

        if not urls:
            result = _run(get_orchestrator().scrape(url, ScrapeOptions(mode="fast")))
            link_data = classify_links(result.content.html, url)
            urls = link_data.get("internal", [])

        progress.remove_task(task)

    urls = list(dict.fromkeys(urls))
    console.print(f"[green]✓[/green] Found [bold]{len(urls)}[/bold] URLs")

    if output:
        output.write_text("\n".join(urls), encoding="utf-8")
        console.print(f"[green]Saved to[/green] {output}")
    else:
        for u in urls[:50]:
            console.print(f"  {u}")
        if len(urls) > 50:
            console.print(f"  [dim]... and {len(urls)-50} more (use --output to save all)[/dim]")


# ──────────────────────────────────────────────────────────────────────────────
# zerocrawl crawl <url>
# ──────────────────────────────────────────────────────────────────────────────
@app.command("crawl")
def crawl_cmd(
    url: str = typer.Argument(..., help="Start URL for crawl"),
    max_pages: int = typer.Option(100, "--max-pages", "-n", help="Maximum pages to scrape"),
    max_depth: int = typer.Option(3, "--max-depth", "-d", help="Maximum link depth"),
    concurrency: int = typer.Option(3, "--concurrency", "-c", help="Parallel workers"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Directory to save results"),
    format: str = typer.Option("json", "--format", "-f", help="Output format per page: json|markdown"),
):
    """Crawl an entire site starting from a URL."""
    from zerocrawl.crawl.crawler import SiteCrawler
    from zerocrawl.models import CrawlOptions

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    options = CrawlOptions(
        start_url=url,
        max_pages=max_pages,
        max_depth=max_depth,
        concurrency=concurrency,
    )

    count = 0
    console.print(f"[cyan]Starting crawl of[/cyan] {url}")

    async def run_crawl():
        nonlocal count
        crawler = SiteCrawler(options)
        async for result in crawler.crawl():
            count += 1
            console.print(f"  [{count}] {result.status:8} {result.mode:10} {result.url[:80]}")
            if output_dir:
                safe_name = result.url.replace("://", "_").replace("/", "_").replace("?", "_")[:100]
                filename = output_dir / f"{count:04d}_{safe_name}.{'json' if format=='json' else 'md'}"
                content = result.to_json() if format == "json" else result.content.markdown
                filename.write_text(content, encoding="utf-8")

    _run(run_crawl())
    console.print(f"\n[green]✓[/green] Crawled [bold]{count}[/bold] pages")


# ──────────────────────────────────────────────────────────────────────────────
# zerocrawl batch <urls_file>
# ──────────────────────────────────────────────────────────────────────────────
@app.command("batch")
def batch_cmd(
    urls_file: Path = typer.Argument(..., help="Text file with one URL per line"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Directory for results"),
    concurrency: int = typer.Option(3, "--concurrency", "-c", help="Parallel workers"),
    timeout: int = typer.Option(60, "--timeout", "-t", help="Per-URL timeout"),
):
    """Scrape multiple URLs from a file in parallel."""
    from zerocrawl.queue.manager import JobManager
    from zerocrawl.queue.worker import AsyncWorker
    from zerocrawl.models import ScrapeOptions

    if not urls_file.exists():
        console.print(f"[red]File not found:[/red] {urls_file}")
        raise typer.Exit(1)

    urls = [u.strip() for u in urls_file.read_text().splitlines() if u.strip() and not u.startswith("#")]
    if not urls:
        console.print("[red]No URLs found in file[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Batch scraping[/cyan] {len(urls)} URLs with concurrency={concurrency}")

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    options = ScrapeOptions(timeout=timeout)

    async def run_batch():
        job = await JobManager.create_batch_job(urls)
        worker = AsyncWorker(job.id, options=options, concurrency=concurrency)

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      TimeElapsedColumn(), console=console) as progress:
            task = progress.add_task(f"Processing {len(urls)} URLs...", total=len(urls))
            worker_task = asyncio.create_task(worker.run())

            while not worker_task.done():
                await asyncio.sleep(1)
                status = await JobManager.get_status(job.id)
                progress.update(task, completed=status.completed + status.failed,
                                description=f"✓ {status.completed} done, ✗ {status.failed} failed")

            await worker_task

        results = await JobManager.get_results(job.id)
        if output_dir:
            for i, r in enumerate(results):
                fname = output_dir / f"{i+1:04d}_result.json"
                fname.write_text(r.to_json(), encoding="utf-8")
        return results

    results = _run(run_batch())
    success = sum(1 for r in results if r.status != "failed")
    console.print(f"[green]✓[/green] Done — {success}/{len(urls)} succeeded")


# ──────────────────────────────────────────────────────────────────────────────
# zerocrawl serve
# ──────────────────────────────────────────────────────────────────────────────
@app.command("serve")
def serve_cmd(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host"),
    port: int = typer.Option(8765, "--port", "-p", help="Bind port"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on code change (dev)"),
):
    """Start the local REST API server."""
    import uvicorn
    from zerocrawl.api.server import create_app

    console.print(f"[green]🕷️  ZeroCrawl API[/green] starting at [bold]http://{host}:{port}[/bold]")
    console.print(f"  Docs: http://{host}:{port}/docs")

    uvicorn.run(
        "zerocrawl.api.server:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


# ──────────────────────────────────────────────────────────────────────────────
# zerocrawl cache
# ──────────────────────────────────────────────────────────────────────────────
@app.command("cache")
def cache_cmd(
    stats: bool = typer.Option(False, "--stats", help="Show cache statistics"),
    clear: bool = typer.Option(False, "--clear", help="Clear all cached results"),
    url: Optional[str] = typer.Option(None, "--url", help="Clear cache for specific URL"),
):
    """Manage the result cache."""
    from zerocrawl.queue.cache import clear_cache
    from zerocrawl.queue.db import DB, init_db

    if clear or url:
        count = _run(clear_cache(url=url))
        if url:
            console.print(f"[green]Cleared cache for[/green] {url}")
        else:
            console.print(f"[green]Cleared[/green] {count} cache entries")
    elif stats:
        async def get_stats():
            await init_db()
            async with DB() as db:
                row = await db.fetchone("SELECT COUNT(*) as c, SUM(ttl_seconds) as total_ttl FROM cache")
                return row
        row = _run(get_stats())
        table = Table(title="Cache Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Cached URLs", str(row["c"] if row else 0))
        console.print(table)
    else:
        console.print("Use --stats or --clear. Run [bold]zerocrawl cache --help[/bold] for options.")


# ──────────────────────────────────────────────────────────────────────────────
# zerocrawl stats
# ──────────────────────────────────────────────────────────────────────────────
@app.command("stats")
def stats_cmd():
    """Show scraper statistics."""
    from zerocrawl.queue.db import DB, init_db, get_db_path

    async def get_all_stats():
        await init_db()
        async with DB() as db:
            jobs = await db.fetchone("SELECT COUNT(*) as c FROM jobs")
            reqs = await db.fetchone("SELECT COUNT(*) as c, SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) as done, SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed FROM requests")
            cache = await db.fetchone("SELECT COUNT(*) as c FROM cache")
        return jobs, reqs, cache

    jobs, reqs, cache = _run(get_all_stats())

    table = Table(title="🕷️  ZeroCrawl Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Total jobs", str(jobs["c"] if jobs else 0))
    table.add_row("Total requests", str(reqs["c"] if reqs else 0))
    table.add_row("Succeeded", str(reqs["done"] if reqs else 0))
    table.add_row("Failed", str(reqs["failed"] if reqs else 0))
    table.add_row("Cache entries", str(cache["c"] if cache else 0))
    table.add_row("DB path", str(get_db_path()))
    console.print(table)


if __name__ == "__main__":
    app()

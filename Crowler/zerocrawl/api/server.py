"""ZeroCrawl FastAPI server."""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import scrape, batch, crawl, map as map_route, stats

def create_app() -> FastAPI:
    app = FastAPI(title="ZeroCrawl API", description="Zero-cost web scraping engine", version="1.0.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(scrape.router)
    app.include_router(batch.router)
    app.include_router(crawl.router)
    app.include_router(map_route.router)
    app.include_router(stats.router)
    return app

from fastapi import APIRouter, HTTPException
from loguru import logger
from ...api.schemas import ScrapeRequest
from ...engine.orchestrator import get_orchestrator
from ...models import ScrapeOptions
from ...queue.cache import get_cached, set_cached

router = APIRouter(tags=["scrape"])

@router.post("/scrape")
async def scrape_endpoint(req: ScrapeRequest):
    try:
        options = ScrapeOptions(
            mode=req.options.mode, screenshot=req.options.screenshot,
            wait_for_selector=req.options.wait_for_selector, timeout=req.options.timeout,
            cache_ttl=req.options.cache_ttl, force_refresh=req.options.force_refresh,
            proxy=req.options.proxy, cookies=req.options.cookies,
            extra_headers=req.options.extra_headers,
            respect_robots_txt=req.options.respect_robots_txt,
            impersonate=req.options.impersonate,
        )
        if not req.options.force_refresh:
            cached = await get_cached(req.url, req.options.cache_ttl)
            if cached:
                return cached.model_dump(mode="json")
        orchestrator = get_orchestrator()
        result = await orchestrator.scrape(req.url, options)
        if result.status != "failed":
            await set_cached(req.url, result, req.options.cache_ttl)
        if req.ai and req.ai.schema_:
            try:
                extractor = _build_extractor(req.ai)
                result.ai_extracted = await extractor.extract(result.content.markdown, req.ai.schema_)
            except Exception as e:
                result.ai_error = str(e)
        return result.model_dump(mode="json")
    except Exception as e:
        logger.error(f"Scrape error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _build_extractor(ai_req):
    from ...ai.ollama import OllamaExtractor, OpenAIExtractor, AnthropicExtractor, GeminiExtractor
    from ...config import settings
    if ai_req.provider == "ollama":
        return OllamaExtractor(model=ai_req.model or "llama3.1:8b")
    elif ai_req.provider == "openai":
        return OpenAIExtractor(api_key=settings.openai_api_key or "", model=ai_req.model or "gpt-4o-mini")
    elif ai_req.provider == "anthropic":
        return AnthropicExtractor(api_key=settings.anthropic_api_key or "", model=ai_req.model or "claude-haiku-4-5")
    return OllamaExtractor()

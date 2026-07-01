"""OllamaExtractor — local LLM, zero cost."""
from __future__ import annotations
import json
import re
from typing import Any
from loguru import logger
from .base import AIExtractor
from .prompts import get_prompt, detect_template

class OllamaExtractor(AIExtractor):
    def __init__(self, model: str = "llama3.1:8b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    async def extract(self, content: str, schema: dict[str, Any], context: str = "") -> dict[str, Any]:
        template = detect_template(schema)
        prompt = get_prompt(template, content, schema)
        try:
            import ollama
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.generate(model=self.model, prompt=prompt, options={"temperature": 0.1})
            )
            raw = response.get("response", "")
            return _parse_json_response(raw)
        except Exception as e:
            logger.error(f"Ollama extraction failed: {e}")
            raise

class OpenAIExtractor(AIExtractor):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def extract(self, content: str, schema: dict[str, Any], context: str = "") -> dict[str, Any]:
        template = detect_template(schema)
        prompt = get_prompt(template, content, schema)
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or ""
            return _parse_json_response(raw)
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")
            raise

class AnthropicExtractor(AIExtractor):
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5"):
        self.api_key = api_key
        self.model = model

    async def extract(self, content: str, schema: dict[str, Any], context: str = "") -> dict[str, Any]:
        template = detect_template(schema)
        prompt = get_prompt(template, content, schema)
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            message = await client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text if message.content else ""
            return _parse_json_response(raw)
        except Exception as e:
            logger.error(f"Anthropic extraction failed: {e}")
            raise

class GeminiExtractor(AIExtractor):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model

    async def extract(self, content: str, schema: dict[str, Any], context: str = "") -> dict[str, Any]:
        template = detect_template(schema)
        prompt = get_prompt(template, content, schema)
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model_obj = genai.GenerativeModel(self.model)
            import asyncio
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: model_obj.generate_content(prompt)
            )
            raw = response.text or ""
            return _parse_json_response(raw)
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            raise

def _parse_json_response(raw: str) -> dict:
    """Parse JSON from LLM response, stripping markdown fences."""
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
    try:
        obj = json.loads(cleaned)
        return obj if isinstance(obj, dict) else {"result": obj}
    except json.JSONDecodeError:
        # Try to find JSON object in the response
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"raw_response": raw[:500]}

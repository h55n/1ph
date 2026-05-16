import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "").strip().strip('"').strip("'")

def test_jina_enrichment(url):
    print(f"Testing URL: {url}")
    # 1. Fetch via Jina
    print("Fetching via r.jina.ai...")
    with httpx.Client(timeout=60) as client:
        r = client.get(f"https://r.jina.ai/{url}")
        page_text = r.text
        print(f"Fetched {len(page_text)} chars from Jina.")
        
    if len(page_text) < 100:
        print("Failed to fetch.")
        return

    # 2. Extract via Mistral
    print("Calling Mistral...")
    system_prompt = """Extract hackathon data as JSON. Schema:
{
  "long_description": "Comprehensive description including problem statement.",
  "prize_pool": number or null,
  "prize_currency": "USD" or "INR" or null,
  "city": "string or null",
  "theme_tags": ["tag1", "tag2"]
}"""
    
    user_prompt = f"URL: {url}\n\nContent:\n{page_text[:12000]}"
    
    with httpx.Client(timeout=60) as client:
        r = client.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
            json={
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
        )
        print(r.json()["choices"][0]["message"]["content"])

if __name__ == "__main__":
    # Test a Devfolio SPA URL
    test_jina_enrichment("https://ethglobal.com/events/brussels")

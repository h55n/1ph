#!/usr/bin/env python3
"""Start ZeroCrawl as a local REST API server."""
import subprocess, sys

print("Starting ZeroCrawl API server at http://127.0.0.1:8765")
print("API docs: http://127.0.0.1:8765/docs")
print("Press Ctrl+C to stop.")
print()
print("Example request:")
print("""  curl -X POST http://127.0.0.1:8765/scrape \
    -H "Content-Type: application/json" \
    -d '{"url": "https://example.com"}\'""")
print()

subprocess.run([sys.executable, "-m", "uvicorn", "zerocrawl.api.server:create_app",
                "--factory", "--host", "127.0.0.1", "--port", "8765"])

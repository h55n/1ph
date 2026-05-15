import sys
import os

# Allow running as `python test_luma_scraper.py` from repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.connectors.luma import LumaConnector

def test():
    print("Starting Luma test...")
    connector = LumaConnector()
    result = connector.fetch()
    
    print(f"\nStatus: {result.status}")
    print(f"Error: {result.error}")
    print(f"Total records found: {len(result.records)}")
    
    for i, record in enumerate(result.records[:5]):
        print(f"\n--- Record {i+1} ---")
        print(f"Title: {record.title}")
        print(f"Apply URL: {record.apply_url}")
        print(f"Mode: {record.mode}")
        print(f"Description: {record.description[:100]}...")

if __name__ == "__main__":
    test()

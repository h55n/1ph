import urllib.request
import json
import os

from dotenv import load_dotenv
load_dotenv('apps/web/.env.local')
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

req = urllib.request.Request(f"{url}/rest/v1/Hackathon?select=id", headers={"apikey": key, "Authorization": f"Bearer {key}"})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        print(f"Hackathons count: {len(data)}")
except Exception as e:
    import traceback
    traceback.print_exc()

req2 = urllib.request.Request(f"{url}/rest/v1/PipelineRun?select=*", headers={"apikey": key, "Authorization": f"Bearer {key}", "Range": "0-2"})
try:
    with urllib.request.urlopen(req2) as response:
        data = json.loads(response.read())
        print(f"PipelineRuns count: {len(data)}")
        for i, run in enumerate(data[:2]):
            print(f"Run {i}: {run}")
except Exception as e:
    import traceback
    traceback.print_exc()

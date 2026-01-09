import os
from supabase import create_client, Client

from dotenv import load_dotenv
from pathlib import Path

# Load .env from the backend directory (where this file is)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

try:
    if not url or not key:
        print("Warning: SUPABASE_URL or SUPABASE_KEY not set. Database features will fail.")
        supabase = None
    else:
        supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Failed to initialize Supabase: {e}")
    supabase = None

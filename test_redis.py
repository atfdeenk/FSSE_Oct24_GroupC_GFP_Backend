import os
import redis
from dotenv import load_dotenv

load_dotenv()  # Load .env

url = os.getenv("REDIS_URL")
print("Connecting to:", url)

try:
    r = redis.from_url(url)
    r.ping()
    print("✅ Redis connection successful")
except Exception as e:
    print("❌ Redis connection failed:", e)

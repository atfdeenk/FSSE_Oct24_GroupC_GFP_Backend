import os
from dotenv import load_dotenv
import redis

load_dotenv()

url = os.getenv("REDIS_URL")
print(f"Connecting to: {url}")

try:
    r = redis.Redis.from_url(url)  # No ssl=True needed; 'rediss://' infers it
    r.ping()
    print("✅ Redis connected successfully")
except Exception as e:
    print("❌ Redis connection failed:", e)

import redis
import os
from dotenv import load_dotenv

# Replace with your Upstash Redis URL
UPSTASH_URL = os.getenv("UPSTASH_URI")

load_dotenv()

redis_client = redis.Redis.from_url(UPSTASH_URL, decode_responses=True)
redis_client.ping()

import redis
import os
from dotenv import load_dotenv

# Replace with your Upstash Redis URL
UPSTASH_URI = os.getenv("UPSTASH_URI")

load_dotenv()

redis_client = redis.Redis.from_url(UPSTASH_URI, decode_responses=True)
redis_client.ping()

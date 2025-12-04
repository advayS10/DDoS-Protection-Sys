import redis
import os
from dotenv import load_dotenv

# Replace with your Upstash Redis URL
UPSTASH_URI = os.getenv("UPSTASH_URI")

load_dotenv()

redis_client = redis.Redis.from_url("rediss://default:AUMJAAIncDIyNjc1ZmY4ZmE0MzA0MjJmODEyOGJlMTJjNGI3NzgzMXAyMTcxNjE@giving-yeti-17161.upstash.io:6379", decode_responses=True)
redis_client.ping()

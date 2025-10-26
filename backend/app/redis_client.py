import redis
import os
from dotenv import load_dotenv

# Replace with your Upstash Redis URL
UPSTASH_URI = os.getenv("UPSTASH_URI")

load_dotenv()

redis_client = redis.Redis.from_url("rediss://default:ARdJAAImcDIzZjBjN2I4NWY1Njc0NWI0YjIzMzgwODRlYjZkYzBhMnAyNTk2MQ@funny-pup-5961.upstash.io:6379", decode_responses=True)
redis_client.ping()

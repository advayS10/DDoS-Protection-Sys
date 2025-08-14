import redis

# Replace with your Upstash Redis URL
UPSTASH_URL = "rediss://default:AShBAAIncDE5MzQ5ZGJhODI4ZjY0ZGY5YjljNDYzZDA5MmNlMWY1MHAxMTAzMDU@trusting-koi-10305.upstash.io:6379"

redis_client = redis.Redis.from_url(UPSTASH_URL, decode_responses=True)

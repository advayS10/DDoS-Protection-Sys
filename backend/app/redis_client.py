import redis

# Replace with your Upstash Redis URL
UPSTASH_URL = "rediss://default:ARaIAAImcDJkMjE1NTllYjFkODE0N2I3OWI4ZDQ4NmE5ODRmY2U1MXAyNTc2OA@dominant-tuna-5768.upstash.io:6379"

redis_client = redis.Redis.from_url(UPSTASH_URL, decode_responses=True)
redis_client.ping()
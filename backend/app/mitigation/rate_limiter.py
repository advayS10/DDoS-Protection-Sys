import redis
from datetime import timedelta
from .gcra_redis import request_is_limited  # the modified GCRA function

# Connect to Redis (adjust host/port/password as needed)
r = redis.Redis()

# Default GCRA settings
LIMIT = 55          # max requests
PERIOD = timedelta(seconds=60)  # per 60 seconds

def is_rate_limited(ip: str) -> bool:
    """
    Returns True if this IP is over the allowed rate.
    """
    key = f"rate:{ip}"
    return request_is_limited(r, key, LIMIT, PERIOD)

def register_request(ip: str):
    """
    Optional: can be left empty because GCRA Lua already registers each request.
    """
    pass

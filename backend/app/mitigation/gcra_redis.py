from datetime import timedelta
import redis

'''
This is GCRA rate limiting.
Each key tracks the next allowed time.
We used Redis Lua to make it atomic for high traffic.
'''

# Lua script for atomic GCRA
GCRA_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
local period = tonumber(ARGV[3])

local separation = math.floor(period / limit)

-- Get current TAT
local tat = tonumber(redis.call("GET", key) or now)
tat = math.max(tat, now)

-- Check if request is allowed
if tat - now <= period - separation then
    local new_tat = tat + separation
    redis.call("SET", key, new_tat)
    return 0  -- allowed
else
    return 1  -- limited
end
"""

'''
Some Error here - 24/9/2025. Time - 8:42
'''

def request_is_limited(r: redis.Redis, key: str, limit: int, period: timedelta):
    now = r.time()[0]
    period_in_seconds = int(period.total_seconds())
    result = r.eval(GCRA_LUA, 1, key, now, limit, period_in_seconds)
    return result == 1  # True if request is limited



# Version - 1
# def request_is_limited(r: redis.Redis, key: str, limit: int, period: timedelta):
#     if r.setnx(key, limit):
#         r.expire(key, int(period.total_seconds()))
    
#     bucket_val = r.get(key)
#     if bucket_val and int(bucket_val) > 0:
#         r.decrby(key, 1)
#         return False
    
#     return True

# Version - 2
# def request_is_limited(r: redis.Redis, key: str, limit: int, period: timedelta):
#     period_in_seconds = int(period.total_seconds())
#     t = r.time()[0]
#     separation = round(period_in_seconds / limit)
#     r.setnx(key, 0)
#     tat = max(int(r.get(key)), t)
#     if tat - t <= period_in_seconds - separation:
#         new_tat = max(tat, t) + separation
#         r.set(key, new_tat)
#         return False
#     return True

# Version - 3
# def request_is_limited(r: redis.Redis, key: str, limit: int, period: timedelta):
#     period_in_seconds = int(period.total_seconds())
#     t = r.time()[0]
#     separation = round(period_in_seconds / limit)
#     r.setnx(key, 0)
#     try:
#         with r.lock('lock:' + key, blocking_timeout=5) as lock:
#             tat = max(int(r.get(key)), t)
#             if tat - t <= period_in_seconds - separation:
#                 new_tat = max(tat, t) + separation
#                 r.set(key, new_tat)
#                 return False
#             return True
#     except LockError:
#         return True
    

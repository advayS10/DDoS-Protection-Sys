from datetime import timedelta
from app.mitigation import rate_limiter
from app.redis_client import redis_client as r

# requests = 25

# for i in range(requests):
#     if rate_limiter.request_is_limited(r, 'admin', 20, timedelta(seconds=30)):
#         print ('🛑 Request is limited')
#     else:
#         print ('✅ Request is allowed')

import app
from app.mitigation.traffic_filter import is_blocked

with app.app_context():
    ip = "192.168.1.100"
    print(is_blocked(ip))
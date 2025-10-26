'''
Tracks request in redis
'''

import time
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from redis_client import redis_client

class RequestTracker():

    def track_request(self, ip: str, packet_size: int):

        now = time.time()

        # save timestamp
        redis_client.lpush(f"track_time:{ip}", now)
        redis_client.ltrim(f"track_time:{ip}", 0, 99)
        redis_client.expire(f"track_time:{ip}", 600)

        # save size
        redis_client.lpush(f"track_size:{ip}", packet_size)
        redis_client.ltrim(f"track_size:{ip}", 0, 99)
        redis_client.expire(f"track_size:{ip}", 600)

    def get_recent_sizes(self, ip: str):

        sizes = redis_client.lrange(f"track_size:{ip}", 0, -1)
        if not sizes:
            return []
        
        return [float(s) for s in sizes]
    
    def get_request_count(self, ip: str, window: int):

        timestamps = redis_client.lrange(f"track_time:{ip}", 0, -1)
        if not timestamps:
            return 0
        
        now = time.time()
        count = 0
        for ts in timestamps:
            if (now - float(ts)) <= window:
                count += 1
        return count


# Testing
if __name__ == "__main__":
    tracker = RequestTracker()
    test_ip = "1.2.3.4"
    
    print("Tracking 5 requests...")
    for i in range(5):
        tracker.track_request(test_ip, 500 + i*10)
        time.sleep(0.1)
    
    count = tracker.get_request_count(test_ip, 60)
    sizes = tracker.get_recent_sizes(test_ip)
    
    print(f"Count in last 60s: {count}")
    print(f"Sizes tracked: {len(sizes)}")
    
    if count == 5 and len(sizes) == 5:
        print("✅ Tracking works!")
    else:
        print("❌ Something wrong")
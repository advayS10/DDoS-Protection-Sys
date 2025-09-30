
from .traffic_filter import is_blocked


ip = "127.0.0.1"

# Use app context for SQLAlchemy session


    # Check if IP is blocked initially
print(f"Initially blocked? {is_blocked(ip)}")

    # Block IP temporarily for 10 minutes
    # block_ip(ip, unblock_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=10))
    # print(f"Blocked after adding? {is_blocked(ip)}")

    # # Unblock IP
    # unblock_ip(ip)
    # print(f"Blocked after removal? {is_blocked(ip)}")
from flask import request
from datetime import datetime
from ..models.suspicious_ip import SuspiciousIP
from .. import db
from ..redis_client import redis_client


def detect_ddos(threshold=100, window_seconds=60):

    # Check if given IP has sent more than `threshold` requests in last `window_seconds` seconds.
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if SuspiciousIP.query.filter_by(ip_address=ip).first():
        return

    count = redis_client.incr(ip)

    if count == 1:
        redis_client.expire(ip, window_seconds)

    if count > threshold:
        already_flagged = SuspiciousIP.query.filter_by(ip_address=ip).first()
        if not already_flagged:
            suspicious = SuspiciousIP(
                ip_address = ip,
                reason = f"{count} requests in {window_seconds} seconds"
                detected_at = datetime.now()
            )
            db.session.add(suspicious)
            db.session.commit()

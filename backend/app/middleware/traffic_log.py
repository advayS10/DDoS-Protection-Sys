from flask import request
from ..models.traffic_log import TrafficLog
from .. import db

def log_request():
    try:
        ip = request.remote_addr
        method = request.method
        endpoint = request.path
        
        # Create log entry matching your schema
        log = TrafficLog(
            ip_address=ip,  # Changed to ip_address
            method=method,
            endpoint=endpoint  # endpoint is correct
        )
        
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log request: {e}")
        db.session.rollback()
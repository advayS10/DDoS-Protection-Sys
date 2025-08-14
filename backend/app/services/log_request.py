from ..models.traffic_log import TrafficLog

def get_latest_logs(limit=100):
    logs = TrafficLog.query.order_by(TrafficLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "ip": log.ip_address,
            "method": log.method,
            "endpoint": log.endpoint,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for log in logs
    ]
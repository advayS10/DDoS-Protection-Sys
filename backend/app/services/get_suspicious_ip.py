from ..models.suspicious_ip import SuspiciousIP

def get_suspicious_ips():
    ips = SuspiciousIP.query.order_by(SuspiciousIP.timestamp.desc()).all()
    return [
        {
            "ip": ip.ip_address,
            "reason": ip.reason,
            "timestamp": ip.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for ip in ips
    ]
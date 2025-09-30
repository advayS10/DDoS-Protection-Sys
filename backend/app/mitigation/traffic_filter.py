import datetime
from .. import db
from ..models.suspicious_ip import SuspiciousIP

def is_blocked(ip: str) -> bool:
    """Check if IP is actually blocked (not just suspicious)"""
    blocked = db.session.query(SuspiciousIP).filter(
        SuspiciousIP.ip_address == ip,
        SuspiciousIP.status == 'blocked'
    ).first()
    return blocked is not None

def is_suspicious(ip: str) -> bool:
    """Check if IP is marked as suspicious"""
    suspicious = db.session.query(SuspiciousIP).filter(
        SuspiciousIP.ip_address == ip,
        SuspiciousIP.status.in_(['suspicious', 'blocked'])
    ).first()
    return suspicious is not None

def block_ip(ip: str, reason: str = "Blocked due to failed challenge"):
    """Actually block an IP by setting status to 'blocked'"""
    existing = SuspiciousIP.query.filter_by(ip_address=ip).first()
    if existing:
        existing.status = 'blocked'
        existing.blocked_at = datetime.datetime.now()
        existing.reason = reason
    else:
        blocked = SuspiciousIP(
            ip_address=ip,
            reason=reason,
            detected_at=datetime.datetime.now(),
            status='blocked',
            blocked_at=datetime.datetime.now()
        )
        db.session.add(blocked)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error blocking IP {ip}: {e}")

def mark_suspicious(ip: str, reason: str = "Detected suspicious activity"):
    """Mark IP as suspicious (not blocked yet)"""
    existing = SuspiciousIP.query.filter_by(ip_address=ip).first()
    if not existing:
        suspicious = SuspiciousIP(
            ip_address=ip,
            reason=reason,
            detected_at=datetime.datetime.now(),
            status='suspicious'
        )
        db.session.add(suspicious)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error marking IP {ip} as suspicious: {e}")

def unblock_ip(ip: str) -> bool:
    """Remove an IP from blocklist or mark as verified"""
    blocked = SuspiciousIP.query.filter_by(ip_address=ip).first()
    if blocked:
        try:
            blocked.status = 'verified'
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error unblocking IP {ip}: {e}")
            return False
    return False
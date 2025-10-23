from flask import Blueprint, jsonify, request
from ..models.traffic_log import TrafficLog
from ..models.suspicious_ip import SuspiciousIP
from .. import db
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

# 1. MAIN STATS - Most important endpoint
@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overview statistics"""
    try:
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        today_start = now.replace(hour=0, minute=0, second=0)
        
        # Quick counts
        total_requests = TrafficLog.query.count()
        total_today = TrafficLog.query.filter(TrafficLog.timestamp >= today_start).count()
        total_hour = TrafficLog.query.filter(TrafficLog.timestamp >= hour_ago).count()
        
        # Count by status
        suspicious_count = SuspiciousIP.query.filter_by(status='suspicious').count()
        blocked_count = SuspiciousIP.query.filter_by(status='blocked').count()
        verified_count = SuspiciousIP.query.filter_by(status='verified').count()
        
        return jsonify({
            'total_requests': total_requests,
            'requests_today': total_today,
            'requests_hour': total_hour,
            'suspicious_ips': suspicious_count,
            'blocked_ips': blocked_count,
            'verified_ips': verified_count,
            'requests_per_second': round(total_hour / 3600, 2) if total_hour > 0 else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 2. TRAFFIC CHART DATA
@dashboard_bp.route('/traffic-chart', methods=['GET'])
def get_traffic_chart():
    """Get last 24 hours of traffic for chart"""
    try:
        now = datetime.utcnow()
        day_ago = now - timedelta(hours=24)
        
        # Get hourly traffic - PostgreSQL version
        traffic = db.session.query(
            func.to_char(TrafficLog.timestamp, 'HH24:00').label('hour'),
            func.count(TrafficLog.id).label('count')
        ).filter(
            TrafficLog.timestamp >= day_ago
        ).group_by('hour').order_by('hour').all()
        
        return jsonify([{
            'time': t.hour,
            'requests': t.count
        } for t in traffic])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 3. SUSPICIOUS IPs LIST
@dashboard_bp.route('/suspicious-ips', methods=['GET'])
def get_suspicious_ips():
    """Get list of suspicious IPs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        suspicious = SuspiciousIP.query.filter_by(
            status='suspicious'
        ).order_by(
            SuspiciousIP.detected_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [{
                'id': ip.id,
                'ip': ip.ip_address,
                'reason': ip.reason,
                'detected_at': ip.detected_at.isoformat(),
                'status': ip.status
            } for ip in suspicious.items],
            'total': suspicious.total,
            'pages': suspicious.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 4. BLOCKED IPs LIST
@dashboard_bp.route('/blocked-ips', methods=['GET'])
def get_blocked_ips():
    """Get list of blocked IPs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        blocked = SuspiciousIP.query.filter_by(
            status='blocked'
        ).order_by(
            SuspiciousIP.blocked_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [{
                'id': ip.id,
                'ip': ip.ip_address,
                'reason': ip.reason,
                'blocked_at': ip.blocked_at.isoformat() if ip.blocked_at else ip.detected_at.isoformat(),
                'status': ip.status
            } for ip in blocked.items],
            'total': blocked.total,
            'pages': blocked.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 5. VERIFIED IPs LIST
@dashboard_bp.route('/verified-ips', methods=['GET'])
def get_verified_ips():
    """Get list of verified IPs (passed challenge)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        verified = SuspiciousIP.query.filter_by(
            status='verified'
        ).order_by(
            SuspiciousIP.detected_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [{
                'id': ip.id,
                'ip': ip.ip_address,
                'reason': ip.reason,
                'verified_at': ip.detected_at.isoformat(),
                'status': ip.status
            } for ip in verified.items],
            'total': verified.total,
            'pages': verified.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 6. RECENT ACTIVITY
@dashboard_bp.route('/recent-activity', methods=['GET'])
def get_recent_activity():
    """Get recent attacks/suspicious activity"""
    try:
        recent = SuspiciousIP.query.order_by(
            SuspiciousIP.detected_at.desc()
        ).limit(10).all()
        
        return jsonify([{
            'ip': ip.ip_address,
            'reason': ip.reason,
            'time': ip.detected_at.isoformat(),
            'status': ip.status
        } for ip in recent])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 7. BLOCK IP ACTION
@dashboard_bp.route('/block-ip/<ip_address>', methods=['POST'])
def block_ip(ip_address):
    """Block an IP address"""
    try:
        suspicious_ip = SuspiciousIP.query.filter_by(ip_address=ip_address).first()
        if suspicious_ip:
            suspicious_ip.status = 'blocked'
            suspicious_ip.blocked_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'message': f'IP {ip_address} blocked'})
        else:
            # Create new entry if doesn't exist
            new_ip = SuspiciousIP(
                ip_address=ip_address,
                reason='Manually blocked from dashboard',
                status='blocked',
                blocked_at=datetime.utcnow()
            )
            db.session.add(new_ip)
            db.session.commit()
            return jsonify({'success': True, 'message': f'IP {ip_address} blocked'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 8. UNBLOCK IP ACTION
@dashboard_bp.route('/unblock-ip/<ip_address>', methods=['POST'])
def unblock_ip(ip_address):
    """Unblock an IP address (set to suspicious)"""
    try:
        suspicious_ip = SuspiciousIP.query.filter_by(ip_address=ip_address).first()
        if suspicious_ip:
            suspicious_ip.status = 'suspicious'
            suspicious_ip.blocked_at = None
            db.session.commit()
            return jsonify({'success': True, 'message': f'IP {ip_address} unblocked'})
        else:
            return jsonify({'success': False, 'message': 'IP not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 9. DELETE IP FROM LIST
@dashboard_bp.route('/delete-ip/<ip_address>', methods=['DELETE'])
def delete_ip(ip_address):
    """Remove IP from suspicious list (mark as verified/safe)"""
    try:
        suspicious_ip = SuspiciousIP.query.filter_by(ip_address=ip_address).first()
        if suspicious_ip:
            # Option 1: Delete completely
            # db.session.delete(suspicious_ip)
            
            # Option 2: Mark as verified (better for tracking)
            suspicious_ip.status = 'verified'
            db.session.commit()
            return jsonify({'success': True, 'message': f'IP {ip_address} marked as safe'})
        else:
            return jsonify({'success': False, 'message': 'IP not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 10. GET ALL IPS (with filter)
@dashboard_bp.route('/all-ips', methods=['GET'])
def get_all_ips():
    """Get all IPs with optional status filter"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        status_filter = request.args.get('status', None)  # suspicious, blocked, verified
        
        query = SuspiciousIP.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        ips = query.order_by(
            SuspiciousIP.detected_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [{
                'id': ip.id,
                'ip': ip.ip_address,
                'reason': ip.reason,
                'detected_at': ip.detected_at.isoformat(),
                'blocked_at': ip.blocked_at.isoformat() if ip.blocked_at else None,
                'status': ip.status
            } for ip in ips.items],
            'total': ips.total,
            'pages': ips.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# 11. GET RECENT LOGS
@dashboard_bp.route('/recent-logs', methods=['GET'])
def get_recent_logs():
    """Get recent traffic logs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        logs = TrafficLog.query.order_by(
            TrafficLog.timestamp.desc()
        ).limit(limit).all()
        
        return jsonify([{
            'id': log.id,
            'ip': log.ip_address,
            'method': log.method,
            'endpoint': log.endpoint,
            'timestamp': log.timestamp.isoformat()
        } for log in logs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
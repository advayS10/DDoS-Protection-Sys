from flask import request, abort
from datetime import datetime, timedelta
from collections import defaultdict
import json
import hashlib
import time
import math
from typing import Dict, List, Tuple, Optional
from ..models.suspicious_ip import SuspiciousIP
from .. import db
from ..redis_client import redis_client


class DDoSDetector:
    # easy
    def __init__(self):
        self.algorithms = {
            'rate_limiting': self.rate_limiting_detection,
            'burst_detection': self.burst_detection,
            'behavior_analysis': self.behavior_analysis,
            'entropy_analysis': self.entropy_analysis,
            'progressive_detection': self.progressive_detection,
            'geographic_analysis': self.geographic_analysis,
            'http_flood_detection': self.http_flood_detection
        }
    # easy
    def get_client_ip(self) -> str:
        """Extract real client IP handling various proxy configurations"""
        proxy_headers = [
            'X-Forwarded-For',
            'X-Real-IP', 
            'X-Client-IP',
            'CF-Connecting-IP',  # Cloudflare
            'HTTP_X_FORWARDED_FOR',
            'HTTP_CLIENT_IP'
        ]
        
        for header in proxy_headers:
            ip = request.headers.get(header)
            if ip:
                return ip.split(',')[0].strip()
        
        return request.remote_addr or 'unknown'
    
    # most advance
    def detect_threats(self, config: Dict = None) -> Dict:
        """Main detection function that runs all algorithms"""
        if config is None:
            config = {
                'rate_limiting': {'threshold': 100, 'window': 60},
                'burst_detection': {'threshold': 20, 'window': 10},
                'behavior_analysis': {'min_requests': 10},
                'entropy_analysis': {'min_entropy': 2.0},
                'progressive_detection': {'enabled': True},
                'geographic_analysis': {'enabled': False},  # Disabled by default
                'http_flood_detection': {'threshold': 50, 'window': 30}
            }
        
        results = {}
        ip = self.get_client_ip()
        
        # Skip if already flagged as suspicious
        if self.is_already_flagged(ip):
            return {'ip': ip, 'blocked': True, 'reason': 'Already flagged', 'results': {}}
        
        # Run all detection algorithms
        for algo_name, algo_func in self.algorithms.items():
            if config.get(algo_name, {}).get('enabled', True):
                try:
                    result = algo_func(ip, config.get(algo_name, {}))
                    results[algo_name] = result
                    
                    # If any algorithm detects threat, flag the IP
                    if result.get('is_threat', False):
                        self.flag_suspicious_ip(ip, result['reason'], algo_name)
                        return {'ip': ip, 'blocked': True, 'reason': result['reason'], 'algorithm': algo_name, 'results': results}
                        
                except Exception as e:
                    results[algo_name] = {'error': str(e)}
        
        return {'ip': ip, 'blocked': False, 'results': results}
    
    # moderate
    def rate_limiting_detection(self, ip: str, config: Dict) -> Dict:
        """Basic rate limiting - requests per time window"""
        threshold = config.get('threshold', 100)
        window = config.get('window', 60)
        
        key = f"rate_limit:{ip}"
        count = redis_client.incr(key)
        
        if count == 1:
            redis_client.expire(key, window)
        
        is_threat = count > threshold
        return {
            'is_threat': is_threat,
            'count': count,
            'threshold': threshold,
            'reason': f"Rate limit exceeded: {count}/{threshold} requests in {window}s"
        }
    
    # moderate
    def burst_detection(self, ip: str, config: Dict) -> Dict:
        """Detect sudden bursts of traffic"""
        threshold = config.get('threshold', 20)
        window = config.get('window', 10)
        
        key = f"burst:{ip}"
        pipe = redis_client.pipeline()
        
        now = time.time()
        pipe.zadd(key, {str(now): now})
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zcard(key)
        pipe.expire(key, window * 2)
        
        results = pipe.execute()
        count = results[2]
        
        is_threat = count > threshold
        return {
            'is_threat': is_threat,
            'count': count,
            'threshold': threshold,
            'reason': f"Burst detected: {count} requests in {window}s window"
        }
    
    # advance
    def behavior_analysis(self, ip: str, config: Dict) -> Dict:
        """Analyze request patterns and behavior"""
        min_requests = config.get('min_requests', 10)
        
        metadata = {
            'timestamp': time.time(),
            'user_agent': request.headers.get('User-Agent', ''),
            'referer': request.headers.get('Referer', ''),
            'path': request.path,
            'method': request.method,
            'content_length': request.content_length or 0
        }
        
        key = f"behavior:{ip}"
        pipe = redis_client.pipeline()
        pipe.lpush(key, json.dumps(metadata))
        pipe.ltrim(key, 0, 99)
        pipe.llen(key)
        pipe.expire(key, 3600)
        
        results = pipe.execute()
        request_count = results[2]
        
        if request_count < min_requests:
            return {'is_threat': False, 'reason': 'Insufficient data'}
        
        recent_requests = redis_client.lrange(key, 0, min_requests - 1)
        requests_data = [json.loads(req) for req in recent_requests]
        
        suspicious_patterns = self.analyze_request_patterns(requests_data)
        
        is_threat = suspicious_patterns['score'] > 0.7
        return {
            'is_threat': is_threat,
            'patterns': suspicious_patterns,
            'reason': f"Suspicious behavior: {', '.join(suspicious_patterns['reasons'])}"
        }
    
    # advance
    def analyze_request_patterns(self, requests: List[Dict]) -> Dict:
        """Analyze request patterns for suspicious behavior"""
        if not requests:
            return {'score': 0, 'reasons': []}
        
        patterns = {'score': 0, 'reasons': []}
        
        # Check for identical user agents
        user_agents = [req.get('user_agent', '') for req in requests]
        if len(set(user_agents)) == 1 and user_agents[0] != '':
            patterns['score'] += 0.3
            patterns['reasons'].append('Identical user agents')
        
        # Check for missing user agents
        empty_ua_count = sum(1 for ua in user_agents if not ua)
        if empty_ua_count > len(requests) * 0.5:
            patterns['score'] += 0.2
            patterns['reasons'].append('Missing user agents')
        
        # Check for rapid sequential requests
        timestamps = [req['timestamp'] for req in requests]
        if len(timestamps) > 1:
            intervals = [timestamps[i] - timestamps[i+1] for i in range(len(timestamps)-1)]
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval < 0.1:
                patterns['score'] += 0.4
                patterns['reasons'].append('Rapid sequential requests')
        
        return patterns
    
    # advance
    def entropy_analysis(self, ip: str, config: Dict) -> Dict:
        """Analyze entropy of request parameters"""
        min_entropy = config.get('min_entropy', 2.0)
        
        query_params = str(request.args)
        user_agent = request.headers.get('User-Agent', '')
        referer = request.headers.get('Referer', '')
        
        combined_data = query_params + user_agent + referer
        
        if not combined_data:
            return {'is_threat': False, 'reason': 'No data for entropy analysis'}
        
        entropy = self.calculate_entropy(combined_data)
        is_threat = entropy < min_entropy
        
        return {
            'is_threat': is_threat,
            'entropy': entropy,
            'threshold': min_entropy,
            'reason': f"Low entropy detected: {entropy:.2f} (threshold: {min_entropy})"
        }
    
    # advance
    def calculate_entropy(self, data: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not data:
            return 0
        
        char_counts = defaultdict(int)
        for char in data:
            char_counts[char] += 1
        
        entropy = 0
        length = len(data)
        
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    # advance
    def progressive_detection(self, ip: str, config: Dict) -> Dict:
        """Progressive penalty system based on historical behavior"""
        key = f"progressive:{ip}"
        
        penalty_level = redis_client.get(key)
        penalty_level = int(penalty_level) if penalty_level else 0
        
        base_threshold = 100
        threshold = max(10, base_threshold - (penalty_level * 20))
        window = 60
        
        rate_key = f"prog_rate:{ip}"
        count = redis_client.incr(rate_key)
        
        if count == 1:
            redis_client.expire(rate_key, window)
        
        is_threat = count > threshold
        
        if is_threat:
            redis_client.incr(key)
            redis_client.expire(key, 3600)
        
        return {
            'is_threat': is_threat,
            'count': count,
            'threshold': threshold,
            'penalty_level': penalty_level,
            'reason': f"Progressive limit: {count}/{threshold} (penalty level: {penalty_level})"
        }
    
    def geographic_analysis(self, ip: str, config: Dict) -> Dict:
        """Geographic analysis placeholder"""
        return {
            'is_threat': False,
            'reason': 'Geographic analysis disabled'
        }
    
    # moderate
    def http_flood_detection(self, ip: str, config: Dict) -> Dict:
        """Detect HTTP flood attacks"""
        threshold = config.get('threshold', 50)
        window = config.get('window', 30)
        
        method = request.method
        path = request.path
        
        key = f"http_flood:{ip}:{method}:{hashlib.md5(path.encode()).hexdigest()[:8]}"
        
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, window)
        
        method_multipliers = {
            'GET': 1.0,
            'POST': 0.5,
            'PUT': 0.3,
            'DELETE': 0.2
        }
        
        adjusted_threshold = threshold * method_multipliers.get(method, 1.0)
        is_threat = count > adjusted_threshold
        
        return {
            'is_threat': is_threat,
            'count': count,
            'threshold': adjusted_threshold,
            'method': method,
            'reason': f"HTTP flood: {count} {method} requests to {path} in {window}s"
        }
    # easy
    def is_already_flagged(self, ip: str) -> bool:
        """Check if IP is already flagged as suspicious"""
        return SuspiciousIP.query.filter_by(ip_address=ip).first() is not None
    # easy
    def flag_suspicious_ip(self, ip: str, reason: str, algorithm: str):
        """Flag IP as suspicious in database"""
        existing = SuspiciousIP.query.filter_by(ip_address=ip).first()
        if not existing:
            suspicious = SuspiciousIP(
                ip_address=ip,
                reason=f"[{algorithm}] {reason}",
                detected_at=datetime.now()
            )
            db.session.add(suspicious)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error flagging IP {ip}: {e}")


# Global detector instance
detector = DDoSDetector()

def detect_ddos_advanced(config: Dict = None):
    """Enhanced DDoS detection function"""
    return detector.detect_threats(config)
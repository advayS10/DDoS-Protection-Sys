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
from ..ml_components.ml_predictor import MLPredictor


class DDoSDetector:
    
    def __init__(self):

        # Initialize ML predictor
        try:
            self.ml_predictor = MLPredictor()
            self.ml_enabled = self.ml_predictor.ready

            print(self.ml_predictor.ready, "Testing enabling")
            
            if self.ml_enabled:
                print("ML Detection: ENABLED")
            else:
                print("ML Detection: DISABLED (models not loaded)")
        except Exception as e:
            print(f"ML initialization error: {e}")
            self.ml_predictor = None
            self.ml_enabled = False


        self.algorithms = {
            'rate_limiting': self.rate_limiting_detection,
            'burst_detection': self.burst_detection,
            # 'behavior_analysis': self.behavior_analysis,
            # 'entropy_analysis': self.entropy_analysis,
            # 'progressive_detection': self.progressive_detection,
            'geographic_analysis': self.geographic_analysis,
            'http_flood_detection': self.http_flood_detection
        }

        # Add ML if available
        if self.ml_enabled:
            self.algorithms['ml_prediction'] = self.ml_prediction
            print("✅ Total algorithms: 4 (including ML)")
        else:
            print("✅ Total algorithms: 3 (rule-based only)")
    
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
    
    
    def detect_threats(self, config: Dict = None) -> Dict:
        """Main detection function that runs all algorithms"""
        if config is None:
            config = {
                'rate_limiting': {'threshold': 100, 'window': 60},
                'burst_detection': {'threshold': 20, 'window': 10},
                # 'behavior_analysis': {'min_requests': 10},
                # 'entropy_analysis': {'min_entropy': 2.0},
                # 'progressive_detection': {'enabled': True},
                'geographic_analysis': {'enabled': False},  # Disabled by default
                'http_flood_detection': {'threshold': 50, 'window': 30},
                'ml_prediction': {'enabled': True,'threshold': 0.7}
            }
        
        results = {}
        ip = self.get_client_ip()
        
        # Skip if already flagged as suspicious
        if self.is_already_flagged(ip):
            return {'ip': ip, 'blocked': True, 'reason': 'Already flagged', 'results': {}}
        
        # Track request for ML (if enabled)
        if self.ml_enabled:
            try:
                packet_size = self._estimate_packet_size()
                self.ml_predictor.feature_calc.tracker.track_request(ip, packet_size)
            except Exception as e:
                print(f"Tracking error: {e}")
        
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
    
    # Future Scope
    def geographic_analysis(self, ip: str, config: Dict) -> Dict:
        """Geographic analysis placeholder"""
        return {
            'is_threat': False,
            'reason': 'Geographic analysis disabled'
        }
    
    
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
    
    
    def is_already_flagged(self, ip: str) -> bool:
        """Check if IP is already flagged as suspicious"""
        return SuspiciousIP.query.filter_by(ip_address=ip).first() is not None
    
    
    def flag_suspicious_ip(self, ip: str, reason: str, algorithm: str):
        """Flag IP as suspicious in database"""
        redis_client.set(f"suspicious:{ip}", f"[{algorithm}] {reason}", ex=300) # 5 minutes TTL
        # existing = SuspiciousIP.query.filter_by(ip_address=ip).first()
        # if not existing:
        #     suspicious = SuspiciousIP(
        #         ip_address=ip,
        #         reason=f"[{algorithm}] {reason}",
        #         detected_at=datetime.now()
        #     )
        #     db.session.add(suspicious)
        #     try:
        #         db.session.commit()
        #     except Exception as e:
        #         db.session.rollback()
        #         print(f"Error flagging IP {ip}: {e}")    

    def ml_prediction(self, ip: str, config: Dict) -> Dict:
        """ML-based detection using Random Forest + Neural Network"""
        if not self.ml_enabled:
            return {
                'is_threat': False,
                'reason': 'ML not available'
            }
        
        try:
            threshold = config.get('threshold', 0.7)
            result = self.ml_predictor.predict(ip, threshold)
            
            return {
                'is_threat': result['is_threat'],
                'confidence': result['confidence'],
                'predictions': result.get('predictions', {}),
                'reason': f"ML detected DDoS with {result['confidence']:.1%} confidence"
            }
            
        except Exception as e:
            return {
                'is_threat': False,
                'error': str(e),
                'reason': f'ML prediction error: {str(e)}'
            }

    def _is_already_blocked(self, ip: str) -> bool:
        """Check if IP is already blocked"""
        return redis_client.exists(f"blocked:{ip}")
    
    def _block_ip(self, ip: str, reason: str, algorithm: str):
        """Block IP in Redis"""
        redis_client.setex(
            f"blocked:{ip}",
            300,  # 5 minutes
            f"[{algorithm}] {reason}"
        )
        print(f"🚫 BLOCKED: {ip} - {reason}")
    
    def _estimate_packet_size(self) -> int:
        """Estimate current request size"""
        size = 0
        
        # Headers
        for key, value in request.headers.items():
            size += len(key) + len(value)
        
        # Path + query
        size += len(request.path)
        if request.query_string:
            size += len(request.query_string)
        
        # Body
        if request.content_length:
            size += request.content_length
        
        # HTTP overhead
        size += 100
        
        return max(size, 200)


# Global detector instance
detector = DDoSDetector()

def detect_ddos_advanced(config: Dict = None):
    """Enhanced DDoS detection function"""
    return detector.detect_threats(config)
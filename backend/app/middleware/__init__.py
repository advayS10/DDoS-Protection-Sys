"""
DDoS detection middleware
"""

from .advanced_ddos_detector import DDoSDetector, detect_ddos_advanced

__all__ = ['DDoSDetector', 'detect_ddos_advanced']
DDOS_CONFIG = {
    'development': {
        'rate_limiting': {'threshold': 1000, 'window': 60},  # More lenient for dev
        'burst_detection': {'threshold': 50, 'window': 10},
        'behavior_analysis': {'min_requests': 10},
        'entropy_analysis': {'min_entropy': 1.0},
        'progressive_detection': {'enabled': False},
        'http_flood_detection': {'threshold': 100, 'window': 30}
    },
    'production': {
        'rate_limiting': {'threshold': 100, 'window': 60},
        'burst_detection': {'threshold': 15, 'window': 10},
        'behavior_analysis': {'min_requests': 5},
        'entropy_analysis': {'min_entropy': 1.5},
        'progressive_detection': {'enabled': True},
        'http_flood_detection': {'threshold': 30, 'window': 30}
    }
}
from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:advay10@localhost/ddos_project_db'  # main db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Model creation
    with app.app_context():
        from .models.traffic_log import TrafficLog
        from .models.suspicious_ip import SuspiciousIP
        db.create_all()

    # Register Middleware
    from .middleware.traffic_log import log_request
    # from .middleware.ddos_detector import detect_ddos  # Your existing basic detector
    from .middleware.advanced_ddos_detector import detect_ddos_advanced  # New advanced detector

    @app.before_request
    def before_request():
        # Log the request first
        log_request()
        # detect_ddos()
        
        # Run advanced DDoS detection
        result = detect_ddos_advanced({
            'rate_limiting': {'threshold': 100, 'window': 60},
            'burst_detection': {'threshold': 15, 'window': 10},
            'behavior_analysis': {'min_requests': 5},
            'entropy_analysis': {'min_entropy': 1.5},
            'progressive_detection': {'enabled': True},
            'http_flood_detection': {'threshold': 30, 'window': 30}
        })
        
        # Block if threat detected
        if result.get('blocked', False):
            # You can customize the response here
            abort(429, description=f"Rate limited: {result.get('reason', 'DDoS protection triggered')}")


    # Import routes
    from .routes.routes import main as main_bp
    from .routes.network_routes import network_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(network_bp)

    return app
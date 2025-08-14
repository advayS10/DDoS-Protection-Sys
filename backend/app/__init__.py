from flask import Flask
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
    from .middleware.ddos_detector import detect_ddos

    @app.before_request
    def before_request():
        log_request()
        detect_ddos()

    # Import routes
    from .routes.routes import main as main_bp
    from .routes.network_routes import network_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(network_bp)

    return app
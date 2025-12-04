from flask import Flask, abort, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():

    load_dotenv()

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}})

    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI  # main db
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
    from .mitigation import handle_suspicious_ip
    from .middleware.get_client_ip import extract_client_ip
    from .mitigation.rate_limiter import is_rate_limited
    from .mitigation.traffic_filter import mark_suspicious, is_suspicious, is_blocked

    # IMPORT CHALLENGE FUNCTIONS
    from .mitigation.challenge_response import (
        has_pending_challenge,
        is_verified,
        needs_challenge,
        get_challenge_response,
        verify_challenge,
        issue_challenge
    )


    @app.before_request
    def before_request():

        """
        DDoS Protection Middleware - CRITICAL ORDER:
        1. Skip challenge verification endpoint
        2. Check pending challenges (BLOCK if unsolved)
        3. Log request
        4. Run DDoS detection
        5. Issue challenge if needed
        """

        # Log the request first
        log_request()

        # ✅ STEP 0: Skip protection for challenge verification endpoint
        CHALLENGE_EXEMPT_ROUTES = ['/challenge', '/api/verify-challenge', '/api/dashboard', '/static']

        if any(request.path.rstrip('/').startswith(route) for route in CHALLENGE_EXEMPT_ROUTES):
            return None
        
        ip = extract_client_ip()

        # ✅ STEP 1: Check if IP has PENDING challenge (MUST be first!)
        # This BLOCKS all requests until challenge is solved
        if has_pending_challenge(ip):
            challenge_data = get_challenge_response(ip)
            # return redirect(url_for('challenge_page'))
            return jsonify({
                'error': 'Challenge Required',
                'message': 'You must solve the challenge before continuing',
                'challenge': get_challenge_response(ip),
                'verify_url': '/api/verify-challenge'
            }), 429
        
        # ✅ STEP 2: Log the request
        # log_request()

        # ✅ STEP 3: Check if already blocked (permanent block)
        if is_blocked(ip):
            return jsonify({
                'error': 'Access Denied',
                'message': 'Your IP has been permanently blocked'
            }), 403
        
        # ✅ STEP 4: Run DDoS detection
        result = detect_ddos_advanced({
            'rate_limiting': {'threshold': 10, 'window': 60},
            'burst_detection': {'threshold': 15, 'window': 10},
            'http_flood_detection': {'threshold': 30, 'window': 30},
            'ml_prediction': {'enabled': True,'threshold': 0.7}
        })


        # ✅ STEP 5: Mark suspicious if detected
        if result.get('blocked', False):
            mark_suspicious(ip, result.get('reason', 'DDoS activity detected'))

        # ✅ STEP 6: Handle suspicious IPs
        if is_suspicious(ip):
            # Check if verified (already solved challenge)
            if is_verified(ip):
                # Verified users get a pass, continue request
                return None
            
            # Not verified, need to issue challenge
            challenge_data = get_challenge_response(ip)
            return jsonify({
                'error': 'Suspicious Activity Detected',
                'message': 'Please solve the challenge to verify you are human',
                'challenge': challenge_data,
                'verify_url': '/api/verify-challenge'
            }), 429
        
        # ✅ STEP 7: Check if challenge is needed based on rate
        # Get request count from your rate limiter
        if is_rate_limited(ip):
            # Check if they're verified
            if not is_verified(ip):
                # Issue challenge
                challenge_data = get_challenge_response(ip)
                mark_suspicious(ip, "Rate limit exceeded")
                return jsonify({
                    'error': 'Rate Limit Exceeded',
                    'message': 'Too many requests. Solve the challenge to continue.',
                    'challenge': challenge_data,
                    'verify_url': '/api/verify-challenge'
                }), 429
        
        # ✅ All checks passed, allow request
        return None

    @app.route('/challenge')
    def challenge_page():
        return render_template('challenge.html')

    @app.route('/api/verify-challenge', methods=['GET'])
    def get_challenge_endpoint():
        ip = extract_client_ip()
        challenge_data = get_challenge_response(ip)
        print(challenge_data)
        return jsonify(challenge_data), 200

    # ADD CHALLENGE VERIFICATION ENDPOINT
    @app.route('/api/verify-challenge', methods=['POST'])
    def verify_challenge_endpoint():
        """Endpoint to verify challenge answers"""
        ip = extract_client_ip()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            answer = int(data.get('answer'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid answer format. Must be a number.'}), 400
        
        # Verify the challenge
        success, message = verify_challenge(ip, answer)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 403

    # Import routes
    from .routes.routes import main as main_bp
    from .routes.network_routes import network_bp
    from .routes.dashboard_routes import dashboard_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(dashboard_bp)


    return app
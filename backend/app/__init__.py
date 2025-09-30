from flask import Flask, abort, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():

    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")  # main db
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
        if request.path.rstrip('/') == '/api/verify-challenge':
            return None
        
        ip = extract_client_ip()

        # ✅ STEP 1: Check if IP has PENDING challenge (MUST be first!)
        # This BLOCKS all requests until challenge is solved
        if has_pending_challenge(ip):
            challenge_data = get_challenge_response(ip)
            return jsonify({
                'error': 'Challenge Required',
                'message': 'You must solve the challenge before continuing',
                'challenge': challenge_data,
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
            'http_flood_detection': {'threshold': 30, 'window': 30}
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

        # # Check if IP is rate limited
        # '''
        # Some Error here - 24/9/2025. Time - 8:42
        # '''
        # # if is_rate_limited(ip):
        # #     mark_suspicious(ip, "Rate limit exceeded")

        # # 1. Detect suspicious behavior
        # # Run advanced DDoS detection
        # result = detect_ddos_advanced({
        #     'rate_limiting': {'threshold': 100, 'window': 60},
        #     'burst_detection': {'threshold': 15, 'window': 10},
        #     'http_flood_detection': {'threshold': 30, 'window': 30}
        # })

        # # Step 2: If suspicious, mark IP
        # if result.get('blocked', False):
        #     mark_suspicious(ip, "DDoS activity detected")

        # if is_suspicious(ip) or is_blocked(ip):
        #     client_response = request.args.get("challenge")
        #     should_block, status, message = handle_suspicious_ip(ip, client_response)
            
        #     if should_block:
        #         abort(status, description=message)

        # Step 3: Mitigation for suspicious IPs
        # if is_blocked(ip):
        #     client_response = request.args.get("challenge")
        #     if is_verified(ip):
        #         unblock_ip(ip)
        #     elif client_response:
        #         if verify_challenge(ip, int(client_response)):
        #             unblock_ip(ip)
        #         else:
        #             abort(403, description="Blocked: Challenge failed")
        #     else:
        #         question = issue_challenge(ip)
        #         abort(403, description=f"Blocked: Solve challenge -> {question}")


        # # 2. Only if suspicious, run mitigation
        # if result.get('blocked', False):
        #     client_response = request.args.get("challenge")  # optional challenge answer
        #     status, message = handle_request(ip, client_response)
        #     if status != 200:
        #         abort(status, description=message)
        
        # # Block if threat detected
        # if result.get('blocked', False):
        #     # You can customize the response here
        #     abort(429, description=f"Rate limited: {result.get('reason', 'DDoS protection triggered')}")


    # ✅ ADD CHALLENGE VERIFICATION ENDPOINT
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
    app.register_blueprint(main_bp)
    app.register_blueprint(network_bp)

    return app
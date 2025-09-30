from datetime import datetime, timedelta
import random

# Store verified IPs (solved challenges)
verified_ips = {}

# Store pending challenges (NOT YET SOLVED) - THIS IS THE KEY FIX
pending_challenges = {}

def generate_challenge():
    """Generate a simple math challenge"""
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = a + b
    return f"What is {a} + {b}?", answer

def issue_challenge(ip: str) -> dict:
    """
    Issue a challenge for the IP and mark it as PENDING.
    This MUST block all requests until solved.
    """
    question, answer = generate_challenge()
    
    # Store in PENDING challenges (not verified yet)
    pending_challenges[ip] = {
        'question': question,
        'answer': answer,
        'created_at': datetime.now(),
        'expiry': datetime.now() + timedelta(minutes=5),
        'attempts': 0
    }
    
    return {
        'question': question,
        'message': 'Please solve this challenge to continue',
        'expires_in': '5 minutes'
    }

def has_pending_challenge(ip: str) -> bool:
    """
    Check if IP has an UNSOLVED challenge.
    If TRUE, all requests MUST be blocked until solved.
    """
    if ip in pending_challenges:
        challenge = pending_challenges[ip]
        # Check if challenge expired
        if datetime.now() > challenge['expiry']:
            del pending_challenges[ip]
            return False
        return True
    return False

def verify_challenge(ip: str, response: int) -> tuple[bool, str]:
    """
    Verify the challenge response.
    Returns: (success: bool, message: str)
    """
    # Check if there's a pending challenge
    if ip not in pending_challenges:
        return False, "No pending challenge found"
    
    challenge = pending_challenges[ip]
    
    # Check if expired
    if datetime.now() > challenge['expiry']:
        del pending_challenges[ip]
        return False, "Challenge expired. Please request a new one."
    
    # Limit attempts
    challenge['attempts'] += 1
    if challenge['attempts'] > 3:
        del pending_challenges[ip]
        return False, "Too many incorrect attempts. Please request a new challenge."
    
    # Check answer
    if response == challenge['answer']:
        # CORRECT! Move from pending to verified
        verified_ips[ip] = {
            'verified_at': datetime.now(),
            'expiry': datetime.now() + timedelta(minutes=15)
        }
        # Remove from pending
        del pending_challenges[ip]
        return True, "Challenge solved! Access granted for 15 minutes."
    
    remaining = 3 - challenge['attempts']
    return False, f"Incorrect answer. {remaining} attempts remaining."

def is_verified(ip: str) -> bool:
    """
    Check if IP has solved a challenge and is verified.
    Verified IPs can bypass rate limits.
    """
    if ip not in verified_ips:
        return False
    
    data = verified_ips[ip]
    
    # Check if verification expired
    if datetime.now() > data['expiry']:
        del verified_ips[ip]
        return False
    
    return True

def needs_challenge(ip: str, request_count: int, threshold: int = 20) -> bool:
    """
    Determine if IP needs a challenge based on request rate.
    """
    # Already verified, no challenge needed
    if is_verified(ip):
        return False
    
    # Already has pending challenge
    if has_pending_challenge(ip):
        return True
    
    # Exceeded threshold, needs challenge
    if request_count > threshold:
        return True
    
    return False

def get_challenge_response(ip: str) -> dict:
    """
    Get the challenge to show to the user.
    """
    if ip in pending_challenges:
        challenge = pending_challenges[ip]
        return {
            'question': challenge['question'],
            'message': 'You must solve this challenge before continuing',
            'attempts_remaining': 3 - challenge['attempts']
        }
    else:
        # Generate new challenge
        return issue_challenge(ip)

def cleanup_expired():
    """Clean up expired challenges and verifications"""
    now = datetime.now()
    
    # Clean expired pending challenges
    expired_pending = [ip for ip, data in pending_challenges.items() 
                      if now > data['expiry']]
    for ip in expired_pending:
        del pending_challenges[ip]
    
    # Clean expired verifications
    expired_verified = [ip for ip, data in verified_ips.items() 
                       if now > data['expiry']]
    for ip in expired_verified:
        del verified_ips[ip]
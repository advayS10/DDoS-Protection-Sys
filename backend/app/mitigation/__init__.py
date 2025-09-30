from flask import abort, request
from datetime import datetime
from .traffic_filter import is_blocked, is_suspicious, block_ip, mark_suspicious, unblock_ip
from .challenge_response import issue_challenge, verify_challenge, is_verified
from ..models.suspicious_ip import SuspiciousIP
from .. import db

def handle_suspicious_ip(ip: str, client_response: str = None):
    """
    Handle mitigation for a suspicious IP with proper blocking logic
    Returns: (should_block, status_code, message)
    """
    
    # Check if IP is already verified and allowed
    if is_verified(ip):
        return False, 200, "IP verified, allowing traffic"
    
    # Check if IP is blocked
    if is_blocked(ip):
        # If client provided a response to challenge
        if client_response:
            try:
                response_int = int(client_response)
                if verify_challenge(ip, response_int):
                    unblock_ip(ip)
                    return False, 200, "Challenge passed, IP unblocked"
                else:
                    # Failed challenge - keep blocked
                    return True, 403, "Challenge failed - access denied"
            except ValueError:
                return True, 400, "Invalid challenge response format"
        
        # No response provided - issue new challenge
        question = issue_challenge(ip)
        return True, 403, f"Access denied. Solve: {question} (append ?challenge=ANSWER to your request)"
    
    # IP is suspicious but not blocked yet - issue challenge
    if is_suspicious(ip):
        if client_response:
            try:
                response_int = int(client_response)
                if verify_challenge(ip, response_int):
                    return False, 200, "Challenge passed, allowing traffic"
                else:
                    # Failed challenge - now block the IP
                    block_ip(ip, "Failed challenge response")
                    return True, 403, "Challenge failed - IP blocked"
            except ValueError:
                return True, 400, "Invalid challenge response format"
        
        # First time suspicious - issue challenge
        question = issue_challenge(ip)
        return True, 403, f"Suspicious activity detected. Solve: {question} (append ?challenge=ANSWER to your request)"
    
    # IP is not suspicious - allow
    return False, 200, "OK"
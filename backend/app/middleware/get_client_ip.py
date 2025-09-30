from flask import request

def extract_client_ip() -> str:
    """
    Safely extract the real client IP from request headers and remote_addr
    """
    headers_to_check = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Client-IP',
        'CF-Connecting-IP',  # Cloudflare
        'HTTP_X_FORWARDED_FOR',
        'HTTP_CLIENT_IP'
    ]
    
    for header in headers_to_check:
        ip = request.headers.get(header)
        if ip:
            return ip.split(',')[0].strip()  # take first IP if multiple
    return request.remote_addr or 'unknown'
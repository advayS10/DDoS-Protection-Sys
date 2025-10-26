'''
Gets client IP from Flask request
'''

from flask import request

def get_client_ip():

    # Check proxy headers
    headers_to_check = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP'
    ]

    for header in headers_to_check:
        ip = request.headers.get(header)
        if ip:
            return ip.split(',')[0].strip()
        
    return request.remote_addr or 'unknown'

if __name__ == "__main__":
    from flask import Flask
    
    app = Flask(__name__)
    
    with app.test_request_context('/', headers={'X-Forwarded-For': '1.2.3.4'}):
        ip = get_client_ip()
        print(f"Extracted IP: {ip}")
        
        if ip == '1.2.3.4':
            print("✅ Works!")
        else:
            print("❌ Failed")
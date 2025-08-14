import requests

for i in range(110):
    r = requests.get("http://127.0.0.1:5000/api/logs")  # replace with your route
    print(f"Request {i+1}: {r.status_code}")

from flask import Blueprint, jsonify
from ..services.log_request import get_latest_logs
from ..services.get_suspicious_ip import get_suspicious_ips

main = Blueprint("main", __name__)

@main.route('/api/logs', methods=['Get'])
def get_logs():
    logs = get_latest_logs()
    return jsonify(logs)

@main.route('/api/suspicious', methods=['GET'])
def get_suspicious():
    ips = get_suspicious_ips()
    return jsonify(ips)
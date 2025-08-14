from flask import request
from ..models.traffic_log import TrafficLog
from .. import db

def log_request():
    ip = request.remote_addr
    method = request.method
    endpoint = request.path

    # log = TrafficLog(ip_address=ip, method=method, endpoint=endpoint)
    # db.session.add(log)
    # db.session.commit()
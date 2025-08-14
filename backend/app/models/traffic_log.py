from datetime import datetime
from .. import db

class TrafficLog(db.Model):
    
    __tablename__ = 'traffic_logs'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    method = db.Column(db.String(10))
    endpoint = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.now)
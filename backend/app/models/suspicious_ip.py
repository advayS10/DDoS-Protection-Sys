from datetime import datetime
from .. import db

class SuspiciousIP(db.Model):
   
    __tablename__ = 'suspicious_ip'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

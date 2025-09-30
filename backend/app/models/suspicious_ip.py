from datetime import datetime
from .. import db

# class SuspiciousIP(db.Model):
   
#     __tablename__ = 'suspicious_ip'

#     id = db.Column(db.Integer, primary_key=True)
#     ip_address = db.Column(db.String(100), nullable=False)
#     reason = db.Column(db.String(255), nullable=False)
#     detected_at = db.Column(db.DateTime, default=datetime.now)
#     timestamp = db.Column(db.DateTime, default=datetime.now)

#     def __repr__(self):
#         return f'<SuspiciousIP {self.ip_address}>'

class SuspiciousIP(db.Model):

    __tablename__ = 'suspicious_ip'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False, unique=True)
    reason = db.Column(db.String(255))
    detected_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='suspicious')  # 'suspicious', 'blocked', 'verified'
    blocked_at = db.Column(db.DateTime)
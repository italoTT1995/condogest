from app import db
from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plate = db.Column(db.String(10), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('vehicles', lazy=True))

    def __repr__(self):
        return f'<Vehicle {self.plate}>'

from app import db
from datetime import datetime

class CommonArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer)
    image_url = db.Column(db.String(255)) # Placeholder for image path
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True) # Multitenancy
    
    # Relationships
    reservations = db.relationship('Reservation', backref='area', lazy='dynamic')

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('common_area.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected, cancelled
    access_token = db.Column(db.String(100), unique=True, nullable=True) # QR Code Token
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

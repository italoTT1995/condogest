from datetime import datetime
from app import db

class Delivery(db.Model):
    __tablename__ = 'delivery'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending') # pending, picked_up
    
    recipient_label = db.Column(db.String(100)) # Name written on the package
    storage_location = db.Column(db.String(100)) # Where it is stored (e.g. Shelf A)

    received_at = db.Column(db.DateTime, default=datetime.now)
    picked_up_at = db.Column(db.DateTime, nullable=True)
    picked_up_by = db.Column(db.String(100), nullable=True) # Name of person who picked up
    
    # Relationships
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    unit = db.relationship('Unit', backref='deliveries')

    def __repr__(self):
        return f'<Delivery {self.id} Unit:{self.unit_id}>'

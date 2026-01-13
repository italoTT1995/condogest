from app import db
from datetime import datetime

class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    location_found = db.Column(db.String(100))
    found_at = db.Column(db.DateTime, default=datetime.now)
    image_filename = db.Column(db.String(255))
    status = db.Column(db.String(20), default='unclaimed') # unclaimed, claimed
    
    # Who registered the item (Porteiro)
    found_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Who claimed it
    claimed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    claimed_at = db.Column(db.DateTime, nullable=True)
    
    # Context
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True)

    finder = db.relationship('User', foreign_keys=[found_by_id])
    claimer = db.relationship('User', foreign_keys=[claimed_by_id])

    def __repr__(self):
        return f'<LostItem {self.description}>'

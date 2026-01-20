from app import db
from datetime import datetime

class ClassifiedAd(db.Model):
    __tablename__ = 'classified_ad'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=True) # 0 for donation/free
    contact_info = db.Column(db.String(100)) # Ads: WhatsApp or internal chat
    image_filename = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active') # active, sold, archived
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('classifieds', lazy=True))

    def __repr__(self):
        return f'<ClassifiedAd {self.title}>'

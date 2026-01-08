from app import db
from datetime import datetime

class Condominium(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    cnpj = db.Column(db.String(20)) # Optional
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    units = db.relationship('Unit', backref='condominium', lazy='dynamic')
    users = db.relationship('User', backref='condominium', lazy='dynamic')

    def __repr__(self):
        return f'<Condominium {self.name}>'

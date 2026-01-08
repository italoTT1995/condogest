from app import db
from datetime import datetime

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False) # minutes, convention, financial, contract, other
    is_public = db.Column(db.Boolean, default=True) # Public to all residents?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True)
    
    # FK
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    uploader = db.relationship('User', backref='uploaded_documents')

    def __repr__(self):
        return f'<Document {self.title}>'

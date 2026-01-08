from datetime import datetime
from app import db

class Visitor(db.Model):
    __tablename__ = 'visitor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    visits = db.relationship('VisitLog', backref='visitor', lazy=True)

    def __repr__(self):
        return f'<Visitor {self.name}>'

class VisitLog(db.Model):
    __tablename__ = 'visit_log'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=True) # Null if it's a resident
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=True) # Null if global access? Or keep mandatory?
    entry_time = db.Column(db.DateTime, nullable=True) # Now nullable for pre-auth
    exit_time = db.Column(db.DateTime, nullable=True)
    observation = db.Column(db.String(200), nullable=True)
    
    # New fields for Pre-authorization
    status = db.Column(db.String(20), default='active') # 'scheduled', 'active', 'completed'
    expected_arrival = db.Column(db.DateTime, nullable=True)
    scheduled_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Resident who authorized
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True) # Multitenancy silo

    # New fields for Access History (Residents)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # If it's a resident
    user = db.relationship('User', foreign_keys=[user_id]) # Relationship for display
    access_status = db.Column(db.String(20)) # 'granted', 'denied'
    failure_reason = db.Column(db.String(100)) # 'debt', 'banned', 'invalid_token'

    # Relationships are handled by backref in Visitor and Unit (need to add to Unit?)
    # Let's add explicit relationship to Unit here if needed, or rely on Unit backref if we add it there.
    # For now, let's just assume we can query unit by unit_id.
    unit = db.relationship('Unit', backref='visits')

    def __repr__(self):
        return f'<VisitLog Visitor:{self.visitor_id} Unit:{self.unit_id}>'

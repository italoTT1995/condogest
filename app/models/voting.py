from datetime import datetime
from app import db

class Assembly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='scheduled') # scheduled, open, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True) # Multitenancy
    
    # Relationships
    items = db.relationship('AgendaItem', backref='assembly', lazy='dynamic', cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='assembly', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Assembly {self.title}>'

class AgendaItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assembly_id = db.Column(db.Integer, db.ForeignKey('assembly.id'), nullable=False)
    
    # Relationships
    votes = db.relationship('Vote', backref='item', lazy='dynamic', cascade='all, delete-orphan')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agenda_item_id = db.Column(db.Integer, db.ForeignKey('agenda_item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    choice = db.Column(db.String(20), nullable=False) # yes, no, abstain
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='votes')
    unit = db.relationship('Unit', backref='votes')

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assembly_id = db.Column(db.Integer, db.ForeignKey('assembly.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='attendances')
    unit = db.relationship('Unit', backref='attendances')

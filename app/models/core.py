from datetime import datetime
from app import db

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block = db.Column(db.String(10), nullable=False)
    number = db.Column(db.String(10), nullable=False)
    # Status: occupied, vacant
    status = db.Column(db.String(20), default='vacant')
    
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True) # Nullable for migration
    
    residents = db.relationship('User', backref='unit', lazy='dynamic')

    def __repr__(self):
        return f'<Unit {self.block}-{self.number}>'

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Category: maintenance (Chamado), complaint (Denúncia)
    category = db.Column(db.String(20), default='maintenance')
    status = db.Column(db.String(20), default='open') # open, in_progress, closed
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    image_filename = db.Column(db.String(255)) # For photo attachment
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Ticket {self.title}>'

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True) # New: Photo
    is_important = db.Column(db.Boolean, default=False)       # New: Urgent/Pinned
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True)
    
    author = db.relationship('User')

    def __repr__(self):
        return f'<Notice {self.title}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(140))
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, paid, overdue
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Now optional (payer)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=True) # New: Link to Unit
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True)

    # Relationships defined in User model via backref
    # user = db.relationship('User', foreign_keys=[user_id]) 
    
    # Unit relationship
    unit = db.relationship('Unit', foreign_keys=[unit_id])

    def __repr__(self):
        return f'<Payment {self.amount} for Unit {self.unit_id}>'

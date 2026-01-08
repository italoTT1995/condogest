from datetime import datetime
from app import db

class TicketComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    ticket = db.relationship('Ticket', backref=db.backref('comments', lazy='dynamic', cascade='all, delete-orphan'))
    author = db.relationship('User')

    def __repr__(self):
        return f'<TicketComment {self.id} by {self.user_id}>'

from app import db
from datetime import datetime

class MaintenanceTask(db.Model):
    __tablename__ = 'maintenance_task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    
    # Status: pending, in_progress, completed, overdue
    status = db.Column(db.String(20), default='pending')
    
    # Optional: assign to a specific user (e.g. Zelador)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignee = db.relationship('User', backref=db.backref('assigned_tasks', lazy=True))
    condo = db.relationship('Condominium', backref=db.backref('maintenance_tasks', lazy=True))

    def __repr__(self):
        return f'<MaintenanceTask {self.title}>'

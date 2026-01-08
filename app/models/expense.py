from datetime import datetime
from app import db

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Manutenção, Pessoal, Contas, Outros
    amount = db.Column(db.Float, nullable=False)
    date_incurred = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    proof_filename = db.Column(db.String(255), nullable=True) # Receipt image/PDF
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True)

    def __repr__(self):
        return f'<Expense {self.description} - {self.amount}>'

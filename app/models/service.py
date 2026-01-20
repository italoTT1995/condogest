from app import db

class ServiceProvider(db.Model):
    __tablename__ = 'service_provider'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50)) # e.g., "Diarista", "Babá", "Personal"
    cpf = db.Column(db.String(14))
    
    # Simple day tracking (Boolean flags or comma string)
    # Storing as string "Mon,Wed,Fri" or "Seg,Qua,Sex"
    allowed_days = db.Column(db.String(100)) 
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Employer
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'))
    
    status = db.Column(db.String(20), default='active')
    
    # Relationships
    user = db.relationship('User', backref=db.backref('providers', lazy=True))
    unit = db.relationship('Unit', backref=db.backref('providers', lazy=True))

    def __repr__(self):
        return f'<ServiceProvider {self.name}>'

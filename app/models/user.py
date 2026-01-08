from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    # Permissions
    is_admin = db.Column(db.Boolean, default=False)
    can_manage_concierge = db.Column(db.Boolean, default=False)
    can_manage_reservations = db.Column(db.Boolean, default=False)
    can_manage_complaints = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    
    # Old text role field (kept for backward compatibility during migration)
    role = db.Column(db.String(20), nullable=False, default='resident') 
    
    # New Dynamic Role
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    user_role = db.relationship('Role', backref='users')
    
    # Resident details
    full_name = db.Column(db.String(120))
    cpf = db.Column(db.String(14))
    contact = db.Column(db.String(20))
    profile_image = db.Column(db.String(255), default='default.jpg')
    access_token = db.Column(db.String(100), unique=True, nullable=True) # Permanent QR Token
    
    # Security Fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    must_change_password = db.Column(db.Boolean, default=False)
    
    
    # Relationships
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    condo_id = db.Column(db.Integer, db.ForeignKey('condominium.id'), nullable=True) # Nullable for migration
    
    tickets = db.relationship('Ticket', backref='author', lazy='dynamic')
    payments = db.relationship('Payment', backref='resident', lazy='dynamic')
    reservations = db.relationship('Reservation', backref='resident', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        # Check both old string role and new Role object
        if self.user_role:
             # Admin and Síndico have administrative access
             return self.user_role.name in ['Admin', 'Síndico', 'Sindico']
        return self.role == 'admin'

    @property
    def is_superuser(self):
        # Only 'Admin' is a superuser
        if self.user_role:
             return self.user_role.name == 'Admin'
        return self.role == 'admin'

    @property
    def can_register_visits(self):
        # Allowed: Admin, Porteiro, Zelador
        # Blocked: Síndico, Morador (and others by default)
        if self.user_role:
             return self.user_role.can_manage_concierge or self.user_role.is_admin
        return self.role.lower() in ['admin', 'porteiro', 'zelador']

    @property
    def is_porteiro(self):
        if self.user_role:
            return self.user_role.name == 'Porteiro'
        return self.role.lower() == 'porteiro'

    @property
    def can_manage_complaints(self):
        if self.user_role:
             return self.user_role.can_manage_complaints or self.user_role.is_admin
        return False # Old roles don't have this explicitly

    @property
    def is_resident(self):
        # Access to My Reservations, My Vehicles, Tickets, etc.
        # Admin is treated as resident for testing/management.
        if self.user_role:
            return self.user_role.name in ['Morador', 'Síndico', 'Sindico', 'Admin']
        return self.role.lower() in ['resident', 'admin', 'morador', 'síndico']

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

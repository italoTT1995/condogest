from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    print("Tentando criar admin...")
    
    # Verifica se ja existe
    existing = User.query.filter_by(username='admin').first()
    if existing:
        print("Usuario 'admin' ja existe. Deletando para recriar...")
        db.session.delete(existing)
        db.session.commit()
    
    # Cria do zero
    admin = User(username='admin', email='admin@condo.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    print("SUCESSO: Usuario 'admin' criado com senha 'admin123'.")

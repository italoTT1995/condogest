from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    print("Criando tabelas do banco de dados...")
    db.create_all()
    
    if not User.query.filter_by(username='admin').first():
        print("Criando usuário administrador padrão...")
        admin = User(username='admin', email='admin@condo.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Usuário 'admin' criado com senha 'admin123'.")
    else:
        print("Usuário 'admin' já existe.")
        
    print("Database initialized successfully.")

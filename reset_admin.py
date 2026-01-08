from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    print("Tentando redefinir usuario admin...")
    try:
        # Tenta pegar o usuario existente
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print("Usuario admin encontrado. Atualizando senha...")
            admin.set_password('admin123')
        else:
            print("Usuario admin NAO encontrado. Criando novo...")
            admin = User(username='admin', email='admin@condo.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
        db.session.commit()
        print("SUCESSO: Usuario 'admin' configurado com senha 'admin123'.")
        print("Tente fazer login agora.")
    except Exception as e:
        print(f"ERRO: {e}")
        print("Verifique se o banco de dados esta rodando e acessivel.")

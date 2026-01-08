from app import create_app, db
from app.models.user import User
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("ATENCAO: Isso vai apagar e recriar todas as tabelas do banco.")
    print("Corrigindo tamanho da coluna de senha...")
    
    # Forçar queda das tabelas
    db.drop_all()
    print("Tabelas antigas removidas.")
    
    # Recriar
    db.create_all()
    print("Novas tabelas criadas com sucesso.")
    
    # Criar admin
    print("Criando usuario admin...")
    admin = User(username='admin', email='admin@condo.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    print("SUCESSO: Banco recriado e admin configurado.")

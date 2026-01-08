from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    print("--- DIAGNOSTICO DE LOGIN ---")
    
    # 1. Verifica config do banco
    print(f"Banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # 2. Tenta buscar usuario
    username = 'admin'
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"ERRO CRITICO: Usuario '{username}' NAO encontrado no banco de dados!")
    else:
        print(f"Usuario '{username}' encontrado. ID: {user.id}, Role: {user.role}")
        print(f"Hash da senha armazenada: {user.password_hash}")
        
        # 3. Teste de senha
        senha_teste = 'admin123'
        if user.check_password(senha_teste):
            print(f"SUCESSO: A senha '{senha_teste}' bate com o hash no banco.")
            print("Se voce nao consegue logar no site, o problema pode ser cookies/navegador.")
        else:
            print(f"FALHA: A senha '{senha_teste}' NAO bate com o hash no banco.")
            print("Redefinindo senha agora...")
            user.set_password(senha_teste)
            db.session.commit()
            print("Senha redefinida para 'admin123'. Tente novamente.")
            
    print("--------------------------")

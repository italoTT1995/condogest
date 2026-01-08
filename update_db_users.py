from app import create_app, db
from sqlalchemy import text
import os

app = create_app()

with app.app_context():
    print("Atualizando tabela 'user' para suportar Foto de Perfil...")
    
    try:
        with db.engine.connect() as conn:
            # Check/Add 'profile_image'
            try:
                conn.execute(text("SELECT profile_image FROM \"user\" LIMIT 1"))
                print("Coluna 'profile_image' já existe.")
            except Exception:
                print("Adicionando coluna 'profile_image'...")
                # Note: "user" is a reserved keyword in some DBs, hence quotes. 
                # SQLAlchemy model name is 'user' (lowercase) so table is likely 'user' or 'users' depending on config.
                # In app/models/user.py no __tablename__ is set, so it defaults to 'user'. 
                # Postgres requires quotes for "user" table usually.
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN profile_image VARCHAR(255) DEFAULT 'default_avatar.png'"))
                conn.commit()
                print("Coluna 'profile_image' adicionada.")
                
    except Exception as e:
        print(f"Erro ao atualizar banco: {e}")
        
    # Create uploads/profiles directory
    upload_dir = app.config['UPLOAD_FOLDER']
    profiles_dir = os.path.join(upload_dir, 'profiles')
    if not os.path.exists(profiles_dir):
        os.makedirs(profiles_dir)
        print(f"Diretório criado: {profiles_dir}")

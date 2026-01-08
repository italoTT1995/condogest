from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Atualizando banco de dados (Segurança)...")
    try:
        with db.engine.connect() as conn:
            # Add failed_login_attempts
            try:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN failed_login_attempts INTEGER DEFAULT 0"))
                print("Coluna failed_login_attempts adicionada.")
            except Exception as e:
                print(f"Nota: failed_login_attempts talvez ja exista. {e}")
            
            # Add locked_until
            try:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN locked_until TIMESTAMP"))
                print("Coluna locked_until adicionada.")
            except Exception as e:
                print(f"Nota: locked_until talvez ja exista. {e}")
            
            conn.commit()
    except Exception as e:
        print(f"Erro ao migrar: {e}")

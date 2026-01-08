from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Correcao de Banco de Dados: Adicionando 'profile_image'...")
    
    try:
        with db.engine.connect() as conn:
            # Force rollback of any stuck transaction context if possible, though new connection should be clean.
            # We will use a simple block.
            
            # Check if column exists
            try:
                # Note: "user" must be quoted in Postgres
                conn.execute(text('SELECT profile_image FROM "user" LIMIT 1'))
                print(">> Coluna 'profile_image' ja existe. Nada a fazer.")
            except Exception:
                print(">> Coluna nao encontrada. Tentando adicionar...")
                # We need to catch the exception from the SELECT to proceed, 
                # but sometimes the connection gets tainted. 
                # It's safer to use a fresh connection or ensure transaction is rolled back.
                pass

    except Exception as e:
        print(f"Erro ao verificar: {e}")

    # New attempt to ADD column in a fresh transaction block
    try:
        with db.engine.connect() as conn:
            trans = conn.begin()
            try:
                # Check again or just try ADD (ADD IF NOT EXISTS is not standard SQL everywhere, but helpful)
                # Postgres support: ALTER TABLE "user" ADD COLUMN IF NOT EXISTS profile_image ...
                conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS profile_image VARCHAR(255) DEFAULT \'default_avatar.png\''))
                trans.commit()
                print(">> Sucesso! Coluna adicionada.")
            except Exception as e:
                trans.rollback()
                print(f">> Erro ao adicionar coluna: {e}")
                
    except Exception as e:
        print(f"Erro geral: {e}")
        
    print("Verificacao concluida.")

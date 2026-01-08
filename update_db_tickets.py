from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Verificando se precisa adicionar coluna 'image_filename' na tabela 'ticket'...")
    try:
        # Check if column exists
        # This is a bit postgres specific or raw SQL specific valid for sqlite/postgres
        # For simplicity, we try to select it, if fails, we add it.
        # But safest way in raw sql without inspecting schema:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT image_filename FROM ticket LIMIT 1"))
            print("Coluna 'image_filename' já existe.")
    except Exception:
        print("Coluna não encontrada. Adicionando...")
        try:
            with db.engine.connect() as conn:
                # Assuming Postgres or SQLite. ALTER TABLE works for both usually for adding column
                conn.execute(text("ALTER TABLE ticket ADD COLUMN image_filename VARCHAR(255)"))
                conn.commit()
            print("Coluna 'image_filename' adicionada com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar coluna: {e}")
            
    # Also ensure upload directory exists
    import os
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print(f"Diretório de uploads criado: {upload_dir}")
    
    # Specific subfolder for tickets
    ticket_upload_dir = os.path.join(upload_dir, 'tickets')
    if not os.path.exists(ticket_upload_dir):
        os.makedirs(ticket_upload_dir)
        print(f"Diretório de tickets criado: {ticket_upload_dir}")

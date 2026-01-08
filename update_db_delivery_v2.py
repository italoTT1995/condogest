from app import create_app, db
from app.models.delivery import Delivery
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Atualizando tabela Delivery (v2)...")
    try:
        with db.engine.connect() as conn:
            # Add recipient_label
            try:
                conn.execute(text("ALTER TABLE delivery ADD COLUMN recipient_label VARCHAR(100)"))
                print("Coluna recipient_label adicionada.")
            except Exception as e:
                print(f"Nota: recipient_label talvez ja exista. {e}")
            
            # Add storage_location
            try:
                conn.execute(text("ALTER TABLE delivery ADD COLUMN storage_location VARCHAR(100)"))
                print("Coluna storage_location adicionada.")
            except Exception as e:
                print(f"Nota: storage_location talvez ja exista. {e}")
            
            conn.commit()
    except Exception as e:
        print(f"Erro ao migrar: {e}")

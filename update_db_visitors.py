from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Atualizando tabela 'visit_log' (Tentativa 2)...")
    
    # 1. Add status
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE visit_log ADD COLUMN status VARCHAR(20) DEFAULT 'active'"))
            conn.commit()
            print("Coluna 'status' adicionada.")
    except Exception as e:
        print(f"Nota sobre 'status': {e}")

    # 2. Add expected_arrival
    try:
         with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE visit_log ADD COLUMN expected_arrival TIMESTAMP"))
            conn.commit()
            print("Coluna 'expected_arrival' adicionada.")
    except Exception as e:
        print(f"Nota sobre 'expected_arrival': {e}")
        
    # 3. Add scheduled_by
    try:
         with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE visit_log ADD COLUMN scheduled_by INTEGER"))
            conn.commit()
            print("Coluna 'scheduled_by' adicionada.")
    except Exception as e:
        print(f"Nota sobre 'scheduled_by': {e}")
    
    print("Concluído.")

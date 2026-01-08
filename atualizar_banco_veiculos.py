from app import create_app, db
from app.models.vehicle import Vehicle

app = create_app()

with app.app_context():
    # Create the vehicle table
    # Since we are not using Alembic/Flask-Migrate heavily yet, we can use create_all 
    # but it won't touch existing tables suitable for development
    try:
        Vehicle.__table__.create(db.engine)
        print("Tabela 'vehicle' criada com sucesso.")
    except Exception as e:
        print(f"Erro (talvez tabela ja exista): {e}")

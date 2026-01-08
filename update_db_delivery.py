from app import create_app, db
from app.models.delivery import Delivery
import os

app = create_app()

with app.app_context():
    print("Atualizando banco de dados para Encomendas...")
    try:
        # Create table
        db.create_all() # This creates all tables that don't exist. Since Delivery is new/imported, it should be created.
        print("Tabelas verificadas/criadas.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        
    # Create upload directory
    upload_dir = app.config['UPLOAD_FOLDER']
    deliveries_dir = os.path.join(upload_dir, 'deliveries')
    if not os.path.exists(deliveries_dir):
        os.makedirs(deliveries_dir)
        print(f"Diretório criado: {deliveries_dir}")

from app import create_app, db
from app.models.visitor import Visitor, VisitLog
import sqlalchemy

app = create_app()

with app.app_context():
    print("Atualizando banco de dados para incluir Visitor e VisitLog...")
    try:
        db.create_all()
        print("Tabelas 'visitor' e 'visit_log' criadas/verificadas com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

from app import create_app, db
from app.models.expense import Expense

app = create_app()

with app.app_context():
    print("Criando tabela de Despesas (Expenses)...")
    try:
        db.create_all()
        print("Tabelas atualizadas com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar banco: {e}")

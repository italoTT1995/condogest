from app import create_app, db
from app.models.ticket_comment import TicketComment

app = create_app()

with app.app_context():
    print("Criando tabela de Comentários de Chamados (TicketComments)...")
    try:
        db.create_all()
        print("Tabelas atualizadas com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar banco: {e}")

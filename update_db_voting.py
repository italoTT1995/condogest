from app import create_app, db
from app.models.voting import Assembly, AgendaItem, Vote, Attendance

app = create_app()

with app.app_context():
    print("Criando tabelas de Assembleia e Votação...")
    try:
        db.create_all()
        print("Tabelas (Assembly, AgendaItem, Vote, Attendance) criadas com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar banco: {e}")

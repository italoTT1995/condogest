from app import create_app, db
from app.models.user import User
from app.models.notification import Notification

app = create_app()

with app.app_context():
    print("Atualizando banco de dados com tabela de notificações...")
    db.create_all()
    print("Concluído.")

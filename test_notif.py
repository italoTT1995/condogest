from app import create_app, db
from app.models.user import User
from app.models.notification import Notification

app = create_app()

with app.app_context():
    print("Testando criação de notificação...")
    user = User.query.first()
    if user:
        print(f"Usuário encontrado: {user.username} (ID: {user.id})")
        
        notif = Notification(
            user_id=user.id,
            message="Teste de notificação do sistema!"
        )
        db.session.add(notif)
        db.session.commit()
        print("Notificação criada com sucesso.")
        
        # Verify
        check = Notification.query.filter_by(user_id=user.id).order_by(Notification.id.desc()).first()
        print(f"Status da notificação recuperada: {check.message}")
    else:
        print("Nenhum usuário encontrado para testar.")

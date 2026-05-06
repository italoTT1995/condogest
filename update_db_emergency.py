from app import create_app, db
from sqlalchemy import text
from app.models.notification import Notification

app = create_app()

def run_migration():
    with app.app_context():
        try:
            # Check if column exists by trying to select it
            db.session.execute(text("SELECT notification_type FROM notifications LIMIT 1"))
            print("Coluna 'notification_type' ja existe na tabela 'notifications'.")
        except Exception as e:
            db.session.rollback()
            print("Coluna 'notification_type' nao existe. Adicionando...")
            try:
                db.session.execute(text("ALTER TABLE notifications ADD COLUMN notification_type VARCHAR(50) DEFAULT 'info'"))
                db.session.commit()
                print("Coluna 'notification_type' adicionada com sucesso!")
            except Exception as inner_e:
                db.session.rollback()
                print(f"Erro ao adicionar coluna: {inner_e}")

if __name__ == "__main__":
    run_migration()

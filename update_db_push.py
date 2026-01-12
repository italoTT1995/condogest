from app import create_app, db
from app.models.notification import PushSubscription

app = create_app()

with app.app_context():
    print("Creating push_subscriptions table...")
    try:
        PushSubscription.__table__.create(db.engine)
        print("Table created successfully!")
    except Exception as e:
        print(f"Error (might already exist): {e}")

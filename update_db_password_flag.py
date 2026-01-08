from app import create_app,db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE "user" ADD COLUMN must_change_password BOOLEAN DEFAULT false'))
            conn.commit()
            print("Migration successful: Added 'must_change_password' column to 'user' table.")
        except Exception as e:
            print(f"Migration failed (maybe column exists?): {e}")

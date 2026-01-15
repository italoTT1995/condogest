from app import create_app, db
from app.models.core import Payment, Unit
from app.models.user import User
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("--- Migrating Payments to Unit-Based ---")
    
    # 1. Add unit_id column
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE payment ADD COLUMN IF NOT EXISTS unit_id INTEGER REFERENCES unit(id)"))
            conn.execute(text("ALTER TABLE payment ALTER COLUMN user_id DROP NOT NULL"))
            conn.commit()
        print("Schema updated: Added unit_id, made user_id nullable.")
    except Exception as e:
        print(f"Schema update note: {e}")

    # 2. Backfill unit_id based on user_id
    payments = Payment.query.filter(Payment.unit_id == None).all()
    print(f"Found {len(payments)} payments to migrate.")
    
    count = 0
    for p in payments:
        if p.user_id:
            user = User.query.get(p.user_id)
            if user and user.unit_id:
                p.unit_id = user.unit_id
                count += 1
            else:
                print(f"Warning: Payment {p.id} (User {p.user_id}) has no Unit linked.")
    
    db.session.commit()
    print(f"Migration Complete: {count} payments updated.")

from app import create_app, db
from app.models.user import User
from app.models.core import Payment
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Starting Data Leakage Fix Migration V6 (Payment)...")
        
        try:
            # Add condo_id to payment
            print("Adding condo_id to payment...")
            try:
                db.session.execute(text("ALTER TABLE payment ADD COLUMN condo_id INTEGER REFERENCES condominium(id)"))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                if "duplicate" in str(e) or "already exists" in str(e):
                    print("  - column condo_id already exists in payment.")
                else:
                    print(f"  - Error updating payment schema: {e}")

            # Update existing payments based on User's condo
            print("Backfilling condo_id from Users...")
            payments = Payment.query.filter(Payment.condo_id == None).all()
            count = 0
            for p in payments:
                user = User.query.get(p.user_id)
                if user and user.condo_id:
                    p.condo_id = user.condo_id
                    count += 1
                else:
                    # Fallback
                    p.condo_id = 1
            
            db.session.commit()
            print(f"  - Updated {count} payments with correct condo_id.")
            print("Migration V6 completed successfully!")
            
        except Exception as e:
            print(f"Migration fatal error: {e}")

if __name__ == "__main__":
    migrate()

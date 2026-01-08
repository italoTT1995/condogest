from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Starting Data Leakage Fix Migration V2 (Expense)...")
        
        try:
            # Add condo_id to expense
            print("Adding condo_id to expense...")
            try:
                db.session.execute(text("ALTER TABLE expense ADD COLUMN condo_id INTEGER REFERENCES condominium(id)"))
                db.session.commit()
                # Update existing
                db.session.execute(text("UPDATE expense SET condo_id = 1 WHERE condo_id IS NULL"))
                db.session.commit()
                print("  - expense updated.")
            except Exception as e:
                db.session.rollback()
                if "duplicate" in str(e) or "already exists" in str(e):
                    print("  - column condo_id already exists in expense.")
                else:
                    print(f"  - Error updating expense: {e}")

            print("Migration V2 completed successfully!")
            
        except Exception as e:
            print(f"Migration fatal error: {e}")

if __name__ == "__main__":
    migrate()

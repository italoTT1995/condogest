from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Starting Data Leakage Fix Migration V4 (Assembly)...")
        
        try:
            # Add condo_id to assembly
            print("Adding condo_id to assembly...")
            try:
                db.session.execute(text("ALTER TABLE assembly ADD COLUMN condo_id INTEGER REFERENCES condominium(id)"))
                db.session.commit()
                # Update existing
                db.session.execute(text("UPDATE assembly SET condo_id = 1 WHERE condo_id IS NULL"))
                db.session.commit()
                print("  - assembly updated.")
            except Exception as e:
                db.session.rollback()
                if "duplicate" in str(e) or "already exists" in str(e):
                    print("  - column condo_id already exists in assembly.")
                else:
                    print(f"  - Error updating assembly: {e}")

            print("Migration V4 completed successfully!")
            
        except Exception as e:
            print(f"Migration fatal error: {e}")

if __name__ == "__main__":
    migrate()

from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Starting Data Leakage Fix Migration V5 (Document)...")
        
        try:
            # Add condo_id to document
            print("Adding condo_id to document...")
            try:
                db.session.execute(text("ALTER TABLE document ADD COLUMN condo_id INTEGER REFERENCES condominium(id)"))
                db.session.commit()
                # Update existing
                db.session.execute(text("UPDATE document SET condo_id = 1 WHERE condo_id IS NULL"))
                db.session.commit()
                print("  - document updated.")
            except Exception as e:
                db.session.rollback()
                if "duplicate" in str(e) or "already exists" in str(e):
                    print("  - column condo_id already exists in document.")
                else:
                    print(f"  - Error updating document: {e}")

            print("Migration V5 completed successfully!")
            
        except Exception as e:
            print(f"Migration fatal error: {e}")

if __name__ == "__main__":
    migrate()

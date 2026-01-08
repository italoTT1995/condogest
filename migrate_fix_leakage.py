from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Starting Data Leakage Fix Migration...")
        
        try:
            # 1. Add condo_id to common_area
            print("Adding condo_id to common_area...")
            try:
                db.session.execute(text("ALTER TABLE common_area ADD COLUMN condo_id INTEGER REFERENCES condominium(id)"))
                db.session.commit()
                # Update existing
                db.session.execute(text("UPDATE common_area SET condo_id = 1 WHERE condo_id IS NULL"))
                db.session.commit()
                print("  - common_area updated.")
            except Exception as e:
                db.session.rollback()
                if "duplicate" in str(e) or "already exists" in str(e):
                    print("  - column condo_id already exists in common_area.")
                else:
                    print(f"  - Error updating common_area: {e}")

            # 2. Add condo_id to notice
            print("Adding condo_id to notice...")
            try:
                db.session.execute(text("ALTER TABLE notice ADD COLUMN condo_id INTEGER REFERENCES condominium(id)"))
                db.session.commit()
                # Update existing
                db.session.execute(text("UPDATE notice SET condo_id = 1 WHERE condo_id IS NULL"))
                db.session.commit()
                print("  - notice updated.")
            except Exception as e:
                db.session.rollback()
                if "duplicate" in str(e) or "already exists" in str(e):
                    print("  - column condo_id already exists in notice.")
                else:
                     print(f"  - Error updating notice: {e}")

            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Migration fatal error: {e}")

if __name__ == "__main__":
    migrate()

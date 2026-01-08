from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Starting Data Leakage Fix Migration V3 (VisitLog)...")
        
        try:
            # Add condo_id to visit_log
            print("Adding condo_id to visit_log...")
            try:
                db.session.execute(text("ALTER TABLE visit_log ADD COLUMN condo_id INTEGER REFERENCES condominium(id)"))
                db.session.commit()
                # Update existing - assuming mostly Condo 1, or try to infer from Unit?
                # Best effort: Infer from Unit if exists, else Default(1)
                db.session.execute(text("""
                    UPDATE visit_log 
                    SET condo_id = (SELECT condo_id FROM unit WHERE unit.id = visit_log.unit_id)
                    WHERE unit_id IS NOT NULL AND condo_id IS NULL
                """))
                db.session.execute(text("UPDATE visit_log SET condo_id = 1 WHERE condo_id IS NULL"))
                db.session.commit()
                print("  - visit_log updated.")
            except Exception as e:
                db.session.rollback()
                if "duplicate" in str(e) or "already exists" in str(e):
                    print("  - column condo_id already exists in visit_log.")
                else:
                    print(f"  - Error updating visit_log: {e}")

            print("Migration V3 completed successfully!")
            
        except Exception as e:
            print(f"Migration fatal error: {e}")

if __name__ == "__main__":
    migrate()

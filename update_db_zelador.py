from app import create_app,db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Updating Ticket and Role tables for Complaints...")
    
    with db.engine.connect() as conn:
        # 1. Update Ticket Table
        try:
            conn.execute(text("ALTER TABLE ticket ADD COLUMN category VARCHAR(20) DEFAULT 'maintenance'"))
            # Set existing tickets to maintenance
            conn.execute(text("UPDATE ticket SET category='maintenance'"))
            print("Added category to Ticket")
        except Exception as e:
            print(f"Skipped category (maybe exists): {e}")

        # 2. Update Role Table
        try:
            conn.execute(text("ALTER TABLE role ADD COLUMN can_manage_complaints BOOLEAN DEFAULT FALSE"))
            print("Added can_manage_complaints to Role")
        except Exception as e:
            print(f"Skipped can_manage_complaints (maybe exists): {e}")

        # 3. Configure Defaults
        # Admin gets everything
        conn.execute(text("UPDATE role SET can_manage_complaints=TRUE WHERE name='Admin'"))
        
        # Zelador Configuration:
        # NO Concierge (Portaria), YES Complaints (Denuncias)
        conn.execute(text("UPDATE role SET can_manage_concierge=FALSE, can_manage_complaints=TRUE WHERE name='Zelador'"))
        
        conn.commit()
    
    print("Migration complete! Zelador updated.")

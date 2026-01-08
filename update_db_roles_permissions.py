from app import create_app,db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Updating Role table with permission columns...")
    
    with db.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE role ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            print("Added is_admin")
        except Exception as e:
            print(f"Skipped is_admin (maybe exists): {e}")

        try:
            conn.execute(text("ALTER TABLE role ADD COLUMN can_manage_concierge BOOLEAN DEFAULT FALSE"))
            print("Added can_manage_concierge")
        except Exception as e:
            print(f"Skipped can_manage_concierge (maybe exists): {e}")

        try:
            conn.execute(text("ALTER TABLE role ADD COLUMN can_manage_reservations BOOLEAN DEFAULT FALSE"))
            print("Added can_manage_reservations")
        except Exception as e:
            print(f"Skipped can_manage_reservations (maybe exists): {e}")

        # Update existing Admin role to have is_admin=True
        conn.execute(text("UPDATE role SET is_admin=TRUE, can_manage_concierge=TRUE, can_manage_reservations=TRUE WHERE name='Admin'"))
        
        # Update Porteiro to have concierge access
        conn.execute(text("UPDATE role SET can_manage_concierge=TRUE WHERE name='Porteiro'"))
        
        conn.commit()
    
    print("Migration complete!")

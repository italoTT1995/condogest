from app import create_app, db
from app.models.amenity import Reservation

app = create_app()

with app.app_context():
    print("Updating 'reservation' table to include access_token...")
    # SQLite doesn't support generic ALTER COLUMN well without Alembic, so we try raw SQL if needed, 
    # but here we rely on db.create_all knowing it won't touch existing columns, 
    # actually SQLAlchemy create_all does NOT update existing tables.
    # We need to manually alter the table.
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("ALTER TABLE reservation ADD COLUMN access_token VARCHAR(100)"))
            conn.commit()
        print("Column added successfully.")
    except Exception as e:
        print(f"Migration warning (maybe column exists): {e}")

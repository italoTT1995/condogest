from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Updating 'notice' table...")
    try:
        with db.engine.connect() as conn:
            # Add image_filename column
            conn.execute(text('ALTER TABLE notice ADD COLUMN image_filename VARCHAR(255)'))
            print("- Added image_filename column")
            
            # Add is_important column (Boolean in Postgres is usually BOOLEAN or SMALLINT, SQLAlchemy maps it)
            # Standard SQL: ALTER TABLE notice ADD COLUMN is_important BOOLEAN DEFAULT FALSE
            # For Postgres specifically
            conn.execute(text('ALTER TABLE notice ADD COLUMN is_important BOOLEAN DEFAULT FALSE'))
            print("- Added is_important column")
            
            conn.commit()
        print("Table updated successfully.")
    except Exception as e:
        print(f"Migration error (columns might exist): {e}")

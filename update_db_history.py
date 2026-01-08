from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Updating 'visit_log' table...")
    try:
        with db.engine.connect() as conn:
            # Add new columns
            conn.execute(text('ALTER TABLE visit_log ADD COLUMN user_id INTEGER REFERENCES "user"(id)'))
            conn.execute(text('ALTER TABLE visit_log ADD COLUMN access_status VARCHAR(20)'))
            conn.execute(text('ALTER TABLE visit_log ADD COLUMN failure_reason VARCHAR(100)'))
            
            # Make visitor_id nullable (SQLite/Postgres syntax differs, strictly standard SQL: ALTER COLUMN ... DROP NOT NULL)
            # For Postgres:
            conn.execute(text('ALTER TABLE visit_log ALTER COLUMN visitor_id DROP NOT NULL'))
            conn.execute(text('ALTER TABLE visit_log ALTER COLUMN unit_id DROP NOT NULL'))
            
            conn.commit()
        print("Table updated successfully.")
    except Exception as e:
        print(f"Migration error: {e}")

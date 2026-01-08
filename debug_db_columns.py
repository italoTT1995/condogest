from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Checking visit_log table columns...")
    try:
        with db.engine.connect() as conn:
            # Postgres specific, but works commonly enough or triggers error if table invalid
            result = conn.execute(text("SELECT * FROM visit_log LIMIT 0"))
            print(f"Columns: {result.keys()}")
    except Exception as e:
        print(f"Error checking columns: {e}")

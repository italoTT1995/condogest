from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('user')]
    print(f"Columns in 'user' table: {columns}")
    
    if 'must_change_password' in columns:
        print("VERIFICATION SUCCESS: 'must_change_password' column exists.")
    else:
        print("VERIFICATION FAILED: Column missing.")

from app import create_app, db
from app.models.lost_found import LostItem
from app.models.user import User
from sqlalchemy import inspect
import sys
import traceback

app = create_app()

with app.app_context():
    print("--- Checking Database Tables ---")
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    
    if 'lost_item' in tables:
        print("Table 'lost_item' EXISTS.")
        columns = [c['name'] for c in inspector.get_columns('lost_item')]
        print(f"Columns: {columns}")
    else:
        print("CRITICAL: Table 'lost_item' DOES NOT EXIST.")
        
    print("\n--- Testing Query ---")
    try:
        items = LostItem.query.limit(1).all()
        print("Query successful (empty or not).")
    except Exception as e:
        print("Query FAILED:")
        traceback.print_exc()

    print("\n--- Testing User Join ---")
    try:
        # Simulate the query from the view
        # users = User.query.join(Unit).limit(1).all() # Need Unit imported
        from app.models.core import Unit
        users = User.query.join(Unit).limit(1).all()
        print("User Join Query successful.")
    except Exception as e:
        print("User Join Query FAILED:")
        traceback.print_exc()

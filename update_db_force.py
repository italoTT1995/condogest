from app import create_app, db
from app.models.lost_found import LostItem
from app.models.user import User
from app.models.condominium import Condominium

app = create_app()

with app.app_context():
    print("--- Database Configuration ---")
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    # Censoring password for safety if printing
    print(f"Target Database URI: {uri}")
    
    print("\n--- Creating Tables ---")
    try:
        db.create_all()
        print("db.create_all() executed successfully.")
        
        # Verify immediately
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'lost_item' in inspector.get_table_names():
            print("SUCCESS: 'lost_item' table verified in database.")
        else:
            print("FAILURE: 'lost_item' table still NOT found after creation.")
            
    except Exception as e:
        print(f"Error creating tables: {e}")

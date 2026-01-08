from app import create_app, db
from app.models.condominium import Condominium
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Starting Multi-Tenant Migration...")
    
    with db.engine.connect() as conn:
        # 1. Create Condominium Table
        # Using SQLAlchemy to create the table based on the model if not exists
        # But since we are modifying existing DB, let's use engine to create specific table
        if not db.inspect(db.engine).has_table("condominium"):
            print("Creating 'condominium' table...")
            db.metadata.create_all(db.engine) # This creates all missing tables, including Condominium
        else:
            print("'condominium' table already exists.")

        # 2. Add condo_id columns if they don't exist
        try:
            conn.execute(text('ALTER TABLE unit ADD COLUMN condo_id INTEGER REFERENCES condominium(id)'))
            print("Added condo_id to Unit.")
            conn.commit() # Commit immediately to save progress
        except Exception as e:
            print(f"Skipped condo_id on Unit: {e}")
            conn.rollback() # Rollback this specific error to keep connection alive

        try:
            # PostgreSQL requires quotes for reserved keyword "user"
            conn.execute(text('ALTER TABLE "user" ADD COLUMN condo_id INTEGER REFERENCES condominium(id)'))
            print("Added condo_id to User.")
            conn.commit()
        except Exception as e:
            print(f"Skipped condo_id on User: {e}")
            conn.rollback()
    
    # 3. Create Default Condominium and Migrate Data
    default_condo = Condominium.query.first()
    if not default_condo:
        print("Creating default condominium: Residencial Sunset")
        default_condo = Condominium(
            name="Residencial Sunset",
            address="Rua das Flores, 123",
            cnpj="00.000.000/0001-00"
        )
        db.session.add(default_condo)
        db.session.commit()
    else:
        print(f"Using existing default condominium: {default_condo.name}")
        
    # 4. Link Existing Data
    print("Linking existing Units and Users to default condominium...")
    
    # Using raw SQL for bulk update efficiency
    with db.engine.connect() as conn:
        conn.execute(text(f"UPDATE unit SET condo_id = {default_condo.id} WHERE condo_id IS NULL"))
        conn.execute(text(f'UPDATE "user" SET condo_id = {default_condo.id} WHERE condo_id IS NULL'))
        conn.commit()
        
    print("Migration Complete! All existing data linked to 'Residencial Sunset'.")

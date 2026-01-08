from app import create_app, db
import uuid

app = create_app()

with app.app_context():
    print("Updating 'user' table to include access_token...")
    try:
        with db.engine.connect() as conn:
            # Use double quotes for "user" table in Postgres
            conn.execute(db.text('ALTER TABLE "user" ADD COLUMN access_token VARCHAR(100)'))
            conn.commit()
        print("Column added successfully.")
    except Exception as e:
        print(f"Migration warning (maybe column exists): {e}")

    # Generate tokens for existing users
    from app.models.user import User
    users = User.query.filter_by(access_token=None).all()
    print(f"Generating tokens for {len(users)} users...")
    
    for user in users:
        user.access_token = uuid.uuid4().hex
        
    db.session.commit()
    print("Tokens generated!")

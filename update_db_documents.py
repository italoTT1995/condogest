from app import create_app, db
from app.models.documents import Document

app = create_app()

with app.app_context():
    print("Creating 'document' table...")
    db.create_all()
    print("Database updated successfully!")

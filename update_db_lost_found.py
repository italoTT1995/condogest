from app import create_app, db
from app.models.lost_found import LostItem

app = create_app()

with app.app_context():
    print("Creating table 'lost_item'...")
    db.create_all()
    print("Locked and Loaded! (Tabelas criadas ou verificadas)")

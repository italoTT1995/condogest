from app import create_app, db
from app.models.amenity import CommonArea, Reservation

app = create_app()

with app.app_context():
    print("Atualizando banco de dados com novas tabelas de Reservas...")
    db.create_all()
    print("Sucesso! Tabelas 'common_area' e 'reservation' criadas.")

from app import create_app, db
from app import create_app, db
from app.models.user import User, Role
from app.models.core import Unit, Ticket, Notice, Payment
from app.models.amenity import CommonArea, Reservation
from app.models.vehicle import Vehicle
from app.models.delivery import Delivery
from app.models.visitor import Visitor, VisitLog
from app.models.expense import Expense
from app.models.ticket_comment import TicketComment
from app.models.voting import Assembly, AgendaItem, Vote
from app.models.documents import Document
from app.models.notification import Notification
from app.models.condominium import Condominium

app = create_app()

with app.app_context():
    print("Criando tabelas do banco de dados...")
    db.create_all()
    
    if not User.query.filter_by(username='admin').first():
        print("Criando usuário administrador padrão...")
        admin = User(username='admin', email='admin@condo.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Usuário 'admin' criado com senha 'admin123'.")
    else:
        print("Usuário 'admin' já existe.")
        
    print("Database initialized successfully.")

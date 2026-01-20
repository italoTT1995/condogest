from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager

from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    # Global Rate Limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    from app.views.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.models.user import User
    from app.models.core import Unit, Ticket, Notice, Payment
    from app.models.amenity import CommonArea, Reservation
    from app.models.amenity import CommonArea, Reservation
    from app.models.vehicle import Vehicle
    from app.models.delivery import Delivery
    from app.models.lost_found import LostItem
    from app.models.visitor import VisitLog
    from app.models.condominium import Condominium
    
    with app.app_context():
        # Ensure all tables exist (fix for missing PushSubscription table on prod)
        db.create_all()
        pass # This block is likely a placeholder for future model registration or setup if needed.

    from app.views.main import main_bp
    app.register_blueprint(main_bp)

    from app.views.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.views.tickets import tickets_bp
    app.register_blueprint(tickets_bp, url_prefix='/tickets')

    from app.views.notices import notices_bp
    app.register_blueprint(notices_bp, url_prefix='/notices')

    from app.views.payments import payments_bp
    app.register_blueprint(payments_bp, url_prefix='/payments')

    from app.views.reservations import reservations_bp
    app.register_blueprint(reservations_bp, url_prefix='/reservations')

    from app.views.vehicles import vehicles_bp
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')

    from app.views.visitors import visitors_bp
    app.register_blueprint(visitors_bp, url_prefix='/visitors')

    from app.views.deliveries import deliveries_bp
    app.register_blueprint(deliveries_bp, url_prefix='/deliveries')

    from app.views.lost_found import lost_found_bp
    app.register_blueprint(lost_found_bp, url_prefix='/lost_found')

    from app.views.financial import financial_bp
    app.register_blueprint(financial_bp, url_prefix='/financial')

    from app.views.roles import roles_bp
    app.register_blueprint(roles_bp, url_prefix='/admin/roles')

    from app.views.notifications import notifications_bp
    app.register_blueprint(notifications_bp, url_prefix='/notifications')

    from app.views.assemblies import assemblies_bp
    app.register_blueprint(assemblies_bp, url_prefix='/assemblies')

    from app.views.documents import documents_bp
    app.register_blueprint(documents_bp, url_prefix='/documents')

    from app.views.access import access_bp
    app.register_blueprint(access_bp, url_prefix='/access')

    from app.views.reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')

    from app.views.condos import condos_bp
    app.register_blueprint(condos_bp, url_prefix='/condos')

    from app.views.marketplace import marketplace_bp
    app.register_blueprint(marketplace_bp, url_prefix='/marketplace')

    from app.views.services import services_bp
    app.register_blueprint(services_bp, url_prefix='/services')

    # Context Processor for Notifications
    from app.models.notification import Notification
    from flask_login import current_user
    
    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            # Assuming 'admin' in user logic means checking 'is_admin' property if using complex roles
            # But here we just fetch personal notifications.
            unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
            return dict(unread_notifications_count=unread, recent_notifications=notifs)
        return dict(unread_notifications_count=0, recent_notifications=[])

    return app

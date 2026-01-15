from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

from app.models.core import Ticket, Notice, Payment


@main_bp.route('/presentation')
def landing():
    return render_template('landing.html')

@main_bp.route('/debug/db')
def debug_db():
    from flask import current_app
    uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    # Simple masking
    return f"Active DB Connection: {uri.replace(':', '***').replace('@', ' AT ')}"

@main_bp.route('/')
@login_required
def index():
    from flask import session
    from app.models.user import User
    
    # Active Condo Filter
    condo_id = session.get('active_condo_id')
    
    if current_user.is_admin:
        # Admin sees strict silo of active condo
        ticket_count = Ticket.query.join(User).filter(User.condo_id == condo_id, Ticket.status == 'open').count()
        
    # Defensive: Payments Summary
    try:
        if current_user.is_admin:
            pending_payments = Payment.query.join(User).filter(User.condo_id == condo_id, Payment.status == 'pending').count()
            payment_amount = pending_payments # Logic seems odd in original but keeping for safety/count context
            next_payment = None
        else:
             # Payments: Show by Unit OR by User (legacy/assigned)
            if current_user.unit_id:
                payments = Payment.query.filter((Payment.unit_id == current_user.unit_id) | (Payment.user_id == current_user.id), Payment.status == 'pending').all()
            else:
                payments = Payment.query.filter_by(user_id=current_user.id, status='pending').all()
                
            payment_amount = sum(p.amount for p in payments)
            pending_payments = len(payments)
            
            if current_user.unit_id:
                next_payment = Payment.query.filter((Payment.unit_id == current_user.unit_id) | (Payment.user_id == current_user.id), Payment.status == 'pending').order_by(Payment.due_date).first()
            else:
                next_payment = Payment.query.filter_by(user_id=current_user.id, status='pending').order_by(Payment.due_date).first()
    except Exception:
        pending_payments = 0
        payment_amount = 0
        next_payment = None

    # Notices: Filter by condo of author? Or if we add condo_id to Notice? 
    # For now, let's filter by author's condo.
    recent_notices = Notice.query.join(User).filter(User.condo_id == condo_id).order_by(Notice.created_at.desc()).limit(3).all()
    
    # Chart Data
    if current_user.is_admin:
        open_tickets = Ticket.query.join(User).filter(User.condo_id == condo_id, Ticket.status == 'open').count()
        progress_tickets = Ticket.query.join(User).filter(User.condo_id == condo_id, Ticket.status == 'in_progress').count()
        closed_tickets = Ticket.query.join(User).filter(User.condo_id == condo_id, Ticket.status == 'closed').count()
    else:
        open_tickets = Ticket.query.filter_by(user_id=current_user.id, status='open').count()
        progress_tickets = Ticket.query.filter_by(user_id=current_user.id, status='in_progress').count()
        closed_tickets = Ticket.query.filter_by(user_id=current_user.id, status='closed').count()
        
    chart_data = {
        'open': open_tickets,
        'progress': progress_tickets,
        'closed': closed_tickets
    }

    # Payment stats for chart
    # Payment stats (Defensive coding for migration)
    try:
        if current_user.is_admin:
            pending_objs = Payment.query.join(User).filter(User.condo_id == condo_id, Payment.status == 'pending').all()
            paid_objs = Payment.query.join(User).filter(User.condo_id == condo_id, Payment.status == 'paid').all()
        else:
            if current_user.unit_id:
                pending_objs = Payment.query.filter((Payment.unit_id == current_user.unit_id) | (Payment.user_id == current_user.id), Payment.status == 'pending').all()
                paid_objs = Payment.query.filter((Payment.unit_id == current_user.unit_id) | (Payment.user_id == current_user.id), Payment.status == 'paid').all()
            else:
                pending_objs = Payment.query.filter_by(user_id=current_user.id, status='pending').all()
                paid_objs = Payment.query.filter_by(user_id=current_user.id, status='paid').all()
        
        payment_stats = {
            'pending_count': len(pending_objs),
            'paid_count': len(paid_objs),
            'pending_val': sum(p.amount for p in pending_objs)
        }
    except Exception as e:
        print(f"Payment Query Error (Likely Migration Needed): {e}")
        payment_stats = {
            'pending_count': 0, 'paid_count': 0, 'pending_val': 0.0
        }
        # Provide feedback to admin
        if current_user.is_admin:
             from flask import flash
             flash('AVISO CRÍTICO: Banco de dados desatualizado (Pagamentos). Execute a manutenção.', 'danger')

    # Visitor Stats (Admin, Porteiro, Síndico)
    # Check if user has permission to view visitor stats
    can_view_visitors = False
    if current_user.is_admin or current_user.is_porteiro:
        can_view_visitors = True
    elif current_user.user_role and current_user.user_role.name in ['Síndico', 'Sindico']:
        can_view_visitors = True
        
    visitor_stats = {}
    if can_view_visitors:
        from app.models.visitor import VisitLog
        from app import db
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        visits_today = VisitLog.query.filter(db.func.date(VisitLog.entry_time) == today).count()
        active_count = VisitLog.query.filter_by(exit_time=None).count()
        
        # Last 7 days flow
        labels = []
        data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_count = VisitLog.query.filter(db.func.date(VisitLog.entry_time) == day).count()
            labels.append(day.strftime('%d/%m'))
            data.append(day_count)
            
        visitor_stats = {
            'active': active_count,
            'today': visits_today,
            'labels': labels,
            'data': data
        }

    return render_template('index.html', ticket_count=ticket_count, 
                           pending_payments=pending_payments, 
                           payment_amount=payment_amount,
                           next_payment=next_payment,
                           notices=recent_notices,
                           chart_data=chart_data,
                           payment_stats=payment_stats,
                           visitor_stats=visitor_stats)

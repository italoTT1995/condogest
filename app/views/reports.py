from flask import Blueprint, render_template, request
from flask_login import login_required
from app.decorators import admin_required
from app.models.core import Payment, Unit
from app.models.user import User
from app.models.amenity import Reservation, CommonArea
from app.models.visitor import VisitLog
from app import db
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
@admin_required
def index():
    return render_template('reports/index.html')

@reports_bp.route('/financial')
@login_required
@admin_required
def financial():
    # Filter by month (default to current)
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    year, month_int = map(int, month.split('-'))
    
    # Revenue (Payments Received)
    # Assuming Payment model has 'paid_date' or we filter by due_date for simplicity
    # Ideally should be paid_date, but let's use status='paid' and due_date in that month for MVP
    start_date = datetime(year, month_int, 1).date()
    if month_int == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month_int + 1, 1).date()

    # Filter by Active Condo
    from flask import session
    from app.models.user import User
    condo_id = session.get('active_condo_id')

    received = Payment.query.filter(
        Payment.condo_id == condo_id,
        Payment.status == 'paid',
        Payment.due_date >= start_date,
        Payment.due_date < end_date
    ).all()
    
    total_received = sum(p.amount for p in received)
    
    # Pending (Delinquency)
    pending = Payment.query.filter(
        Payment.condo_id == condo_id,
        Payment.status != 'paid',
        Payment.due_date < datetime.now().date() # Overdue
    ).all()
    
    total_pending = sum(p.amount for p in pending)

    return render_template('reports/financial.html', 
                         month=month,
                         received=received,
                         total_received=total_received,
                         pending=pending,
                         total_pending=total_pending)

@reports_bp.route('/access')
@login_required
@admin_required
def access():
    from flask import session
    condo_id = session.get('active_condo_id')
    # Last 30 days by default
    logs = VisitLog.query.filter_by(condo_id=condo_id).order_by(VisitLog.entry_time.desc()).limit(100).all()
    return render_template('reports/access.html', logs=logs)

@reports_bp.route('/reservations')
@login_required
@admin_required
def reservations():
    from flask import session
    from app.models.user import User
    condo_id = session.get('active_condo_id')
    # Future and Past
    all_res = Reservation.query.join(User).filter(User.condo_id == condo_id).order_by(Reservation.date.desc()).all()
    return render_template('reports/reservations.html', reservations=all_res)

# Export Routes
import io
import csv
from flask import make_response

@reports_bp.route('/financial/export')
@login_required
@admin_required
def export_financial():
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    year, month_int = map(int, month.split('-'))
    
    start_date = datetime(year, month_int, 1).date()
    if month_int == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month_int + 1, 1).date()

    # Query Data
    # Query Data
    from flask import session
    from app.models.user import User
    condo_id = session.get('active_condo_id')

    received = Payment.query.filter(
        Payment.condo_id == condo_id,
        Payment.status == 'paid',
        Payment.due_date >= start_date,
        Payment.due_date < end_date
    ).all()
    
    pending = Payment.query.filter(
        Payment.condo_id == condo_id,
        Payment.status != 'paid',
        Payment.due_date < datetime.now().date()
    ).all()

    # Generate CSV
    si = io.StringIO()
    cw = csv.writer(si, delimiter=';') # Semicolon for Excel compatibility in BR
    
    cw.writerow(['Tipo', 'Morador', 'Unidade', 'Descricao', 'Valor', 'Data'])
    
    for p in received:
        unit = f"{p.unit.block}-{p.unit.number}" if p.unit else "N/A"
        cw.writerow(['Recebido', p.user.username if p.user else 'Desconhecido', unit, p.description, 
                     f"R$ {p.amount:.2f}", p.due_date.strftime('%d/%m/%Y')])

    for p in pending:
        unit = f"{p.unit.block}-{p.unit.number}" if p.unit else "N/A"
        cw.writerow(['Pendente', p.user.username if p.user else 'Desconhecido', unit, p.description, 
                     f"R$ {p.amount:.2f}", p.due_date.strftime('%d/%m/%Y')])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=financeiro_{month}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@reports_bp.route('/access/export')
@login_required
@admin_required
def export_access():
    from flask import session
    condo_id = session.get('active_condo_id')
    logs = VisitLog.query.filter_by(condo_id=condo_id).order_by(VisitLog.entry_time.desc()).limit(500).all() # Limit for safety

    si = io.StringIO()
    cw = csv.writer(si, delimiter=';')
    cw.writerow(['Data Entrada', 'Hora Entrada', 'Tipo', 'Nome', 'Documento', 'Destino', 'Status', 'Hora Saida'])

    for log in logs:
        tipo = 'Visitante' if log.visitor else 'Morador'
        nome = log.visitor.name if log.visitor else (log.user.username if log.user else 'Desconhecido')
        doc = log.visitor.cpf if log.visitor else '-'
        destino = f"{log.unit.block}-{log.unit.number}" if log.unit else '-'
        
        saida = log.exit_time.strftime('%H:%M') if log.exit_time else '-'
        
        cw.writerow([
            log.entry_time.strftime('%d/%m/%Y'),
            log.entry_time.strftime('%H:%M'),
            tipo, nome, doc, destino, 
            log.access_status, saida
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=acessos.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@reports_bp.route('/reservations/export')
@login_required
@admin_required
def export_reservations():
    from flask import session
    from app.models.user import User
    condo_id = session.get('active_condo_id')
    res_list = Reservation.query.join(User).filter(User.condo_id == condo_id).order_by(Reservation.date.desc()).all()

    si = io.StringIO()
    cw = csv.writer(si, delimiter=';')
    cw.writerow(['Data', 'Area', 'Morador', 'Unidade', 'Horario', 'Status'])

    for r in res_list:
        area = r.area.name if r.area else 'Area Removida'
        unidade = f"{r.resident.unit.block}-{r.resident.unit.number}" if r.resident.unit else '-'
        
        cw.writerow([
            r.date.strftime('%d/%m/%Y'),
            area,
            r.resident.username,
            unidade,
            f"{r.start_time.strftime('%H:%M')} - {r.end_time.strftime('%H:%M')}",
            r.status
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=reservas.csv"
    output.headers["Content-type"] = "text/csv"
    return output

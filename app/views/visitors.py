from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.visitor import Visitor, VisitLog
from app.models.core import Unit
from datetime import datetime

visitors_bp = Blueprint('visitors', __name__)

@visitors_bp.route('/')
@login_required
def index():
    from flask import session
    condo_id = session.get('active_condo_id')
    
    try:
        if condo_id:
            # Filtrar por condomínio específico
            active_visits = VisitLog.query.filter_by(condo_id=condo_id, status='active').filter(VisitLog.exit_time == None).order_by(VisitLog.entry_time.desc()).all()
            scheduled_visits = VisitLog.query.filter_by(condo_id=condo_id, status='scheduled').order_by(VisitLog.expected_arrival).all()
            history_visits = VisitLog.query.filter(VisitLog.condo_id == condo_id, VisitLog.exit_time != None).order_by(VisitLog.entry_time.desc()).limit(50).all()
        else:
            # Fallback: mostrar todas as visitas se condo_id não estiver na sessão
            active_visits = VisitLog.query.filter_by(status='active').filter(VisitLog.exit_time == None).order_by(VisitLog.entry_time.desc()).all()
            scheduled_visits = VisitLog.query.filter_by(status='scheduled').order_by(VisitLog.expected_arrival).all()
            history_visits = VisitLog.query.filter(VisitLog.exit_time != None).order_by(VisitLog.entry_time.desc()).limit(50).all()
    except Exception as e:
        # Fallback se colunas novas não existirem (ex: status, condo_id)
        try:
            active_visits = VisitLog.query.filter(VisitLog.exit_time == None).order_by(VisitLog.entry_time.desc()).all()
        except:
            active_visits = []
        scheduled_visits = []
        history_visits = []
        flash(f'Aviso: banco de dados pode precisar de atualização. ({str(e)[:80]})', 'warning')

    today = datetime.now().date()
    try:
        visits_today = VisitLog.query.filter(
            db.func.date(VisitLog.entry_time) == today
        ).count()
    except:
        visits_today = 0
    
    active_count = len(active_visits)
    scheduled_count = len(scheduled_visits)
    
    return render_template('visitors/index.html', 
                           active_visits=active_visits, 
                           history_visits=history_visits,
                           scheduled_visits=scheduled_visits,
                           stats={
                               'active': active_count,
                               'today': visits_today,
                               'scheduled': scheduled_count
                           })


@visitors_bp.route('/activate/<int:id>', methods=['POST'])
@login_required
def activate_visit(id):
    visit = VisitLog.query.get_or_404(id)
    
    # Permission: Admin or Porteiro (or anyone who can_register_visits)
    if not current_user.can_register_visits:
         flash('Acesso negado.', 'danger')
         return redirect(url_for('visitors.index'))

    visit.status = 'active'
    visit.entry_time = datetime.now()
    db.session.commit()
    flash('Entrada confirmada com sucesso!', 'success')
    return redirect(url_for('visitors.index'))

@visitors_bp.route('/new_visit', methods=['GET', 'POST'])
@login_required
def new_visit():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        name = request.form.get('name')
        unit_id = request.form.get('unit_id')
        observation = request.form.get('observation')
        
        if not unit_id:
            flash('Unidade de destino é obrigatória.', 'danger')
            return redirect(url_for('visitors.new_visit'))
            
        # 1. Find or Create Visitor
        visitor = Visitor.query.filter_by(cpf=cpf).first()
        if not visitor:
            if not name:
                flash('Nome é obrigatório para um novo visitante.', 'danger')
                return redirect(url_for('visitors.new_visit'))
            visitor = Visitor(name=name, cpf=cpf)
            db.session.add(visitor)
            db.session.commit() # Commit to get ID
        
        # 2. Log Entry
        try:
            from flask import session
            condo_id = session.get('active_condo_id')
            new_log = VisitLog(
                visitor_id=visitor.id,
                unit_id=int(unit_id),
                observation=observation,
                condo_id=condo_id,
                entry_time=datetime.now(),
                status='active'  # Explícito para garantir que aparece na listagem
            )
            db.session.add(new_log)
            db.session.commit()
            flash('Entrada registrada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar entrada: {str(e)}', 'danger')
            return redirect(url_for('visitors.new_visit'))
        return redirect(url_for('visitors.index'))


    # GET: Show form
    from flask import session
    units = Unit.query.filter_by(condo_id=session.get('active_condo_id')).order_by(Unit.block, Unit.number).all()
    return render_template('visitors/form.html', units=units)

@visitors_bp.route('/exit/<int:log_id>', methods=['POST'])
@login_required
def log_exit(log_id):
    visit = VisitLog.query.get_or_404(log_id)
    visit.exit_time = datetime.now()
    db.session.commit()
    flash('Saída registrada.', 'info')
    return redirect(url_for('visitors.index'))

@visitors_bp.route('/search_visitor')
@login_required
def search_visitor():
    cpf = request.args.get('cpf')
    visitor = Visitor.query.filter_by(cpf=cpf).first()
    if visitor:
        return {'found': True, 'name': visitor.name, 'cpf': visitor.cpf}
    return {'found': False}

@visitors_bp.route('/my_guests')
@login_required
def my_guests():
    # Resident only view of their expected visitors
    if not current_user.unit_id and not current_user.is_admin:
        flash('Você não está vinculado a uma unidade.', 'danger')
        return redirect(url_for('main.index'))
        
    # Get scheduled visits for my unit
    # Logic: Status is 'scheduled' AND (unit_id matches OR scheduled_by matches)
    # We'll rely on scheduled_by for precision if multiple people in unit.
    scheduled_visits = VisitLog.query.filter_by(
        scheduled_by=current_user.id, 
        status='scheduled'
    ).order_by(VisitLog.expected_arrival).all()
    
    return render_template('visitors/my_guests.html', scheduled_visits=scheduled_visits)

@visitors_bp.route('/pre_authorize', methods=['POST'])
@login_required
def pre_authorize():
    name = request.form.get('name')
    cpf = request.form.get('cpf')
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    
    if not name or not date_str:
        flash('Nome e Data são obrigatórios.', 'danger')
        return redirect(url_for('visitors.my_guests'))
        
    try:
        arrival_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
    except ValueError:
        arrival_dt = datetime.strptime(f"{date_str}", '%Y-%m-%d') # Default to midnight or handle error
        
    # Find or Create Visitor
    visitor = Visitor.query.filter_by(cpf=cpf).first() if cpf else None
    if not visitor and cpf:
         visitor = Visitor(name=name, cpf=cpf)
         db.session.add(visitor)
         db.session.commit()
    elif not visitor and not cpf:
         # Create visitor without CPF? Allowed for pre-auth? 
         # Maybe require CPF for security, or generate a placeholder.
         # For now, require CPF or reuse existing name logic if strict.
         # Let's allow name-only for "Family" but better to ask CPF.
         flash('CPF é recomendado para segurança, mas salvamos apenas com o nome.', 'warning')
         visitor = Visitor(name=name, cpf=f"TEMP_{datetime.now().timestamp()}") # Hack if CPF mandatory
         db.session.add(visitor)
         db.session.commit()

    # Create Scheduled Log
    from flask import session
    condo_id = session.get('active_condo_id') or current_user.condo_id
    
    log = VisitLog(
        visitor_id=visitor.id,
        unit_id=current_user.unit_id,
        expected_arrival=arrival_dt,
        status='scheduled',
        scheduled_by=current_user.id,
        condo_id=condo_id,  # ← ESSENCIAL para o porteiro encontrar a visita
        entry_time=None
    )
    db.session.add(log)
    db.session.commit()
    flash('Visitante pré-autorizado com sucesso!', 'success')

    return redirect(url_for('visitors.my_guests'))

@visitors_bp.route('/cancel_visit/<int:id>', methods=['POST'])
@login_required
def cancel_visit(id):
    log = VisitLog.query.get_or_404(id)
    if log.scheduled_by != current_user.id and not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('visitors.my_guests'))
        
    db.session.delete(log)
    db.session.commit()
    flash('Autorização cancelada.', 'info')
    return redirect(url_for('visitors.my_guests'))

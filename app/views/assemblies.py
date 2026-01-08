from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.voting import Assembly, AgendaItem, Vote, Attendance
from app.models.core import Unit
from app import db
from datetime import datetime

assemblies_bp = Blueprint('assemblies', __name__)

@assemblies_bp.route('/')
@login_required
def index():
    from flask import session
    condo_id = session.get('active_condo_id')
    assemblies = Assembly.query.filter_by(condo_id=condo_id).order_by(Assembly.start_time.desc()).all()
    return render_template('assemblies/index.html', assemblies=assemblies)

@assemblies_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.')
        return redirect(url_for('assemblies.index'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_time_str = request.form['start_time']
        
        # Simple format parsing (adjust format based on input type datetime-local)
        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Formato de data inválido.')
            return redirect(url_for('assemblies.create'))

        from flask import session
        condo_id = session.get('active_condo_id')
        assembly = Assembly(
            title=title, 
            description=description, 
            start_time=start_time,
            condo_id=condo_id
        )
        db.session.add(assembly)
        db.session.commit()
        
        flash('Assembleia agendada com sucesso! Adicione as pautas agora.')
        return redirect(url_for('assemblies.details', id=assembly.id))
        
    return render_template('assemblies/create.html')

@assemblies_bp.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def details(id):
    assembly = Assembly.query.get_or_404(id)
    
    # Logic to add agenda items if admin
    if request.method == 'POST' and current_user.is_admin:
        if 'add_item' in request.form:
            item_title = request.form['item_title']
            item_desc = request.form['item_desc']
            new_item = AgendaItem(title=item_title, description=item_desc, assembly_id=assembly.id)
            db.session.add(new_item)
            db.session.commit()
            flash('Pauta adicionada.')
            
        elif 'toggle_status' in request.form:
            new_status = request.form['status']
            assembly.status = new_status
            db.session.commit()
            flash(f'Status alterado para {new_status}.')
            
    # Check if user attended
    attendance = Attendance.query.filter_by(assembly_id=assembly.id, user_id=current_user.id).first()
    
    # Calculate Quorum (Unique Units)
    unique_units_count = db.session.query(Attendance.unit_id).filter_by(assembly_id=assembly.id).distinct().count()
    
    # Filter Total Units by Condo ID of the Assembly
    total_units = Unit.query.filter_by(condo_id=assembly.condo_id).count() 
    quorum_percentage = (unique_units_count / total_units * 100) if total_units > 0 else 0
    
    # Get user votes for this assembly to show what they voted
    user_votes = {}
    if attendance:
        votes = Vote.query.filter(Vote.agenda_item_id.in_([i.id for i in assembly.items]), Vote.user_id == current_user.id).all()
        user_votes = {v.agenda_item_id: v.choice for v in votes}

    # Admin Reporting Data
    attendance_list = []
    item_results = {}
    detailed_votes = {}
    
    if current_user.is_admin:
        # Full attendance list
        attendance_list = Attendance.query.filter_by(assembly_id=assembly.id).order_by(Attendance.timestamp.desc()).all()
        
        # Vote Calculations
        for item in assembly.items:
            # Aggregate counts
            yes_count = Vote.query.filter_by(agenda_item_id=item.id, choice='yes').count()
            no_count = Vote.query.filter_by(agenda_item_id=item.id, choice='no').count()
            abs_count = Vote.query.filter_by(agenda_item_id=item.id, choice='abstain').count()
            
            item_results[item.id] = {
                'yes': yes_count,
                'no': no_count,
                'abstain': abs_count,
                'total': yes_count + no_count + abs_count
            }
            
            # Detailed Log
            detailed_votes[item.id] = Vote.query.filter_by(agenda_item_id=item.id).all()

    return render_template('assemblies/details.html', 
                           assembly=assembly, 
                           attendance=attendance, 
                           unique_units_count=unique_units_count,
                           quorum_percentage=int(quorum_percentage),
                           user_votes=user_votes,
                           attendance_list=attendance_list,
                           item_results=item_results,
                           detailed_votes=detailed_votes)

@assemblies_bp.route('/<int:id>/check_in', methods=['POST'])
@login_required
def check_in(id):
    assembly = Assembly.query.get_or_404(id)
    if assembly.status == 'closed':
        flash('Assembleia já encerrada.')
        return redirect(url_for('assemblies.details', id=id))

    # Check if unit is assigned
    if not current_user.unit:
        flash('Erro: Você não está vinculado a uma unidade. Contate o admin.', 'danger')
        return redirect(url_for('assemblies.details', id=id))

    # Check already present
    exists = Attendance.query.filter_by(assembly_id=id, user_id=current_user.id).first()
    if not exists:
        att = Attendance(assembly_id=id, user_id=current_user.id, unit_id=current_user.unit.id)
        db.session.add(att)
        db.session.commit()
        flash('Presença confirmada! Bem-vindo à sala virtual.')
    else:
        flash('Você já marcou presença.')
        
    return redirect(url_for('assemblies.details', id=id))

@assemblies_bp.route('/vote/<int:item_id>', methods=['POST'])
@login_required
def vote(item_id):
    item = AgendaItem.query.get_or_404(item_id)
    assembly = item.assembly
    
    if assembly.status != 'open':
        flash('Votação não está aberta.', 'danger')
        return redirect(url_for('assemblies.details', id=assembly.id))
        
    # Check attendance
    if not Attendance.query.filter_by(assembly_id=assembly.id, user_id=current_user.id).first():
        flash('Você precisa marcar presença antes de votar.', 'warning')
        return redirect(url_for('assemblies.details', id=assembly.id))

    # Check One Vote Per Unit Logic
    # We allow the same user to change vote? No, usually vote is final.
    # We check if *any* user from this unit has voted on this item.
    
    existing_vote = Vote.query.filter_by(agenda_item_id=item.id, unit_id=current_user.unit.id).first()
    
    if existing_vote:
        # If it's the same user, maybe allow change? Or strict no?
        # Let's be strict: One vote per unit, period.
        flash(f'Voto já registrado para a unidade {current_user.unit}.', 'danger')
        return redirect(url_for('assemblies.details', id=assembly.id))
        
    choice = request.form['choice']
    if choice not in ['yes', 'no', 'abstain']:
         flash('Opção inválida.', 'danger')
         return redirect(url_for('assemblies.details', id=assembly.id))
         
    vote = Vote(agenda_item_id=item.id, user_id=current_user.id, unit_id=current_user.unit.id, choice=choice)
    db.session.add(vote)
    db.session.commit()
    
    flash('Voto computado com sucesso!', 'success')
    return redirect(url_for('assemblies.details', id=assembly.id))

@assemblies_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('assemblies.index'))
        
    assembly = Assembly.query.get_or_404(id)
    db.session.delete(assembly)
    db.session.commit()
    
    flash('Assembleia excluída com sucesso.', 'success')
    return redirect(url_for('assemblies.index'))

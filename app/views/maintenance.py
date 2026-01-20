from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date
from app.models.maintenance import MaintenanceTask
from app import db

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/')
@login_required
def index():
    if not (current_user.is_admin or current_user.is_zelador or current_user.is_sindico):
        flash('Acesso restrito à administração.', 'warning')
        return redirect(url_for('main.index'))
        
    from flask import session
    condo_id = session.get('active_condo_id')
    
    # Fetch tasks
    tasks = MaintenanceTask.query.filter_by(condo_id=condo_id).order_by(MaintenanceTask.due_date).all()
    
    # Simple stats/grouping
    today = date.today()
    overdue = [t for t in tasks if t.status != 'completed' and t.due_date < today]
    pending = [t for t in tasks if t.status != 'completed' and t.due_date >= today]
    completed = [t for t in tasks if t.status == 'completed']
    
    return render_template('maintenance/index.html', overdue=overdue, pending=pending, completed=completed, today=today)

@maintenance_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not (current_user.is_admin or current_user.is_zelador or current_user.is_sindico):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'danger')
            return redirect(url_for('maintenance.new'))
            
        from flask import session
        condo_id = session.get('active_condo_id')
        
        task = MaintenanceTask(
            title=title,
            description=description,
            due_date=due_date,
            condo_id=condo_id,
            status='pending'
        )
        
        db.session.add(task)
        db.session.commit()
        flash('Tarefa de manutenção criada!', 'success')
        return redirect(url_for('maintenance.index'))
        
    return render_template('maintenance/form.html')

@maintenance_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    if not (current_user.is_admin or current_user.is_zelador):
         return redirect(url_for('main.index'))
         
    task = MaintenanceTask.query.get_or_404(id)
    task.status = 'completed'
    db.session.commit()
    flash('Tarefa marcada como concluída.', 'success')
    return redirect(url_for('maintenance.index'))

@maintenance_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        flash('Apenas administradores podem excluir tarefas.', 'danger')
        return redirect(url_for('maintenance.index'))
        
    task = MaintenanceTask.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Tarefa removida.', 'success')
    return redirect(url_for('maintenance.index'))

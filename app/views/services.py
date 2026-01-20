from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.service import ServiceProvider
from app import db

services_bp = Blueprint('services', __name__, url_prefix='/services')

@services_bp.route('/')
@login_required
def index():
    if not current_user.is_resident:
         flash('Acesso exclusivo para moradores.', 'warning')
         return redirect(url_for('main.index'))
         
    # List my active/inactive providers
    providers = ServiceProvider.query.filter_by(user_id=current_user.id).order_by(ServiceProvider.name).all()
    
    return render_template('services/my_providers.html', providers=providers)

@services_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        cpf = request.form.get('cpf')
        
        # Days handling (Checkboxes)
        days = request.form.getlist('days') # ['Mon', 'Fri']
        allowed_days_str = ",".join(days)
        
        from flask import session
        condo_id = session.get('active_condo_id')
        
        provider = ServiceProvider(
            name=name,
            role=role,
            cpf=cpf,
            allowed_days=allowed_days_str,
            user_id=current_user.id,
            unit_id=current_user.unit_id,
            condo_id=condo_id
        )
        
        db.session.add(provider)
        db.session.commit()
        flash('Prestador cadastrado com sucesso!', 'success')
        return redirect(url_for('services.index'))
        
    return render_template('services/form.html')

@services_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    provider = ServiceProvider.query.get_or_404(id)
    
    if provider.user_id != current_user.id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('services.index'))
        
    db.session.delete(provider)
    db.session.commit()
    flash('Prestador removido.', 'success')
    return redirect(url_for('services.index'))

@services_bp.route('/search')
@login_required
def search():
    # View for Porteiro/Admin to check authorized providers
    if not (current_user.is_porteiro or current_user.is_admin or current_user.is_zelador):
         flash('Acesso restrito.', 'danger')
         return redirect(url_for('main.index'))
         
    from flask import session
    condo_id = session.get('active_condo_id')
    
    query = request.args.get('q')
    providers = []
    
    if query:
        # Search by Name or Unit (Block-Number)
        from app.models.core import Unit
        providers = ServiceProvider.query.join(Unit).filter(
            ServiceProvider.condo_id == condo_id,
            (ServiceProvider.name.ilike(f'%{query}%')) | 
            (Unit.block.ilike(f'%{query}%')) | 
            (Unit.number.ilike(f'%{query}%'))
        ).all()
    else:
        # Just show recent ones or none? Maybe none to keep UI clean.
        pass
        
    return render_template('services/search.html', providers=providers, query=query)

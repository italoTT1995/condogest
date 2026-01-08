from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import Role
from app.decorators import admin_required, superuser_required

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/')
@login_required
@superuser_required
def index():
    roles = Role.query.order_by(Role.name).all()
    return render_template('admin/roles/index.html', roles=roles)

@roles_bp.route('/create', methods=['GET', 'POST'])
@login_required
@superuser_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if Role.query.filter_by(name=name).first():
            flash('Uma função com este nome já existe.', 'danger')
        else:
            role = Role(
                name=name, 
                description=description,
                is_admin = 'is_admin' in request.form,
                can_manage_concierge = 'can_manage_concierge' in request.form,
                can_manage_reservations = 'can_manage_reservations' in request.form
            )
            db.session.add(role)
            db.session.commit()
            flash('Função criada com sucesso!', 'success')
            return redirect(url_for('roles.index'))
            
    return render_template('admin/roles/form.html', title="Nova Função")

@roles_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@superuser_required
def edit(id):
    role = Role.query.get_or_404(id)
    if request.method == 'POST':
        role.name = request.form.get('name')
        role.description = request.form.get('description')
        role.is_admin = 'is_admin' in request.form
        role.can_manage_concierge = 'can_manage_concierge' in request.form
        role.can_manage_reservations = 'can_manage_reservations' in request.form
        db.session.commit()
        flash('Função atualizada com sucesso!', 'success')
        return redirect(url_for('roles.index'))
        
    return render_template('admin/roles/form.html', title="Editar Função", role=role)

@roles_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@superuser_required
def delete(id):
    role = Role.query.get_or_404(id)
    # Prevent deleting critical roles
    if role.name in ['Admin', 'Morador']:
        flash('Não é permitido excluir as funções padrão do sistema.', 'warning')
    elif role.users:
        flash('Não é possível excluir uma função que possui usuários vinculados.', 'danger')
    else:
        db.session.delete(role)
        db.session.commit()
        flash('Função removida com sucesso!', 'success')
        
    return redirect(url_for('roles.index'))

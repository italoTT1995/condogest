from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models.user import User, Role
from app.models.core import Unit
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    from flask import session
    condo_id = session.get('active_condo_id')
    
    users = User.query.filter_by(condo_id=condo_id).all()
    units = Unit.query.filter_by(condo_id=condo_id).all()
    return render_template('admin/dashboard.html', users=users, units=units)

@admin_bp.route('/user/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    from flask import session
    condo_id = session.get('active_condo_id')
    units = Unit.query.filter_by(condo_id=condo_id).all()
    # Logic to filter roles: Only Superuser (Admin) can create other Admins
    if current_user.is_superuser:
        roles = Role.query.all()
    else:
        roles = Role.query.filter(Role.name != 'Admin').all()
        
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpf = request.form.get('cpf')
        role_id = request.form['role_id'] # ID of the selected role
        unit_id = request.form.get('unit_id')
        
        if User.query.filter_by(username=username).first():
            flash('Este nome de usuário já existe no sistema global. Por favor, escolha outro (ex: porteiro.bloco1).', 'warning')
            return redirect(url_for('admin.create_user'))
            
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado no sistema global. Use um email único.', 'warning')
            return redirect(url_for('admin.create_user'))
        
        if cpf:
            existing_cpf = User.query.filter_by(cpf=cpf).first()
            if existing_cpf:
                flash('Este CPF já está cadastrado no sistema.', 'warning')
                return redirect(url_for('admin.create_user'))
        
        # Determine legacy role string for compatibility
        selected_role = Role.query.get(role_id)
        
        # Security Check: Prevent non-superusers from creating Admins
        if selected_role.name == 'Admin' and not current_user.is_superuser:
             flash('Você não tem permissão para criar administradores.', 'danger')
             return redirect(url_for('admin.create_user'))

        legacy_role_str = 'admin' if selected_role.name == 'Admin' else 'resident'

        user = User(username=username, email=email, cpf=cpf, role=legacy_role_str, role_id=role_id)
        user.set_password(password)
        
        if 'must_change_password' in request.form:
            user.must_change_password = True
            
        if unit_id:
            user.unit_id = int(unit_id)
            
        from flask import session
        user.condo_id = session.get('active_condo_id')
            
        db.session.add(user)
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/create_user.html', units=units, roles=roles)

@admin_bp.route('/unit/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_unit():
    if request.method == 'POST':
        block = request.form['block']
        number = request.form['number']
        
        from flask import session
        unit = Unit(block=block, number=number, condo_id=session.get('active_condo_id'))
        db.session.add(unit)
        db.session.commit()
        flash('Unidade criada com sucesso!')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/create_unit.html')

@admin_bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    # Security Check: Non-superusers cannot edit Admins (to prevent account takeover)
    if user.is_superuser and not current_user.is_superuser:
        flash('Você não tem permissão para editar este usuário.', 'danger')
        return redirect(url_for('admin.dashboard'))

    from flask import session
    condo_id = session.get('active_condo_id')
    units = Unit.query.filter_by(condo_id=condo_id).all()
    
    if current_user.is_superuser:
        roles = Role.query.all()
    else:
        roles = Role.query.filter(Role.name != 'Admin').all()

    if request.method == 'POST':
        user.username = request.form['username']
        email = request.form['email']
        cpf = request.form.get('cpf')
        
        # Check if email is being used by another user
        existing_email_user = User.query.filter_by(email=email).first()
        if existing_email_user and existing_email_user.id != user.id:
            flash('Este email já está em uso por outro usuário.', 'warning')
            return redirect(url_for('admin.edit_user', id=user.id))
            
        user.email = email
        
        # Check CPF
        if cpf:
            existing_cpf_user = User.query.filter_by(cpf=cpf).first()
            if existing_cpf_user and existing_cpf_user.id != user.id:
                flash('Este CPF já está cadastrado para outro usuário.', 'warning')
                return redirect(url_for('admin.edit_user', id=user.id))
            user.cpf = cpf
        else:
            user.cpf = None
        
        # Update Role
        role_id = request.form['role_id']
        selected_role = Role.query.get(role_id)
        
        # Security Check: Prevent assigning Admin role if not superuser
        if selected_role.name == 'Admin' and not current_user.is_superuser:
            flash('Você não tem permissão para promover usuários a Administrador.', 'danger')
            return redirect(url_for('admin.edit_user', id=user.id))
            
        user.role_id = role_id
        user.role = 'admin' if selected_role.name == 'Admin' else 'resident'
        
        unit_id = request.form.get('unit_id')
        if unit_id:
            user.unit_id = int(unit_id)
        else:
            user.unit_id = None
            
        if request.form.get('password'):
            user.set_password(request.form['password'])
            
        # Update Reset Flag (Checkbox present = True, absent = False) - Wait, switch sends 'on' or nothing.
        user.must_change_password = 'must_change_password' in request.form
            
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/edit_user.html', user=user, units=units, roles=roles)

@admin_bp.route('/unit/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_unit(id):
    unit = Unit.query.get_or_404(id)
    if request.method == 'POST':
        unit.block = request.form['block']
        unit.number = request.form['number']
        unit.status = request.form['status']
        
        db.session.commit()
        flash('Unidade atualizada com sucesso!')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/edit_unit.html', unit=unit)

@admin_bp.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Você não pode excluir a si mesmo!')
        return redirect(url_for('admin.dashboard'))
        
    if user.username == 'admin':
        flash('O administrador principal não pode ser excluído.')
        return redirect(url_for('admin.dashboard'))
        
    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído com sucesso.')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/unit/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_unit(id):
    unit = Unit.query.get_or_404(id)
    # Check if there are residents? Maybe warning? For now just delete.
    db.session.delete(unit)
    db.session.commit()
    flash('Unidade excluída com sucesso.')
    return redirect(url_for('admin.dashboard'))

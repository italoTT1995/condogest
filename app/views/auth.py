from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User
from app import db
import os
from werkzeug.utils import secure_filename
import uuid


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username'].strip().lower() # Normalize input (mobile friendly)
        password = request.form['password']
        # Try finding by lowercase username. 
        # Note: If database has mixed case usernames, this might need logic tweak, 
        # but for 'admin' and standard usernames, lowercase is safer convention.
        user = User.query.filter(User.username.ilike(username)).first()
        
        from datetime import datetime
        
        # Check Account Lockout
        if user and user.locked_until:
             if user.locked_until > datetime.now():
                 wait_minutes = int((user.locked_until - datetime.now()).total_seconds() / 60) + 1
                 flash(f'Conta bloqueada. Tente novamente em {wait_minutes} minutos.', 'danger')
                 return render_template('auth/login.html')
             else:
                 # Lock expired, reset
                 user.locked_until = None
                 user.failed_login_attempts = 0
                 db.session.commit()
        
        if user is None or not user.check_password(password):
            if user:
                from datetime import timedelta
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.now() + timedelta(minutes=15)
                    flash('Conta bloqueada por 15 minutos devido a múltiplas tentativas falhas.', 'danger')
                else:
                    flash(f'Credenciais inválidas. Tentativa {user.failed_login_attempts}/5.', 'warning')
                db.session.commit()
            else:
                 flash('Credenciais inválidas.', 'warning')
                 
            return redirect(url_for('auth.login'))
        
        # Login Successful
        if user.must_change_password:
             login_user(user)
             flash('Por segurança, você deve alterar sua senha antes de continuar.', 'info')
             return redirect(url_for('auth.change_password'))

        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
        
        login_user(user)
        
        # Set Active Condo Context
        from flask import session
        if user.condominium:
            session['active_condo_id'] = user.condo_id
            session['active_condo_name'] = user.condominium.name
        else:
            # Fallback for old users or error state
            session['active_condo_id'] = 1
            session['active_condo_name'] = 'Residencial Sunset'
            
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('auth.change_password'))
            
        if len(password) < 6:
            flash('A senha deve ter no mínimo 6 caracteres.', 'warning')
            return redirect(url_for('auth.change_password'))
            
        current_user.set_password(password)
        current_user.must_change_password = False
        current_user.failed_login_attempts = 0
        current_user.locked_until = None
        db.session.commit()
        
        flash('Senha alterada com sucesso! Bem-vindo.', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('auth/change_password.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Update text fields
        if 'full_name' in request.form:
             current_user.full_name = request.form['full_name']
        if 'contact' in request.form:
             current_user.contact = request.form['contact']
             
        # Handle Image Upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
                new_filename = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
                
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
                file.save(os.path.join(upload_path, new_filename))
                
                # Delete old image if not default? (Optional enhancement)
                current_user.profile_image = new_filename
                
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html')

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.models.user import User
from app.models.core import Payment
from app.models.visitor import VisitLog
from app import db
import qrcode
from io import BytesIO
from datetime import datetime

access_bp = Blueprint('access', __name__)

@access_bp.route('/my_badge')
@login_required
def my_badge():
    # Ensure user has a token
    if not current_user.access_token:
        import uuid
        current_user.access_token = uuid.uuid4().hex
        db.session.commit()
        
    return render_template('access/badge.html', user=current_user)

@access_bp.route('/qr/<int:user_id>')
@login_required
def qr_image(user_id):
    user = User.query.get_or_404(user_id)
    
    # Security: User can see own, Admin/Porteiro can see all
    if user.id != current_user.id and not (current_user.is_admin or current_user.is_porteiro):
        return "Acesso negado", 403
        
    if not user.access_token:
        return "Token não gerado", 404
        
    img = qrcode.make(user.access_token)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

@access_bp.route('/scan')
@login_required
def scan():
    if not (current_user.is_admin or current_user.is_porteiro):
         flash('Acesso restrito.', 'danger')
         return redirect(url_for('main.index'))
    return render_template('access/scan.html')

@access_bp.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    if not (current_user.is_admin or current_user.is_porteiro):
         flash('Acesso restrito.', 'danger')
         return redirect(url_for('main.index'))

    token = request.args.get('token') or request.form.get('token')
    if not token:
        flash('Token inválido.', 'danger')
        return redirect(url_for('access.scan'))
        
    user = User.query.filter_by(access_token=token).first()
    
    status = 'denied'
    message = 'Token não encontrado.'
    failure_reason = 'invalid_token'
    
    if user:
        # 0. Anti-Passback Check (prevent double entry in < 60s)
        last_success = VisitLog.query.filter_by(user_id=user.id, access_status='allowed')\
            .order_by(VisitLog.entry_time.desc()).first()
            
        if last_success:
            time_diff = (datetime.now() - last_success.entry_time).total_seconds()
            if time_diff < 60:
                # Block double entry
                status = 'denied'
                message = f'Acesso Duplo Bloqueado. Aguarde {int(60 - time_diff)}s.'
                failure_reason = 'Bloqueio: Acesso Duplo (60s)'
                
                # Log the blocked attempt
                log = VisitLog(
                    user_id=user.id,
                    unit_id=user.unit_id,
                    entry_time=datetime.now(),
                    access_status=status,
                    failure_reason=failure_reason
                )
                db.session.add(log)
                db.session.commit()
                
                return render_template('access/result.html', status=status, message=message, user_data=user)

        # 1. Check Financial Status - REMOVED AS REQUESTED
        # (Former logic checked for overdue payments here)

        if not user.is_active: 
             # Simple ban check placeholder (currently defaults to allowed)
             status = 'allowed' 
             message = 'Acesso Autorizado.'
             failure_reason = None
        else:
            status = 'allowed'
            message = 'Acesso Autorizado.'
            failure_reason = None
        elif not user.is_active: # Assuming is_active property exists or logic needs to be added
             # Simple ban check placeholder
             status = 'allowed' # default allowed if no explicit ban logic yet
             message = 'Acesso Autorizado.'
             failure_reason = None
        else:
            status = 'allowed'
            message = 'Acesso Autorizado.'
            failure_reason = None
            
        # 2. Log Access
        log = VisitLog(
            user_id=user.id,
            unit_id=user.unit_id,
            entry_time=datetime.now(),
            access_status=status,
            failure_reason=failure_reason
        )
        db.session.add(log)
        db.session.commit()
            
    return render_template('access/result.html', status=status, message=message, user_data=user)

@access_bp.route('/history')
@login_required
def history():
    if not (current_user.is_admin or current_user.is_porteiro):
        flash('Acesso restrito.')
        return redirect(url_for('main.index'))
        
    # Fetch logs (Residents + Visitors mixed? For now residents mainly)
    from flask import session
    condo_id = session.get('active_condo_id')
    
    logs = VisitLog.query.filter(
        VisitLog.condo_id == condo_id, 
        VisitLog.user_id != None
    ).order_by(VisitLog.entry_time.desc()).limit(100).all()
    
    return render_template('access/history.html', logs=logs)

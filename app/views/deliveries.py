from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.delivery import Delivery
from app.models.core import Unit
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

deliveries_bp = Blueprint('deliveries', __name__)

@deliveries_bp.route('/')
@login_required
def index():
    # Porteiro/Admin view: List all pending deliveries
    if not current_user.can_register_visits:
        flash('Acesso negado. Área restrita à portaria.', 'danger')
        return redirect(url_for('main.index'))
        
    pending_deliveries = Delivery.query.join(Unit).filter(
        Unit.condo_id == current_user.condo_id, # Or use active_condo_id from session for safety
        Delivery.status == 'pending'
    ).order_by(Delivery.received_at.desc()).all()
    
    # Better to use session if admin context can switch
    # but deliveries are physical, linked to Unit.
    # If admin switches condo, current_user.condo_id should ideally match or we use session.
    from flask import session
    condo_id = session.get('active_condo_id')
    pending_deliveries = Delivery.query.join(Unit).filter(
        Unit.condo_id == condo_id,
        Delivery.status == 'pending'
    ).order_by(Delivery.received_at.desc()).all()
    
    # Simple stats
    today = datetime.now().date()
    # delivered_today = Delivery.query.filter(db.func.date(Delivery.picked_up_at) == today).count() # If needed
    
    return render_template('deliveries/index.html', deliveries=pending_deliveries)

@deliveries_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not current_user.can_register_visits:
         flash('Acesso negado.', 'danger')
         return redirect(url_for('main.index'))

    if request.method == 'POST':
        unit_id = request.form.get('unit_id')
        description = request.form.get('description')
        
        if not unit_id or not description:
            flash('Unidade e Descrição são obrigatórias.', 'danger')
            return redirect(url_for('deliveries.new'))
            
        recipient_label = request.form.get('recipient_label')
        storage_location = request.form.get('storage_location')
            
        # Handle Image
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
                new_filename = f"delivery_{uuid.uuid4().hex[:8]}.{ext}"
                
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'deliveries')
                file.save(os.path.join(upload_path, new_filename))
                image_filename = new_filename

        delivery = Delivery(
            unit_id=unit_id,
            description=description,
            recipient_label=recipient_label,
            storage_location=storage_location,
            image_filename=image_filename
        )
        db.session.add(delivery)
        
        # Notify Residents
        unit = Unit.query.get(unit_id)
        if unit:
            from app.models.notification import Notification
            for resident in unit.residents:
                msg = f"Chegou encomenda! {description}"
                if recipient_label:
                    msg += f" (Para: {recipient_label})"
                
                notif = Notification(
                    user_id=resident.id,
                    message=msg
                )
                db.session.add(notif)
        
        db.session.commit()
        flash('Encomenda registrada e moradores notificados!', 'success')
        return redirect(url_for('deliveries.index'))

    from flask import session
    units = Unit.query.filter_by(condo_id=session.get('active_condo_id')).order_by(Unit.block, Unit.number).all()
    return render_template('deliveries/form.html', units=units)

@deliveries_bp.route('/pickup/<int:id>', methods=['POST'])
@login_required
def pickup(id):
    if not current_user.can_register_visits:
         flash('Acesso negado.', 'danger')
         return redirect(url_for('main.index'))
         
    delivery = Delivery.query.get_or_404(id)
    recipient_name = request.form.get('recipient_name')
    
    delivery.status = 'picked_up'
    delivery.picked_up_at = datetime.now()
    delivery.picked_up_by = recipient_name or 'Morador'
    
    db.session.commit()
    flash('Entrega registrada com sucesso.', 'success')
    return redirect(url_for('deliveries.index'))

@deliveries_bp.route('/my_deliveries')
@login_required
def my_deliveries():
    if not current_user.unit_id and not current_user.is_admin:
        flash('Você não está vinculado a uma unidade.', 'danger')
        return redirect(url_for('main.index'))
        
    my_pending = Delivery.query.filter_by(unit_id=current_user.unit_id, status='pending').all()
    my_history = Delivery.query.filter_by(unit_id=current_user.unit_id, status='picked_up').order_by(Delivery.picked_up_at.desc()).limit(10).all()
    
    return render_template('deliveries/my_deliveries.html', pending=my_pending, history=my_history)

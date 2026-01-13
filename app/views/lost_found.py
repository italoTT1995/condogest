from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.lost_found import LostItem
from app.models.user import User
from app.models.core import Unit
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

lost_found_bp = Blueprint('lost_found', __name__)

@lost_found_bp.route('/')
@login_required
def index():
    try:
        from flask import session
        condo_id = session.get('active_condo_id')
        
        items_unclaimed = LostItem.query.filter_by(condo_id=condo_id, status='unclaimed').order_by(LostItem.found_at.desc()).all()
        items_claimed = LostItem.query.filter_by(condo_id=condo_id, status='claimed').order_by(LostItem.claimed_at.desc()).limit(20).all()
        
        # Get residents for the claim modal datalist
        residents = User.query.join(Unit).filter(Unit.condo_id == condo_id).order_by(User.username).all()
        
        return render_template('lost_found/index.html', 
                             items_unclaimed=items_unclaimed, 
                             items_claimed=items_claimed,
                             residents=residents)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Erro ao carregar página: {str(e)}", 'danger')
        return redirect(url_for('main.index'))

@lost_found_bp.route('/new', methods=['POST'])
@login_required
def new():
    if not current_user.can_register_visits:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('lost_found.index'))
        
    description = request.form.get('description')
    location = request.form.get('location')
    
    # Handle Image
    image_filename = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
            new_filename = f"lost_{uuid.uuid4().hex[:8]}.{ext}"
            
            # Ensure folder exists
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'lost_found')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
                
            file.save(os.path.join(upload_path, new_filename))
            image_filename = new_filename

    from flask import session
    condo_id = session.get('active_condo_id')

    item = LostItem(
        description=description,
        location_found=location,
        image_filename=image_filename,
        found_by_id=current_user.id,
        condo_id=condo_id
    )
    
    db.session.add(item)
    db.session.commit()
    
    # Optional: Notify all residents? Maybe too spammy.
    # Let's just flash success.
    flash('Item registrado com sucesso!', 'success')
    return redirect(url_for('lost_found.index'))

@lost_found_bp.route('/<int:id>/claim', methods=['POST'])
@login_required
def claim(id):
    if not current_user.can_register_visits:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('lost_found.index'))
        
    item = LostItem.query.get_or_404(id)
    claimer_name = request.form.get('claimer_name')
    
    # Try to find user by name
    claimer = User.query.filter_by(username=claimer_name).first()
    
    item.status = 'claimed'
    item.claimed_at = datetime.now()
    if claimer:
        item.claimed_by_id = claimer.id
    
    db.session.commit()
    flash('Item marcado como entregue.', 'success')
    return redirect(url_for('lost_found.index'))

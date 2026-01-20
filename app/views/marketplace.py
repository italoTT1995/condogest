from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.marketplace import ClassifiedAd
from app import db
import os
import uuid
from werkzeug.utils import secure_filename

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

@marketplace_bp.route('/')
@login_required
def index():
    from flask import session
    condo_id = session.get('active_condo_id')
    
    # Show active ads for this condo
    ads = ClassifiedAd.query.filter_by(condo_id=condo_id, status='active').order_by(ClassifiedAd.created_at.desc()).all()
    
    return render_template('marketplace/index.html', ads=ads)

@marketplace_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        contact = request.form.get('contact')
        
        # Handle Image
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
                new_filename = f"ad_{uuid.uuid4().hex[:8]}.{ext}"
                
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'marketplace')
                os.makedirs(upload_path, exist_ok=True)
                    
                file.save(os.path.join(upload_path, new_filename))
                image_filename = new_filename
        
        from flask import session
        condo_id = session.get('active_condo_id')
        
        ad = ClassifiedAd(
            title=title,
            description=description,
            price=float(price) if price else 0.0,
            contact_info=contact,
            image_filename=image_filename,
            user_id=current_user.id,
            condo_id=condo_id
        )
        
        db.session.add(ad)
        db.session.commit()
        flash('Anúncio criado com sucesso!', 'success')
        return redirect(url_for('marketplace.index'))
        
    return render_template('marketplace/form.html')

@marketplace_bp.route('/<int:id>/sold', methods=['POST'])
@login_required
def mark_sold(id):
    ad = ClassifiedAd.query.get_or_404(id)
    
    if ad.user_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('marketplace.index'))
        
    ad.status = 'sold'
    db.session.commit()
    flash('Item marcado como vendido!', 'success')
    return redirect(url_for('marketplace.index'))

@marketplace_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    ad = ClassifiedAd.query.get_or_404(id)
    
    if ad.user_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('marketplace.index'))
        
    # Optional: Delete image from disk
    
    db.session.delete(ad)
    db.session.commit()
    flash('Anúncio removido.', 'success')
    return redirect(url_for('marketplace.index'))

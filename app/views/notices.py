from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models.core import Notice
from app import db
import os
import uuid
from werkzeug.utils import secure_filename

notices_bp = Blueprint('notices', __name__)

@notices_bp.route('/')
@login_required
def index():
    from flask import session
    condo_id = session.get('active_condo_id')
    
    # Order by Important first, then Date
    notices = Notice.query.filter_by(condo_id=condo_id).order_by(Notice.is_important.desc(), Notice.created_at.desc()).all()
    return render_template('notices/index.html', notices=notices)

@notices_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        is_important = True if request.form.get('is_important') else False
        
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
                image_filename = f"notice_{uuid.uuid4().hex[:8]}.{ext}"
                
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'notices')
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, image_filename))

        from flask import session
        condo_id = session.get('active_condo_id')
        
        notice = Notice(
            title=title, 
            content=content, 
            image_filename=image_filename,
            is_important=is_important,
            created_by=current_user.id,
            condo_id=condo_id
        )
        db.session.add(notice)
        db.session.commit()
        
        # Notify all residents OF THIS CONDO
        from app.models.user import User
        from app.models.notification import Notification
        
        residents = User.query.filter_by(condo_id=condo_id).all() # Notify only this condo residents
        msg_prefix = "🚨 URGENTE: " if is_important else "📢 Novo Comunicado: "
        
        for resident in residents:
            # Don't notify the author themselves if you prefer, but usually good to confirm
            if resident.id != current_user.id: 
                notif = Notification(
                    user_id=resident.id,
                    message=f"{msg_prefix}{title}"
                )
                db.session.add(notif)
        db.session.commit()

        flash('Comunicado publicado no Mural!')
        return redirect(url_for('notices.index'))
    return render_template('notices/create.html')

@notices_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    notice = Notice.query.get_or_404(id)
    db.session.delete(notice)
    db.session.commit()
    flash('Comunicado excluído com sucesso.')
    return redirect(url_for('notices.index'))

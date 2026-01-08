from flask import Blueprint, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.notification import Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/read/<int:id>', methods=['POST'])
@login_required
def mark_read(id):
    notif = Notification.query.get_or_404(id)
    if notif.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@notifications_bp.route('/read_all', methods=['POST'])
@login_required
def mark_all_read():
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for n in notifications:
        n.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for('main.index'))

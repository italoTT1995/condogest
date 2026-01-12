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

@notifications_bp.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
        
    subscription_info = data.get('subscription_info')
    if not subscription_info:
        return jsonify({'error': 'Missing subscription_info'}), 400
        
    from app.models.notification import PushSubscription
    
    # Check if subscription already exists
    endpoint = subscription_info.get('endpoint')
    existing = PushSubscription.query.filter_by(endpoint=endpoint).first()
    
    if not existing:
        new_sub = PushSubscription(
            user_id=current_user.id,
            endpoint=endpoint,
            p256dh=subscription_info['keys']['p256dh'],
            auth=subscription_info['keys']['auth']
        )
        db.session.add(new_sub)
        db.session.commit()
    
    return jsonify({'success': True})

def send_web_push(user_id, message_body):
    from app.models.notification import PushSubscription
    from pywebpush import webpush, WebPushException
    import os
    import json
    
    subscriptions = PushSubscription.query.filter_by(user_id=user_id).all()
    
    # VAPID Keys (MUST be set in env vars for production)
    # Using a generated pair for testing/default if missing (Not recommended for prod persistence)
    VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
    VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
    VAPID_CLAIMS = {"sub": "mailto:admin@condomanager.com"}
    
    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        print("VAPID Keys not configured. Skipping Push.")
        return

    payload = json.dumps({
        "title": "CondoGest",
        "body": message_body,
        "icon": "/static/img/logo.png",
        "url": "/"
    })

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth
                    }
                },
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        except WebPushException as ex:
            print(f"Push failed: {repr(ex)}")
            # If 410 Gone, remove subscription
            if ex.response and ex.response.status_code == 410:
                db.session.delete(sub)
                db.session.commit()
        except Exception as e:
            print(f"Generic Push Error: {e}")

@notifications_bp.route('/vapid_public_key')
def get_vapid_public_key():
    import os
    # Fallback to a dummy key if env var not set to prevent JS errors, 
    # but strictly speaking it wont work without a real key pair.
    # User needs to run generate_vapid_keys.py
    pub_key = os.environ.get('VAPID_PUBLIC_KEY')
    return jsonify({'publicKey': pub_key})

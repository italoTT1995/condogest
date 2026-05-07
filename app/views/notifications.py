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
    pub_key = os.environ.get('VAPID_PUBLIC_KEY')
    return jsonify({'publicKey': pub_key})

@notifications_bp.route('/emergency', methods=['POST'])
@login_required
def trigger_emergency():
    """Dispara alerta de emergência para todos os síndicos e porteiros do condomínio."""
    from app.models.user import User, Role
    from datetime import datetime

    data = request.get_json() or {}
    emergency_type = data.get('type', 'emergency_police')

    tag = "[🚨 POLÍCIA]" if emergency_type == 'emergency_police' else "[🔔 PORTEIRO]"
    message = f"{tag} EMERGÊNCIA ACIONADA por: {current_user.name} ({current_user.unit_block} - {current_user.unit_number})"

    # Buscar usuários com cargo de admin/síndico/porteiro via ROLE OBJECT (novo sistema)
    staff_via_role = User.query.join(Role, User.role_id == Role.id).filter(
        Role.name.in_(['Síndico', 'Sindico', 'Porteiro', 'Admin'])
    ).all()
    
    # Também buscar via role string (sistema legado) para garantir compatibilidade
    staff_via_string = User.query.filter(
        User.role.in_(['admin', 'porteiro', 'sindico'])
    ).all()
    
    # Unir as duas listas sem duplicatas
    staff_ids = {u.id for u in staff_via_role} | {u.id for u in staff_via_string}
    users_to_alert = [u for u in (staff_via_role + staff_via_string) if u.id in staff_ids]
    # Remover duplicatas
    seen = set()
    unique_staff = []
    for u in users_to_alert:
        if u.id not in seen:
            seen.add(u.id)
            unique_staff.append(u)

    notified = 0
    for u in unique_staff:
        if u.id != current_user.id:
            notif = Notification(
                user_id=u.id,
                message=message,
                notification_type=emergency_type
            )
            db.session.add(notif)
            send_web_push(u.id, message)
            notified += 1

    db.session.commit()
    
    if notified == 0:
        return jsonify({'success': True, 'message': 'Alerta registrado. Nenhuma equipe encontrada no sistema para notificar.'})
    
    return jsonify({'success': True, 'message': f'Alerta de emergência enviado para {notified} pessoa(s)!'})


@notifications_bp.route('/check_emergency', methods=['GET'])
@login_required
def check_emergency():
    """Endpoint de polling para a interface tocar a sirene de emergência"""
    from app.models.user import Role
    
    # Apenas porteiros e síndicos (e admins) devem ficar fazendo polling
    if not current_user.user_role or current_user.user_role.name not in ['Síndico', 'Sindico', 'Porteiro', 'Admin']:
        return jsonify({'emergency': False})
        
    # Buscar a emergência mais recente não lida
    latest_emergency = Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
        Notification.notification_type.in_(['emergency_police', 'emergency_porteiro'])
    ).order_by(Notification.created_at.desc()).first()
    
    if latest_emergency:
        # Identificar quem mandou a emergência pelo texto (simplificação)
        # O padrão é: "[TAG] EMERGÊNCIA ACIONADA por: Nome (Bloco - Numero)"
        import re
        parts = latest_emergency.message.split(' por: ')
        solicitante = parts[1] if len(parts) > 1 else "Desconhecido"
        
        return jsonify({
            'emergency': True,
            'id': latest_emergency.id,
            'type': latest_emergency.notification_type,
            'message': latest_emergency.message,
            'solicitante': solicitante,
            'time': latest_emergency.created_at.strftime('%H:%M')
        })
        
    return jsonify({'emergency': False})

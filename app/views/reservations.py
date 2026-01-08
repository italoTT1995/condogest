from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.decorators import admin_required, superuser_required
from app.models.amenity import CommonArea, Reservation
from app.models.notification import Notification
from app import db
from datetime import datetime

reservations_bp = Blueprint('reservations', __name__)

# --- ADMIN ROUTES (Manage Areas) ---

@reservations_bp.route('/areas')
@login_required
@superuser_required
def manage_areas():
    areas = CommonArea.query.all()
    return render_template('reservations/manage_areas.html', areas=areas)

@reservations_bp.route('/areas/new', methods=['GET', 'POST'])
@login_required
@superuser_required
def create_area():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        capacity = request.form['capacity']
        
        area = CommonArea(name=name, description=description, capacity=capacity)
        db.session.add(area)
        db.session.commit()
        flash('Área comum criada com sucesso!')
        return redirect(url_for('reservations.manage_areas'))
        
    return render_template('reservations/create_area.html')

@reservations_bp.route('/areas/<int:id>/delete', methods=['POST'])
@login_required
@superuser_required
def delete_area(id):
    area = CommonArea.query.get_or_404(id)
    db.session.delete(area)
    db.session.commit()
    flash('Área removida com sucesso.')
    return redirect(url_for('reservations.manage_areas'))

# --- RESIDENT ROUTES (Bookings) ---

@reservations_bp.route('/my_reservations')
@login_required
def my_reservations():
    if current_user.is_admin:
        # Admin sees ALL reservations
        all_reservations = Reservation.query.order_by(Reservation.date.desc()).all()
        return render_template('reservations/admin_list.html', reservations=all_reservations)
    else:
        # Resident sees only theirs + available areas to book
        my_res = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.date.desc()).all()
        areas = CommonArea.query.all()
        return render_template('reservations/my_reservations.html', reservations=my_res, areas=areas)

@reservations_bp.route('/book/<int:area_id>', methods=['GET', 'POST'])
@login_required
def book_area(area_id):
    area = CommonArea.query.get_or_404(area_id)
    if request.method == 'POST':
        date_str = request.form['date']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        
        # --- FINANCIAL SECURITY RULE ---
        from app.models.core import Payment
        overdue_payments = Payment.query.filter(
            Payment.user_id == current_user.id,
            Payment.status != 'paid',
            Payment.due_date < datetime.now().date()
        ).count()
        
        if overdue_payments > 0:
            # ALERT MODE: Do not block, but notify
            flash('Atenção: Identificamos pendências financeiras. Sua reserva foi realizada, mas a administração será notificada.', 'warning')
            
            # Notify Resident
            notif_res = Notification(
                user_id=current_user.id,
                message=f'Reserva realizada para {area.name} em {date_str}, porém constam pendências financeiras.'
            )
            db.session.add(notif_res)
            
            # Notify Admins/Sindicos
            from app.models.user import User
            admins = User.query.filter(User.role.in_(['admin', 'sindico'])).all()
            for admin in admins:
                notif_admin = Notification(
                    user_id=admin.id,
                    message=f'ALERTA: Morador {current_user.username} (Unidade {current_user.unit_id}) reservou {area.name} com pendências financeiras.'
                )
                db.session.add(notif_admin)
            
            db.session.commit()
            # return redirect(url_for('reservations.book_area', area_id=area_id)) # REMOVED BLOCK
        # -------------------------------
        
        # Convert strings to objects
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
        
        # Check for overlapping (status pending or approved)
        # Check for conflict (One reservation per day per area)
        conflict = Reservation.query.filter(
            Reservation.area_id == area.id,
            Reservation.date == date_obj,
            Reservation.status.in_(['pending', 'approved'])
        ).first()

        if conflict:
            flash(f'Erro: Data indisponível! A área "{area.name}" já possui uma reserva para o dia {date_obj.strftime("%d/%m/%Y")}.', 'danger')
            return redirect(url_for('reservations.book_area', area_id=area_id))
        
        res = Reservation(
            user_id=current_user.id,
            area_id=area.id,
            date=date_obj,
            start_time=start_time_obj,
            end_time=end_time_obj,
            status='pending' # Needs admin approval
        )
        db.session.add(res)
        db.session.commit()
        flash('Solicitação de reserva enviada! Aguarde aprovação.')
        return redirect(url_for('reservations.my_reservations'))
        
    # Fetch existing reservations to show availability
    existing_reservations = Reservation.query.filter(
        Reservation.area_id == area.id,
        Reservation.status.in_(['pending', 'approved']),
        Reservation.date >= datetime.now().date()
    ).order_by(Reservation.date, Reservation.start_time).all()

    return render_template('reservations/book_area.html', area=area, existing_reservations=existing_reservations)

@reservations_bp.route('/approve/<int:id>', methods=['POST'])
@login_required
@admin_required
def approve_reservation(id):
    res = Reservation.query.get_or_404(id)
    res.status = 'approved'
    
    import uuid
    if not res.access_token:
        res.access_token = uuid.uuid4().hex
    
    # Notify User
    area_name = res.area.name if res.area else "Área Removida"
    notif = Notification(
        user_id=res.user_id,
        message=f'Sua reserva para {area_name} no dia {res.date.strftime("%d/%m/%Y")} foi APROVADA!'
    )
    db.session.add(notif)
    
    db.session.commit()
    flash('Reserva aprovada!')
    return redirect(url_for('reservations.my_reservations'))

@reservations_bp.route('/reject/<int:id>', methods=['POST'])
@login_required
@admin_required
def reject_reservation(id):
    res = Reservation.query.get_or_404(id)
    res.status = 'rejected'
    
    # Notify User
    area_name = res.area.name if res.area else "Área Removida"
    notif = Notification(
        user_id=res.user_id,
        message=f'Sua reserva para {area_name} no dia {res.date.strftime("%d/%m/%Y")} foi REJEITADA.'
    )
    db.session.add(notif)
    
    db.session.commit()
    flash('Reserva rejeitada.')
    return redirect(url_for('reservations.my_reservations'))

@reservations_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_reservation(id):
    res = Reservation.query.get_or_404(id)
    db.session.delete(res)
    db.session.commit()
    flash('Reserva excluída com sucesso.')
    return redirect(url_for('reservations.my_reservations'))

# --- QR CODE ACCESS CONTROL ---
import qrcode
from io import BytesIO
from flask import send_file
import uuid

@reservations_bp.route('/qr_code/<int:reservation_id>')
@login_required
def qr_code(reservation_id):
    res = Reservation.query.get_or_404(reservation_id)
    
    # Security check: User must own the reservation OR be admin
    if res.user_id != current_user.id and not current_user.is_admin:
        return "Acesso negado", 403

    if not res.access_token:
        # Generate token if missing (lazy generation)
        res.access_token = uuid.uuid4().hex
        db.session.commit()
        
    # Generate QR
    img = qrcode.make(res.access_token)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

@reservations_bp.route('/scan')
@login_required
def scan():
    # Only admins/porters should scan. For now, allow all logged in for demo.
    if not (current_user.is_admin or current_user.is_porteiro):
         flash('Acesso restrito à portaria/segurança.', 'danger')
         return redirect(url_for('main.index'))
         
    return render_template('reservations/scan.html')

@reservations_bp.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    token = request.args.get('token') or request.form.get('token')
    
    if not token:
        flash('Token inválido.', 'danger')
        return redirect(url_for('reservations.scan'))
        
    res = Reservation.query.filter_by(access_token=token).first()
    
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()
    
    status = 'denied'
    message = 'Token não encontrado ou inválido.'
    
    reservation_data = None
    
    if res:
        reservation_data = res
        if res.status != 'approved':
             message = 'Reserva não está APROVADA.'
        elif res.date != current_date:
             message = f'Data inválida. Reserva é para {res.date.strftime("%d/%m/%Y")}.'
        elif not (res.start_time <= current_time <= res.end_time):
             message = f'Fora do horário permitido ({res.start_time.strftime("%H:%M")} - {res.end_time.strftime("%H:%M")}).'
        else:
             status = 'allowed'
             message = 'Acesso Autorizado!'

    return render_template('reservations/access_result.html', status=status, message=message, reservation=reservation_data)


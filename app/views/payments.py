from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models.core import Payment
from app.models.user import User
from app import db
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/')
@login_required
def index():
    if current_user.is_admin:
        from flask import session
        condo_id = session.get('active_condo_id')
        payments = Payment.query.filter_by(condo_id=condo_id).order_by(Payment.due_date.desc()).all()
    else:
        # Resident sees payments for their UNIT or explicitly assigned to them
        if current_user.unit_id:
            payments = Payment.query.filter((Payment.unit_id == current_user.unit_id) | (Payment.user_id == current_user.id)).order_by(Payment.due_date.desc()).all()
        else:
            payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.due_date.desc()).all()

    return render_template('payments/index.html', payments=payments)

@payments_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    from flask import session
    from app.models.core import Unit
    condo_id = session.get('active_condo_id')
    
    # Allow selecting Units instead of Users
    units = Unit.query.filter_by(condo_id=condo_id).order_by(Unit.block, Unit.number).all()
    
    if request.method == 'POST':
        unit_id = request.form.get('unit_id')
        description = request.form['description']
        amount = float(request.form['amount'])
        due_date_str = request.form['due_date']
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        
        payment = Payment(
            unit_id=unit_id, # Link to Unit
            description=description, 
            amount=amount, 
            due_date=due_date,
            condo_id=condo_id
        )
        db.session.add(payment)
        db.session.commit()
        flash('Cobrança lançada para a Unidade com sucesso!')
        return redirect(url_for('payments.index'))
    return render_template('payments/create.html', units=units)

@payments_bp.route('/<int:id>/pay', methods=['POST'])
@login_required
def pay(id):
    payment = Payment.query.get_or_404(id)
    
    # Auth check: Admin or Resident of the unit
    allowed = False
    if current_user.is_admin:
        allowed = True
    elif payment.unit_id and current_user.unit_id == payment.unit_id:
        allowed = True
    elif payment.user_id == current_user.id:
        allowed = True
        
    if not allowed:
        flash('Acesso negado.')
        return redirect(url_for('payments.index'))

    payment.status = 'paid'
    # Record who paid
    payment.user_id = current_user.id 
    db.session.commit()
    flash('Pagamento registrado.')
    return redirect(url_for('payments.index'))

@payments_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    flash('Cobrança excluída com sucesso.')
    return redirect(url_for('payments.index'))

@payments_bp.route('/<int:id>/boleto')
@login_required
def boleto(id):
    payment = Payment.query.get_or_404(id)
    
    # Auth check
    allowed = False
    if current_user.is_admin:
        allowed = True
    elif payment.unit_id and current_user.unit_id == payment.unit_id:
        allowed = True
    elif payment.user_id == current_user.id:
        allowed = True

    if not allowed:
        flash('Acesso negado.')
        return redirect(url_for('payments.index'))

    return render_template('payments/boleto.html', payment=payment)

@payments_bp.route('/<int:id>/pix')
@login_required
def pix(id):
    payment = Payment.query.get_or_404(id)
    # Auth Check (Reuse logic?)
    allowed = False
    if current_user.is_admin:
        allowed = True
    elif payment.unit_id and current_user.unit_id == payment.unit_id:
        allowed = True
    elif payment.user_id == current_user.id:
        allowed = True
    
    if not allowed:
         flash('Acesso negado.')
         return redirect(url_for('payments.index'))

    return render_template('payments/pix.html', payment=payment)

@payments_bp.route('/<int:id>/send_email', methods=['POST'])
@login_required
@admin_required
def send_email(id):
    payment = Payment.query.get_or_404(id)
    
    recipients = []
    if payment.unit_id:
        # Get all residents of the unit
        residents = User.query.filter_by(unit_id=payment.unit_id).all()
        for r in residents:
            if r.email:
                recipients.append(r.email)
    elif payment.user_id:
        # Fallback for old payments
        u = User.query.get(payment.user_id)
        if u and u.email:
            recipients.append(u.email)

    if not recipients:
        flash('Nenhum email encontrado para enviar a cobrança.', 'warning')
        return redirect(url_for('payments.index'))
        
    try:
        from flask_mail import Message
        from app import mail
        
        msg = Message(f"Cobrança Disponível - {payment.description}",
                      recipients=recipients)
        
        link = url_for('payments.boleto', id=payment.id, _external=True)
        
        msg.body = f"""Olá,
        
Uma nova cobrança foi gerada para sua unidade.

Descrição: {payment.description}
Valor: R$ {payment.amount}
Vencimento: {payment.due_date.strftime('%d/%m/%Y')}

Acesse seu boleto no link abaixo:
{link}

Atenciosamente,
Administração do Condomínio
"""
        mail.send(msg)
        flash(f'Email enviado para {len(recipients)} destinatários com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao enviar email: {str(e)}', 'danger')
        
    return redirect(url_for('payments.index'))

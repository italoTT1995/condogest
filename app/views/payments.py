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
        payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.due_date.desc()).all()
    return render_template('payments/index.html', payments=payments)

@payments_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    from flask import session
    condo_id = session.get('active_condo_id')
    users = User.query.filter_by(role='resident', condo_id=condo_id).all()
    
    if request.method == 'POST':
        user_id = request.form['user_id']
        description = request.form['description']
        amount = float(request.form['amount'])
        due_date_str = request.form['due_date']
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        
        payment = Payment(
            user_id=user_id, 
            description=description, 
            amount=amount, 
            due_date=due_date,
            condo_id=condo_id
        )
        db.session.add(payment)
        db.session.commit()
        flash('Cobrança lançada com sucesso!')
        return redirect(url_for('payments.index'))
    return render_template('payments/create.html', users=users)

@payments_bp.route('/<int:id>/pay', methods=['POST'])
@login_required
@admin_required
def pay(id):
    payment = Payment.query.get_or_404(id)
    payment.status = 'paid'
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
    if payment.user_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('payments.index'))
    return render_template('payments/boleto.html', payment=payment)

@payments_bp.route('/<int:id>/pix')
@login_required
def pix(id):
    payment = Payment.query.get_or_404(id)
    if payment.user_id != current_user.id and not current_user.is_admin:
         flash('Acesso negado.')
         return redirect(url_for('payments.index'))
    return render_template('payments/pix.html', payment=payment)

@payments_bp.route('/<int:id>/send_email', methods=['POST'])
@login_required
@admin_required
def send_email(id):
    payment = Payment.query.get_or_404(id)
    user = User.query.get(payment.user_id)
    
    if not user.email:
        flash('Usuário não possui email cadastrado.', 'danger')
        return redirect(url_for('payments.index'))
        
    try:
        from flask_mail import Message
        from app import mail
        
        msg = Message(f"Cobrança Disponível - {payment.description}",
                      recipients=[user.email])
        
        # Link to boleto (assuming external access or internal network for now)
        link = url_for('payments.boleto', id=payment.id, _external=True)
        
        msg.body = f"""Olá {user.username},
        
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
        flash(f'Email enviado para {user.email} com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao enviar email: {str(e)}', 'danger')
        
    return redirect(url_for('payments.index'))

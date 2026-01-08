from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.core import Ticket
from app.models.ticket_comment import TicketComment
from app import db

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/')
@login_required
def index():
    # Filter by user role/category
    # Residents see their own tickets (any category)
    # Staff sees tickets based on category
    
    filter_status = request.args.get('status', 'all')
    
    if filter_status == 'all':
        if current_user.is_resident and not current_user.is_admin:
            tickets = Ticket.query.filter_by(user_id=current_user.id, category='maintenance').order_by(Ticket.created_at.desc()).all()
        else:
             # Admin/Zelador see all maintenance tickets for ACTIVE CONDO
             from flask import session
             from app.models.user import User
             condo_id = session.get('active_condo_id')
             tickets = Ticket.query.join(User).filter(User.condo_id == condo_id, Ticket.category == 'maintenance').order_by(Ticket.created_at.desc()).all()
    else:
        if current_user.is_resident and not current_user.is_admin:
            tickets = Ticket.query.filter_by(user_id=current_user.id, status=filter_status, category='maintenance').order_by(Ticket.created_at.desc()).all()
        else:
            from flask import session
            from app.models.user import User
            condo_id = session.get('active_condo_id')
            tickets = Ticket.query.join(User).filter(User.condo_id == condo_id, Ticket.status == filter_status, Ticket.category == 'maintenance').order_by(Ticket.created_at.desc()).all()
            
    return render_template('tickets/index.html', tickets=tickets, filter_status=filter_status)

@tickets_bp.route('/complaints')
@login_required
def complaints():
    # Similar to index but for complaints
    if not (current_user.is_admin or current_user.can_manage_complaints):
         # If resident, they can see their own complaints
         complaints = Ticket.query.filter_by(user_id=current_user.id, category='complaint').order_by(Ticket.created_at.desc()).all()
    else:
         # Admin/Zelador see all complaints for ACTIVE CONDO
         from flask import session
         from app.models.user import User
         condo_id = session.get('active_condo_id')
         complaints = Ticket.query.join(User).filter(User.condo_id == condo_id, Ticket.category == 'complaint').order_by(Ticket.created_at.desc()).all()
         
    return render_template('tickets/complaints.html', tickets=complaints)

import os
from werkzeug.utils import secure_filename
from flask import current_app

@tickets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                import uuid
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                new_filename = f"ticket_{uuid.uuid4().hex}.{ext}"
                
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'tickets')
                # Ensure directory exists
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                    
                file.save(os.path.join(upload_path, new_filename))
                image_filename = new_filename

        # Get category from form (hidden or select), default maintenance
        category = request.form.get('category', 'maintenance')

        ticket = Ticket(
            title=title, 
            description=description, 
            author=current_user, 
            image_filename=image_filename,
            category=category
        )
        db.session.add(ticket)
        db.session.commit()
        
        if category == 'complaint':
            flash('Denúncia registrada com sucesso!', 'success')
            return redirect(url_for('tickets.complaints'))
        else:
            flash('Chamado aberto com sucesso!', 'success')
            return redirect(url_for('tickets.index'))

    # Determine if creating complaint or ticket based on args
    is_complaint = request.args.get('type') == 'complaint'
    title_text = "Nova Denúncia" if is_complaint else "Novo Chamado"
            
    return render_template('tickets/create.html', title=title_text, is_complaint=is_complaint)

@tickets_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem alterar o status.')
        return redirect(url_for('tickets.index'))
    
    ticket = Ticket.query.get_or_404(id)
    new_status = request.form['status']
    ticket.status = new_status
    
    # Notify Resident
    from app.models.notification import Notification
    status_map = {'open': 'Aberto', 'in_progress': 'Em Andamento', 'closed': 'Concluído'}
    status_label = status_map.get(new_status, new_status)
    
    notif = Notification(user_id=ticket.user_id, message=f"🔄 Status do chamado atualizado para: {status_label}")
    db.session.add(notif)
    
    db.session.commit()
    flash('Status do chamado atualizado.')
    return redirect(url_for('tickets.index'))

@tickets_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem excluir chamados.')
        return redirect(url_for('tickets.index'))
    
    ticket = Ticket.query.get_or_404(id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Chamado excluído com sucesso.')
    return redirect(url_for('tickets.index'))

@tickets_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    ticket = Ticket.query.get_or_404(id)
    
    # Permission check: Must be owner
    if ticket.user_id != current_user.id:
        flash('Você não tem permissão para editar este chamado.', 'danger')
        return redirect(url_for('tickets.index'))
        
    # Status check: Must be 'open'
    if ticket.status != 'open':
        flash('Este chamado já está em atendimento ou concluído e não pode ser editado.', 'warning')
        return redirect(url_for('tickets.index'))
        
    if request.method == 'POST':
        ticket.title = request.form['title']
        ticket.description = request.form['description']
        db.session.commit()
        flash('Chamado atualizado com sucesso!', 'success')
        return redirect(url_for('tickets.index'))
        
    return render_template('tickets/edit.html', ticket=ticket)

@tickets_bp.route('/<int:id>')
@login_required
def details(id):
    ticket = Ticket.query.get_or_404(id)
    
    # Permission check: Owner or Admin
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('tickets.index'))
        
    comments = ticket.comments.order_by(TicketComment.created_at.asc()).all()
    return render_template('tickets/details.html', ticket=ticket, comments=comments)

@tickets_bp.route('/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    ticket = Ticket.query.get_or_404(id)
    content = request.form['content']
    
    if not content.strip():
        flash('Comentário não pode estar vazio.', 'warning')
        return redirect(url_for('tickets.details', id=id))

    # Save comment
    from app.models.ticket_comment import TicketComment
    comment = TicketComment(content=content, ticket_id=ticket.id, user_id=current_user.id)
    db.session.add(comment)
    
    # Notification Logic
    from app.models.notification import Notification
    
    # If Admin commented, notify Author
    if current_user.is_admin and ticket.user_id != current_user.id:
         notif = Notification(user_id=ticket.user_id, message=f"💬 Nova resposta no chamado: {ticket.title}")
         db.session.add(notif)
    
    # If Author commented, notify Admins (optional, or just rely on dashboard)
    # For now, let's notify admins could be noisy, but good for responsiveness
    # Skipping admin notification for simplicity unless requested
    
    db.session.commit()
    flash('Resposta enviada.', 'success')
    return redirect(url_for('tickets.details', id=id))

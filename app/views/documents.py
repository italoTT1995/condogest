from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from app.models.documents import Document
from app import db
import os
from werkzeug.utils import secure_filename
import uuid

documents_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/')
@login_required
def index():
    from flask import session
    condo_id = session.get('active_condo_id')
    
    # Filter: Residents only see public docs. Admins see all. WITH CONDO FILTER
    if current_user.is_admin:
        documents = Document.query.filter_by(condo_id=condo_id).order_by(Document.created_at.desc()).all()
    else:
        documents = Document.query.filter_by(condo_id=condo_id, is_public=True).order_by(Document.created_at.desc()).all()
        
    # Group by category for easier display
    categories = {
        'minutes': [],
        'convention': [],
        'financial': [],
        'contract': [],
        'other': []
    }
    
    for doc in documents:
        if doc.category in categories:
            categories[doc.category].append(doc)
        else:
            categories['other'].append(doc)
            
    return render_template('documents/index.html', categories=categories)

@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('documents.index'))
        
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado.')
        return redirect(url_for('documents.index'))
        
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.')
        return redirect(url_for('documents.index'))
        
    if file and allowed_file(file.filename):
        # Secure filename and save
        original_filename = secure_filename(file.filename)
        # Add unique ID to prevent overwrite
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
        os.makedirs(upload_folder, exist_ok=True)
        
        file.save(os.path.join(upload_folder, unique_filename))
        
        # Create DB record
        title = request.form['title']
        category = request.form['category']
        is_public = 'is_public' in request.form
        
        from flask import session
        
        doc = Document(
            title=title,
            description=request.form.get('description', ''),
            filename=unique_filename,
            category=category,
            is_public=is_public,
            user_id=current_user.id,
            condo_id=session.get('active_condo_id')
        )
        db.session.add(doc)
        db.session.commit()
        
        flash('Documento publicado com sucesso!', 'success')
    else:
        flash('Tipo de arquivo não permitido.', 'danger')
        
    return redirect(url_for('documents.index'))

@documents_bp.route('/download/<int:id>')
@login_required
def download(id):
    doc = Document.query.get_or_404(id)
    
    # Permission check
    if not doc.is_public and not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('documents.index'))
        
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
    return send_from_directory(upload_folder, doc.filename, as_attachment=True, download_name=f"{doc.title}.{doc.filename.split('.')[-1]}")

@documents_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('documents.index'))
        
    doc = Document.query.get_or_404(id)
    
    # Helper to remove file from disk
    try:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
        os.remove(os.path.join(upload_folder, doc.filename))
    except Exception as e:
        print(f"Error deleting file: {e}")
        
    db.session.delete(doc)
    db.session.commit()
    
    flash('Documento removido.', 'success')
    return redirect(url_for('documents.index'))

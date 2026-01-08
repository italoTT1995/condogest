from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models.expense import Expense
from app import db
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/transparency')
@login_required
def transparency():
    from flask import session
    condo_id = session.get('active_condo_id')
    
    # Only get expenses from current month for default view, or filter?
    # For now, get last 50 expenses for ACTIVE CONDO
    expenses = Expense.query.filter_by(condo_id=condo_id).order_by(Expense.date_incurred.desc()).limit(50).all()
    
    # Calculate totals by category for chart
    categories = {}
    total_spent = 0
    for exp in expenses:
        total_spent += exp.amount
        categories[exp.category] = categories.get(exp.category, 0) + exp.amount
        
    return render_template('financial/transparency.html', 
                         expenses=expenses, 
                         categories=categories,
                         total_spent=total_spent)

@financial_bp.route('/expenses/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_expense():
    if request.method == 'POST':
        description = request.form['description']
        category = request.form['category']
        amount = float(request.form['amount'])
        date_str = request.form['date_incurred']
        date_incurred = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        proof_filename = None
        if 'proof' in request.files:
            file = request.files['proof']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
                proof_filename = f"receipt_{uuid.uuid4().hex[:8]}.{ext}"
                
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'receipts')
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, proof_filename))

        from flask import session
        
        expense = Expense(
            description=description,
            category=category,
            amount=amount,
            date_incurred=date_incurred,
            proof_filename=proof_filename,
            created_by=current_user.id,
            condo_id=session.get('active_condo_id')
        )
        db.session.add(expense)
        db.session.commit()
        flash('Despesa registrada com sucesso!', 'success')
        return redirect(url_for('financial.transparency'))
        
    return render_template('financial/new_expense.html')

@financial_bp.route('/expenses/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash('Despesa removida.', 'success')
    return redirect(url_for('financial.transparency'))

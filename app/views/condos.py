from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models.condominium import Condominium
from app.decorators import superuser_required

condos_bp = Blueprint('condos', __name__)

@condos_bp.route('/')
@login_required
@superuser_required
def index():
    condos = Condominium.query.order_by(Condominium.created_at.desc()).all()
    return render_template('admin/condos/index.html', condos=condos)

@condos_bp.route('/new', methods=['GET', 'POST'])
@login_required
@superuser_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        cnpj = request.form.get('cnpj')
        
        condo = Condominium(name=name, address=address, cnpj=cnpj)
        db.session.add(condo)
        db.session.commit()
        
        flash('Condomínio criado com sucesso!', 'success')
        return redirect(url_for('condos.index'))
        
    return render_template('admin/condos/form.html', title="Novo Condomínio")

@condos_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@superuser_required
def edit(id):
    condo = Condominium.query.get_or_404(id)
    
    if request.method == 'POST':
        condo.name = request.form.get('name')
        condo.address = request.form.get('address')
        condo.cnpj = request.form.get('cnpj')
        
        db.session.commit()
        flash('Condomínio atualizado com sucesso!', 'success')
        return redirect(url_for('condos.index'))
        
    return render_template('admin/condos/form.html', title="Editar Condomínio", condo=condo)

@condos_bp.route('/switch/<int:id>')
@login_required
@superuser_required
def switch(id):
    condo = Condominium.query.get_or_404(id)
    session['active_condo_id'] = condo.id
    session['active_condo_name'] = condo.name
    flash(f'Alternado para: {condo.name}', 'info')
    return redirect(url_for('main.index'))

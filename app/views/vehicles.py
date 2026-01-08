from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models.vehicle import Vehicle
from app import db

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/')
@login_required
def index():
    if current_user.is_admin or current_user.is_porteiro:
        # Filter by Active Condo
        from flask import session
        from app.models.user import User
        condo_id = session.get('active_condo_id')
        vehicles = Vehicle.query.join(User).filter(User.condo_id == condo_id).all()
    else:
        vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    return render_template('vehicles/index.html', vehicles=vehicles)

@vehicles_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        plate = request.form['plate'].upper()
        model = request.form['model']
        color = request.form['color']
        user_id = request.form['user_id']
        
        # Check if plate already exists
        existing = Vehicle.query.filter_by(plate=plate).first()
        if existing:
            flash('Erro: Veículo com esta placa já cadastrado.', 'danger')
            return redirect(url_for('vehicles.create'))

        vehicle = Vehicle(
            user_id=user_id,
            plate=plate,
            model=model,
            color=color
        )
        db.session.add(vehicle)
        db.session.commit()
        flash('Veículo cadastrado com sucesso!')
        return redirect(url_for('vehicles.index'))
    
    # Pass residents to the template for the dropdown
    from app.models.user import User
    from flask import session
    residents = User.query.filter_by(role='resident', condo_id=session.get('active_condo_id')).all()
    return render_template('vehicles/form.html', residents=residents)

@vehicles_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    flash('Veículo removido.')
    return redirect(url_for('vehicles.index'))

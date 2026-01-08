from app import create_app, db
from app.models.user import User, Role

app = create_app()

with app.app_context():
    print("Migrating Users to Dynamic Roles...")
    
    # 1. Ensure Roles Exist
    roles_map = {
        'admin': 'Admin',
        'porteiro': 'Porteiro',
        'zelador': 'Zelador',
        'morador': 'Morador',
        'resident': 'Morador', # handle english default if any
        'sindico': 'Síndico'
    }
    
    # Cache Role IDs
    db_roles = {}
    for r_name in set(roles_map.values()):
        role = Role.query.filter_by(name=r_name).first()
        if not role:
            print(f"Creating missing role: {r_name}")
            role = Role(name=r_name, description=f"Cargo padrão {r_name}")
            db.session.add(role)
            db.session.commit()
        db_roles[r_name] = role

    # 2. Update Users
    users = User.query.filter(User.role_id == None).all()
    count = 0
    
    for user in users:
        old_role = user.role.lower() if user.role else 'resident'
        
        # Map old string to new Role Name
        target_role_name = None
        if old_role == 'admin': target_role_name = 'Admin'
        elif old_role == 'porteiro': target_role_name = 'Porteiro'
        elif old_role == 'zelador': target_role_name = 'Zelador'
        elif old_role in ['sindico', 'síndico']: target_role_name = 'Síndico'
        else: target_role_name = 'Morador' # Default
        
        target_role = db_roles.get(target_role_name)
        if target_role:
            user.user_role = target_role
            count += 1
            print(f"Migrated user '{user.username}' ({old_role}) -> Role '{target_role.name}'")

    db.session.commit()
    print(f"Migration complete. Updated {count} users.")

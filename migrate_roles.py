from app import create_app, db
from app.models.user import Role, User
import sqlalchemy

app = create_app()

with app.app_context():
    print("Starting migration...")
    
    # 1. Create Role table
    # We inspect to see if it exists first just in case
    inspector = sqlalchemy.inspect(db.engine)
    if 'role' not in inspector.get_table_names():
        print("Creating 'role' table...")
        Role.__table__.create(db.engine)
    else:
        print("'role' table already exists.")

    # 2. Add 'role_id' column to 'user' table if it doesn't exist
    # SQLite does not support IF NOT EXISTS in ALTER TABLE mostly, so we check columns
    columns = [col['name'] for col in inspector.get_columns('user')]
    if 'role_id' not in columns:
        print("Adding 'role_id' column to 'user' table...")
        with db.engine.connect() as conn:
            # Quote table name "user" for PostgreSQL compatibility
            conn.execute(sqlalchemy.text('ALTER TABLE "user" ADD COLUMN role_id INTEGER REFERENCES role(id)'))
            conn.commit()
    else:
        print("'role_id' column already exists.")

    # 3. Seed Default Roles
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        print("Creating 'Admin' role...")
        admin_role = Role(name='Admin', description='Acesso total ao sistema')
        db.session.add(admin_role)
    
    resident_role = Role.query.filter_by(name='Morador').first()
    if not resident_role:
        print("Creating 'Morador' role...")
        resident_role = Role(name='Morador', description='Acesso restrito ao morador')
        db.session.add(resident_role)

    # 3.1 Create other common roles to show flexibility
    porteiro_role = Role.query.filter_by(name='Porteiro').first()
    if not porteiro_role:
        print("Creating 'Porteiro' role...")
        porteiro_role = Role(name='Porteiro', description='Gestão de visitantes e encomendas')
        db.session.add(porteiro_role)
        
    zelador_role = Role.query.filter_by(name='Zelador').first()
    if not zelador_role:
        print("Creating 'Zelador' role...")
        zelador_role = Role(name='Zelador', description='Gestão de manutenção e áreas comuns')
        db.session.add(zelador_role)

    db.session.commit()
    print("Roles seeded.")

    # 4. Migrate existing users based on old 'role' string
    print("Migrating existing users...")
    users = User.query.all()
    count = 0
    for user in users:
        if not user.role_id:
            if user.role == 'admin':
                user.user_role = admin_role
            else:
                user.user_role = resident_role
            count += 1
            
    db.session.commit()
    print(f"Migrated {count} users to new Role system.")
    print("Migration complete!")

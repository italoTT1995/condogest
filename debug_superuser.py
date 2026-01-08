from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    # Check Admin User
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"User: {admin.username}")
        print(f"Role: {admin.user_role.name if admin.user_role else admin.role}")
        print(f"Is Superuser? {admin.is_superuser}")
        print(f"Condo ID: {admin.condo_id}")
    else:
        print("Admin user not found!")

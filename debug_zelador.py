from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    u = User.query.filter_by(username='zelador').first()
    if u:
        print(f"User: {u.username}")
        print(f"Role (Legacy): {u.role}")
        print(f"Role ID: {u.role_id}")
        if u.user_role:
            print(f"Role Object: {u.user_role.name}")
            print(f"  - Can Concierge: {u.user_role.can_manage_concierge}")
            print(f"  - Can Complaints: {u.user_role.can_manage_complaints}")
    else:
        print("User 'zelador' not found")

from app import create_app, db
from app.models.core import Payment
from app.models.user import User

app = create_app()

with app.app_context():
    print("-" * 50)
    print("DEBUGGING PAYMENTS VISIBILITY")
    print("-" * 50)
    
    payments = Payment.query.all()
    if not payments:
        print("  >> NO PAYMENTS FOUND IN DATABASE.")
    else:
        print(f"  >> Found {len(payments)} payments.")
        for p in payments:
            user = User.query.get(p.user_id)
            user_name = user.username if user else "UNKNOWN ID"
            print(f"  - Payment ID {p.id}: {p.description} (Amount: {p.amount}) -> Assigned to User ID: {p.user_id} ({user_name})")
    
    print("-" * 50)
    
    # Also list all residents to help verify IDs
    print("AVAILABLE USERS (Residents):")
    residents = User.query.all()
    for r in residents:
         role_name = r.user_role.name if r.user_role else r.role
         print(f"  - ID {r.id}: {r.username} (Role: {role_name})")

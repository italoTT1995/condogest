from app import create_app, db
from app.models.user import User
from app.models.visitor import VisitLog
from datetime import datetime

app = create_app()

with app.app_context():
    print("--- Verifying Access History ---")
    
    # 1. Find a user to simulate access
    user = User.query.first()
    if not user:
        print("No users found.")
        exit()
        
    print(f"Simulating access for: {user.username}")
    
    # 2. Create a fake log entry
    log = VisitLog(
        user_id=user.id,
        unit_id=user.unit_id,
        entry_time=datetime.now(),
        access_status='allowed',
        failure_reason='TESTE AUTOMATICO'
    )
    db.session.add(log)
    db.session.commit()
    print("Fake Log Entry Created.")
    
    # 3. Read it back
    latest = VisitLog.query.order_by(VisitLog.id.desc()).first()
    print(f"Latest Log ID: {latest.id}")
    print(f"User: {latest.user.username if latest.user else 'None'}")
    print(f"Status: {latest.access_status}")
    print(f"Timestamp: {latest.entry_time}")
    
    if latest.failure_reason == 'TESTE AUTOMATICO':
        print("SUCCESS: Log verification passed!")
    else:
        print("FAILURE: Log verification failed.")

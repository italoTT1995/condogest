from app import create_app, db
from app.models.lost_found import LostItem
from app.models.user import User
from app.models.core import Unit
import traceback

app = create_app()

with app.app_context():
    print("--- Simulating Lost & Found Index View ---")
    
    # Mock condo_id (assuming 1 exists, usually active condo)
    condo_id = 1 
    print(f"Using condo_id: {condo_id}")

    try:
        print("Querying Unclaimed Items...")
        items_unclaimed = LostItem.query.filter_by(condo_id=condo_id, status='unclaimed').order_by(LostItem.found_at.desc()).all()
        print(f"Found {len(items_unclaimed)} unclaimed items.")
        for item in items_unclaimed:
            print(f" - {item.description} (Found at: {item.found_at})")
            
        print("\nQuerying Claimed Items...")
        items_claimed = LostItem.query.filter_by(condo_id=condo_id, status='claimed').order_by(LostItem.claimed_at.desc()).limit(20).all()
        print(f"Found {len(items_claimed)} claimed items.")

        print("\nQuerying Residents (User JOIN Unit)...")
        residents = User.query.join(Unit).filter(Unit.condo_id == condo_id).order_by(User.username).all()
        print(f"Found {len(residents)} residents.")
        
    except Exception as e:
        print("CRITICAL FAILURE in View Logic:")
        traceback.print_exc()

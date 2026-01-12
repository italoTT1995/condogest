from pywebpush import VAPIDClaims

# This generates a new keypair
vapid = VAPIDClaims()
print(f"VAPID_PUBLIC_KEY={vapid.public_key}")
print(f"VAPID_PRIVATE_KEY={vapid.private_key}")
print("\nSAVE THESE IN YOUR RENDER ENVIRONMENT VARIABLES AND config.py!")


import sys
import os

# Ensure app can be imported
sys.path.append(os.getcwd())

from app.core.security import get_password_hash, verify_password

try:
    print("Testing password hash...")
    pw_hash = get_password_hash("admin123")
    print(f"Hash: {pw_hash}")
    
    print("Testing password verify...")
    is_valid = verify_password("admin123", pw_hash)
    print(f"Valid: {is_valid}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

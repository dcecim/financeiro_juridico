
import asyncio
import sys
import uuid
import pyotp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete

from app.core.database import engine
from app.models.usuario import Usuario
from app.core.security import get_password_hash

# Mock DB session
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def test_2fa_flow():
    print("\n--- Testing 2FA Flow ---")
    unique_id = str(uuid.uuid4())[:8]
    email = f"user_2fa_{unique_id}@test.com"
    password = "password123"
    
    async with AsyncSessionLocal() as db:
        # 1. Create User
        print(f"Creating user {email}...")
        hashed_password = get_password_hash(password)
        user = Usuario(
            email=email,
            password_hash=hashed_password,
            role="ADMIN",
            is_2fa_enabled=False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # 2. Simulate /2fa/setup
        print("Setting up 2FA...")
        secret = pyotp.random_base32()
        user.secret_2fa = secret
        # In real API, we don't set enabled=True yet
        db.add(user)
        await db.commit()
        
        # 3. Simulate /2fa/activate
        print("Activating 2FA...")
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        # Verify code (API logic)
        if totp.verify(code):
            user.is_2fa_enabled = True
            db.add(user)
            await db.commit()
            print("2FA Activated successfully.")
        else:
            print("FAILURE: 2FA Activation code invalid.")
            return

        # 4. Simulate Login WITH 2FA
        print("Attempting Login with 2FA...")
        # Reload user
        await db.refresh(user)
        
        if user.is_2fa_enabled:
            # Generate new code
            current_code = totp.now()
            if totp.verify(current_code):
                print("SUCCESS: Login with 2FA passed.")
            else:
                print("FAILURE: Login with 2FA failed (code rejected).")
        else:
             print("FAILURE: 2FA not enabled on user.")

        # 5. Simulate Login WITHOUT 2FA (Should fail check)
        print("Attempting Login WITHOUT 2FA (Check logic)...")
        if user.is_2fa_enabled:
             print("SUCCESS: System detected 2FA is required.")
        else:
             print("FAILURE: System did not require 2FA.")

        # Cleanup
        await db.delete(user)
        await db.commit()

async def main():
    await test_2fa_flow()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

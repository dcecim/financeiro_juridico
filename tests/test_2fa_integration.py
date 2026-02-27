import httpx
import pyotp
import json

BASE_URL = "http://localhost:8000"

def test_2fa_flow():
    email = "test_frontend@example.com"
    password = "password123"
    
    client = httpx.Client()
    
    # 1. Register (or login if exists)
    try:
        resp = client.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "role": "ADMIN"
        })
        if resp.status_code == 200:
            print("User registered")
        elif resp.status_code == 400 and "Email already registered" in resp.text:
            print("User already exists")
        else:
            print(f"Register failed: {resp.text}")
            return
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # 2. Login (should succeed initially)
    resp = client.post(f"{BASE_URL}/auth/token", data={
        "username": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"Initial login failed: {resp.text}")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Initial login successful")

    # 3. Setup 2FA
    resp = client.post(f"{BASE_URL}/auth/2fa/setup", headers=headers)
    if resp.status_code != 200:
        # Check if already enabled
        if "2FA is already enabled" in resp.text:
             print("2FA already enabled, skipping setup")
             # Try to disable first to test setup
             # But we need OTP to disable... assume we continue
        else:
            print(f"Setup 2FA failed: {resp.text}")
            return
    else:
        secret = resp.json()["secret"]
        print(f"2FA Setup successful, secret: {secret}")

        # 4. Activate 2FA
        totp = pyotp.TOTP(secret)
        code = totp.now()
        resp = client.post(f"{BASE_URL}/auth/2fa/activate?otp_code={code}", headers=headers)
        if resp.status_code == 200:
            print("2FA Activated")
        else:
            print(f"2FA Activation failed: {resp.text}")
            return

    # 5. Login without OTP (should fail with "2FA code required")
    resp = client.post(f"{BASE_URL}/auth/token", data={
        "username": email,
        "password": password
    })
    if resp.status_code == 401 and "2FA code required" in resp.text:
        print("Login without OTP correctly failed")
    else:
        print(f"Login without OTP unexpected result: {resp.status_code} {resp.text}")
        # If it succeeds, maybe 2FA activation failed silently? Or logic is wrong.
        return

    # 6. Login with OTP (should succeed)
    # If we reached here, 2FA is enabled.
    # We need the secret. If we just set it up, we have 'secret' variable.
    # If it was already enabled, we don't have the secret, so we can't generate OTP.
    if 'secret' in locals():
        totp = pyotp.TOTP(secret)
        code = totp.now()
        # Note: query param for otp_code
        resp = client.post(f"{BASE_URL}/auth/token?otp_code={code}", data={
            "username": email,
            "password": password
        })
        if resp.status_code == 200:
            print("Login with OTP successful")
        else:
             print(f"Login with OTP failed: {resp.text}")

if __name__ == "__main__":
    test_2fa_flow()

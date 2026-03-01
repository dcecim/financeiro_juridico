import httpx

url = "http://localhost:8000/auth/token"
data = {
    "username": "admin@financas.com",
    "password": "admin123"
}

try:
    response = httpx.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

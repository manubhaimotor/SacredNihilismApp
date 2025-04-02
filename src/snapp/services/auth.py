import requests
import base64
import json


# Firebase Web API Key
FIREBASE_WEB_API_KEY = "AIzaSyAse0jNdrq0LBu33fJc6WzoF6XovI2OyDQ"

def sign_in_with_email_password(email, password):
    """Sign in a user using Firebase Authentication REST API."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"

    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        user_data = response.json()
        print("✅ Successfully signed in:", user_data)
        return user_data["idToken"]
    else:
        print("❌ Error signing in:", response.json())
        return None

def extract_user_id(id_token):
    """Decode Firebase JWT to extract the user_id (UID)."""
    try:
        payload = id_token.split('.')[1] + '=='
        decoded = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded)
        return payload_data.get('user_id')
    except Exception as e:
        print("❌ Failed to extract user_id:", e)
        return None
    
def sign_up_with_email_password(email, password):
    API_KEY = "AIzaSyAse0jNdrq0LBu33fJc6WzoF6XovI2OyDQ"
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)

    # 🔍 Print full error details for debugging
    print("📤 Firebase Signup Request:", payload)
    print("📥 Firebase Response:", response.status_code, response.text)

    if response.status_code == 200:
        return response.json()["idToken"]
    else:
       error_msg = response.json().get("error", {}).get("message", "UNKNOWN_ERROR")
       print(f"❌ Sign-up failed: {error_msg}")
       return None


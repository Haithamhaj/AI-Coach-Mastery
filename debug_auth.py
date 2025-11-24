
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("FIREBASE_API_KEY")
project_id = os.getenv("FIREBASE_PROJECT_ID")

print(f"DEBUG: API Key loaded: {'Yes' if api_key else 'No'}")
print(f"DEBUG: Project ID loaded: {'Yes' if project_id else 'No'}")

if not api_key:
    print("ERROR: FIREBASE_API_KEY is missing in .env")
    exit(1)

# Test Sign Up Endpoint with a dummy email (dry run if possible, or just check if endpoint accepts key)
# We'll try to sign up a random test user to see the specific error
import random
import string

random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
test_email = f"test_{random_str}@example.com"
test_pass = "password123"

SIGN_UP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"

payload = {
    "email": test_email,
    "password": test_pass,
    "returnSecureToken": True
}

print(f"\nAttempting to sign up test user: {test_email}")

try:
    response = requests.post(SIGN_UP_URL, json=payload)
    data = response.json()
    
    if response.status_code == 200:
        print("SUCCESS: Sign up successful!")
        print(f"User ID: {data.get('localId')}")
        # Clean up would require admin sdk, but for now we just want to know if it works
    else:
        print(f"FAILURE: Status Code {response.status_code}")
        error = data.get('error', {})
        print(f"Error Code: {error.get('code')}")
        print(f"Error Message: {error.get('message')}")
        
        if error.get('message') == "OPERATION_NOT_ALLOWED":
            print("\n>>> DIAGNOSIS: Email/Password provider is NOT enabled in Firebase Console.")
            print(">>> ACTION: Go to Firebase Console -> Authentication -> Sign-in method -> Enable Email/Password.")
        elif error.get('message') == "API_KEY_INVALID":
            print("\n>>> DIAGNOSIS: The API Key in .env is invalid.")
            print(">>> ACTION: Check your FIREBASE_API_KEY in .env.")

except Exception as e:
    print(f"EXCEPTION: {str(e)}")

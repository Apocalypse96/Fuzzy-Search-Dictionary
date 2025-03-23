import bcrypt
import requests
import json

def test_login(username, password):
    print(f"Testing login for: {username} / {password}")
    
    # Create form data
    data = {
        'username': username,
        'password': password
    }
    
    try:
        response = requests.post('http://localhost:8000/token', data=data)
        if response.status_code == 200:
            print("Login successful!")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"Login failed with status code: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error during request: {e}")
        return False

if __name__ == "__main__":
    test_login("admin", "password")

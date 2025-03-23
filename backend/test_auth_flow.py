import requests
import json
import time

def test_auth_flow():
    base_url = 'http://localhost:8000'
    session = requests.Session()
    
    print("1. Testing login...")
    login_data = {
        'username': 'admin',
        'password': 'password'
    }
    
    login_response = session.post(f'{base_url}/token', data=login_data)
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code == 200:
        print("Login successful!")
        print(json.dumps(login_response.json(), indent=2))
        
        # Check cookies
        print("\nCookies after login:")
        for cookie in session.cookies:
            print(f"{cookie.name}: {cookie.value[:10]}... (expires: {cookie.expires})")
            
        # Test debug endpoint
        print("\n2. Testing debug endpoint...")
        debug_response = session.get(f'{base_url}/debug-auth')
        print(f"Debug endpoint status: {debug_response.status_code}")
        if debug_response.status_code == 200:
            print(json.dumps(debug_response.json(), indent=2))
        
        # Test search endpoint
        print("\n3. Testing search endpoint...")
        search_data = {
            'word': 'python'
        }
        search_response = session.post(
            f'{base_url}/search', 
            json=search_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Search status: {search_response.status_code}")
        if search_response.status_code == 200:
            print("Search successful!")
            print(json.dumps(search_response.json(), indent=2))
        else:
            print(f"Search failed: {search_response.text}")
    else:
        print(f"Login failed: {login_response.text}")

if __name__ == "__main__":
    test_auth_flow()

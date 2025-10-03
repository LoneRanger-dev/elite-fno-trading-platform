import requests
import json
from pprint import pprint

def test_route(url, method='GET', data=None):
    print(f"\nTesting {method} {url}")
    try:
        if method == 'GET':
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if len(response.content) > 1000:
            print(f"Content Length: {len(response.content)} bytes")
        else:
            try:
                print(f"Content: {response.content.decode()}")
            except:
                print(f"Content: {response.content}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

base_url = "http://127.0.0.1:5000"

# Test GET routes
get_routes = [
    "/",
    "/premium-landing",
    "/landing-original",
    "/internal/test_signal",
    "/pro-setups",
    "/dashboard",
    "/paper-trading",
    "/api/paper-trading/portfolio/user_001"
]

# Test POST routes
post_routes = [
    ("/api/subscribe", {"user_id": "user_001", "plan_type": "premium"}),
    ("/api/paper-trading/create-portfolio", {"user_id": "user_001", "initial_balance": 100000.0}),
    ("/api/paper-trading/place-order", {
        "user_id": "user_001",
        "symbol": "NIFTY",
        "quantity": 50,
        "price": 19500,
        "order_type": "MARKET"
    }),
    ("/start_trial", {"email": "test@example.com", "phone": "1234567890"})
]

print("Testing GET routes...")
for route in get_routes:
    test_route(f"{base_url}{route}")

print("\nTesting POST routes...")
for route, data in post_routes:
    test_route(f"{base_url}{route}", method='POST', data=data)
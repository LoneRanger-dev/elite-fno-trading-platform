import requests
import json
import socket
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import time

def wait_for_server(url, timeout=30):
    """Wait for server to become available"""
    start_time = time.time()
    while True:
        try:
            response = requests.get(url)
            return True
        except requests.exceptions.RequestException:
            if time.time() - start_time > timeout:
                print(f"Server at {url} did not become available within {timeout} seconds")
                return False
            time.sleep(1)

def test_route(url, method='GET', data=None, timeout=5):
    """Test a route with detailed error handling"""
    print(f"\nTesting {method} {url}")
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.1)
        session.mount('http://', HTTPAdapter(max_retries=retries))
        
        if method == 'GET':
            response = session.get(url, timeout=timeout)
        else:
            response = session.post(url, json=data, timeout=timeout)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        content_length = len(response.content)
        print(f"Content Length: {content_length} bytes")
        
        if content_length < 1000:
            try:
                print(f"Content: {response.content.decode()}")
            except:
                print(f"Content: {response.content}")
        
        return response
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {str(e)}")
        # Try to determine if the port is actually open
        port = int(url.split(':')[-1].split('/')[0])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            print(f"Port {port} is open but request failed")
        else:
            print(f"Port {port} is not open")
        sock.close()
    except requests.exceptions.Timeout:
        print(f"Request timed out after {timeout} seconds")
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    return None

base_url = "http://127.0.0.1:5000"

# Wait for server to be available
print("Waiting for server to become available...")
if not wait_for_server(base_url):
    print("Server not available, exiting")
    exit(1)

print("Server is available, starting tests...")

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

print("\nTesting GET routes...")
for route in get_routes:
    test_route(f"{base_url}{route}")
    time.sleep(0.5)  # Small delay between requests

print("\nTesting POST routes...")
for route, data in post_routes:
    test_route(f"{base_url}{route}", method='POST', data=data)
    time.sleep(0.5)  # Small delay between requests
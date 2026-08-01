import sys
import time
import requests
import urllib.request
import urllib.error
import json

def wait_for_service(url, name, timeout=30):
    print(f"Waiting for {name} at {url} to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                if response.status in (200, 404, 401, 403):  # Any valid response means it's up
                    print(f"OK: {name} is up.")
                    return True
        except urllib.error.URLError as e:
            pass
        except Exception:
            pass
        time.sleep(1)
    print(f"FAILED: {name} failed to start within {timeout} seconds.")
    return False

def test_backend_health():
    try:
        response = requests.get("http://localhost:8000/api/health")
        response.raise_for_status()
        if response.json().get("status") == "ok":
            print("OK: Backend Health Check: OK")
            return True
        else:
            print("FAILED: Backend Health Check: FAILED (Unexpected response)")
            return False
    except Exception as e:
        print(f"FAILED: Backend Health Check: FAILED ({e})")
        return False

def test_database_connection():
    try:
        response = requests.post("http://localhost:8000/api/sessions")
        response.raise_for_status()
        session_id = response.json().get("id")
        if session_id:
            print("OK: Database Connection: OK (Session created)")
            return session_id
        else:
            print("FAILED: Database Connection: FAILED (No session ID returned)")
            return None
    except Exception as e:
        print(f"FAILED: Database Connection: FAILED ({e})")
        return None

def test_orchestration(session_id):
    try:
        payload = {
            "session_id": session_id,
            "message": "Hello! What is Lenny's growth framework?"
        }
        response = requests.post("http://localhost:8000/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        if "answer" in data:
            print("OK: Orchestration & LLM Connection: OK (Response received)")
            print(f"   Response snippet: {data['answer'][:100]}...")
            return True
        else:
            print("FAILED: Orchestration & LLM Connection: FAILED (No answer in response)")
            return False
    except Exception as e:
        print(f"FAILED: Orchestration & LLM Connection: FAILED ({e})")
        return False

def main():
    if not wait_for_service("http://localhost:8000/api/health", "Backend"):
        sys.exit(1)
    if not wait_for_service("http://localhost:5173", "Frontend"):
        sys.exit(1)

    print("\n--- Running Tests ---")
    if not test_backend_health():
        sys.exit(1)
    
    session_id = test_database_connection()
    if not session_id:
        sys.exit(1)
        
    if not test_orchestration(session_id):
        sys.exit(1)
        
    print("\nDONE: All components are connected and functioning correctly.")

if __name__ == "__main__":
    main()

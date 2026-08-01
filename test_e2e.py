import requests
import json
import uuid
import time

BACKEND_URL = "http://localhost:8000/api"

def test_chat(message: str, expected_skill: str):
    print(f"Testing message: '{message}'")
    
    # 1. Create a session first
    sess_res = requests.post(f"{BACKEND_URL}/sessions")
    sess_res.raise_for_status()
    session_id = sess_res.json()["id"]
    
    payload = {
        "session_id": session_id,
        "message": message
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=60)
        elapsed = time.time() - start_time
        if not response.ok:
            print(f"  -> ERROR: {response.status_code} - written to err.txt")
            with open("err.txt", "w") as ef:
                ef.write(response.text)
            return False, response.text
        
        data = response.json()
        
        skill = data.get("skill")
        print(f"  -> Received skill: {skill}")
        print(f"  -> Answer preview: {data.get('answer', '')[:50]}...")
        print(f"  -> Time taken: {elapsed:.2f}s")
        
        if skill == expected_skill:
            print("  -> PASSED")
            return True, data
        else:
            print(f"  -> FAILED: Expected {expected_skill}, got {skill}")
            return False, data
            
    except Exception as e:
        print(f"  -> ERROR: {str(e)}")
        return False, str(e)

def run_tests():
    # Wait to ensure server is ready
    try:
        requests.get(f"{BACKEND_URL}/docs", timeout=5)
        print("Backend is reachable.\n")
    except Exception as e:
        print(f"Backend is not reachable: {e}")
        return

    tests = [
        ("What did Lenny say about product-market fit?", "qa"),
        ("Write a Ship30for30 essay on product-led growth", "ship30"),
        ("Fix this FastAPI async SQLAlchemy session bug", "pi_code")
    ]
    
    results = []
    for msg, expected in tests:
        success, data = test_chat(msg, expected)
        results.append({
            "message": msg,
            "expected_skill": expected,
            "success": success,
            "data": data
        })
        print("-" * 40)
        
    with open("e2e_results.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    run_tests()

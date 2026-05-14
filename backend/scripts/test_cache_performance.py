import time
import requests
import statistics

BASE_URL = "http://127.0.0.1:8000"

def measure_request(url, headers):
    start = time.perf_counter()
    resp = requests.get(url, headers=headers)
    end = time.perf_counter()
    return (end - start) * 1000, resp.status_code

def test_performance():
    print("🚀 Starting Cache Performance Test...")
    
    # 1. Login to get token
    print("🔑 Logging in...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@example.com", "password": "admin"})
    if login_resp.status_code != 200:
        print("❌ Login failed. Make sure the server is running and seeded.")
        return
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    url = f"{BASE_URL}/students/"
    
    # 2. First request (Cache Miss)
    print("📥 First request (Should be Cache MISS)...")
    dur1, status = measure_request(url, headers)
    print(f"⏱️  Duration: {dur1:.2f}ms (Status: {status})")
    
    # 3. Multiple requests (Cache Hits)
    print("\n📥 Subsequent requests (Should be Cache HITS)...")
    durations = []
    for i in range(5):
        dur, _ = measure_request(url, headers)
        durations.append(dur)
        print(f"⏱️  Request {i+1}: {dur:.2f}ms")
    
    avg_hit = statistics.mean(durations)
    improvement = (dur1 - avg_hit) / dur1 * 100
    
    print("\n📊 Performance Summary:")
    print(f"  - First Request (DB): {dur1:.2f}ms")
    print(f"  - Average Hit (Redis): {avg_hit:.2f}ms")
    print(f"  - Speed Improvement: {improvement:.1f}%")
    
    if improvement > 0:
        print("\n✅ Cache-Aside Pattern successfully demonstrated!")
    else:
        print("\n⚠️ No significant improvement detected. Is Redis running?")

if __name__ == "__main__":
    test_performance()

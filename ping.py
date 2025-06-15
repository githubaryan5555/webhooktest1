import os
import requests
import time
import concurrent.futures

# Read cookie from environment variable
ROBLOSECURITY = os.getenv("cookie")
if not ROBLOSECURITY:
    print("ERROR: Set your .ROBLOSECURITY cookie as env var 'cookie' first!")
    exit(1)

# Create a requests session and set the Roblox security cookie properly
session = requests.Session()
session.cookies.set(".ROBLOSECURITY", ROBLOSECURITY, domain=".roblox.com", path="/")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.roblox.com",
    "Accept": "application/json",
}

# Function to get fresh CSRF token for session (needed for POST requests)
def get_csrf_token():
    resp = session.post("https://auth.roblox.com/v2/logout", headers=HEADERS)
    token = resp.headers.get("x-csrf-token")
    if token:
        HEADERS["x-csrf-token"] = token
        return True
    return False

# Check authentication status before continuing
def is_authenticated():
    resp = session.get("https://www.roblox.com/mobileapi/userinfo", headers=HEADERS)
    if resp.status_code == 200:
        print("[INFO] Authentication success!")
        return True
    else:
        print(f"[ERROR] Authentication failed! Status: {resp.status_code} - {resp.text}")
        return False

# Function to follow a single user by ID
def follow_user(user_id):
    url = f"https://friends.roblox.com/v1/users/{user_id}/follow"
    retries = 5
    for attempt in range(retries):
        try:
            resp = session.post(url, headers=HEADERS)
            if resp.status_code == 200:
                print(f"[SUCCESS] Followed user {user_id}")
                return True
            elif resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", "1"))
                print(f"[RATE LIMIT] User {user_id} - Waiting {wait}s before retry")
                time.sleep(wait)
            elif resp.status_code == 403:
                # CSRF token missing or expired, refresh it
                print(f"[CSRF] Refreshing token for user {user_id}")
                if get_csrf_token():
                    continue
                else:
                    print(f"[FAILED] Could not refresh CSRF token for user {user_id}")
                    return False
            elif resp.status_code == 401:
                print(f"[FAILED] User {user_id} - Unauthorized (check cookie!)")
                return False
            else:
                print(f"[FAILED] User {user_id} - Status {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            print(f"[EXCEPTION] User {user_id} - {e}")
            time.sleep(1)
    print(f"[GIVE UP] User {user_id} after {retries} retries")
    return False

def main():
    if not is_authenticated():
        print("Fix your .ROBLOSECURITY cookie and try again.")
        return
    
    # Get initial CSRF token before starting
    if not get_csrf_token():
        print("Failed to get CSRF token, aborting.")
        return

    user_ids = range(1, 501)  # User IDs 1 to 500
    
    # Use ThreadPoolExecutor for concurrency (10 threads)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(follow_user, user_ids))
    
    print(f"Done. Successfully followed {sum(results)} users out of {len(user_ids)}.")

if __name__ == "__main__":
    main()

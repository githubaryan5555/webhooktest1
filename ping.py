import requests
import threading
import time
import random

ROBLOSECURITY = (
    "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"
    # your full cookie here...
)

START_USER_ID = 1
END_USER_ID = 500
MAX_THREADS = 5  # Chill mode
MAX_RETRIES = 5

session = requests.Session()
session.cookies.set(".ROBLOSECURITY", ROBLOSECURITY)

thread_limiter = threading.BoundedSemaphore(MAX_THREADS)

def get_csrf_token():
    url = f"https://friends.roblox.com/v1/users/{START_USER_ID}/follow"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = session.post(url, headers=headers)
    if resp.status_code == 403 and "x-csrf-token" in resp.headers:
        return resp.headers["x-csrf-token"]
    return None

def follow_user(user_id):
    thread_limiter.acquire()
    try:
        url = f"https://friends.roblox.com/v1/users/{user_id}/follow"
        headers = {"User-Agent": "Mozilla/5.0"}
        retries = 0
        csrf_token = None

        while retries < MAX_RETRIES:
            if csrf_token:
                headers["x-csrf-token"] = csrf_token
            resp = session.post(url, headers=headers)

            if resp.status_code == 200:
                print(f"[SUCCESS] Followed user {user_id}")
                break
            elif resp.status_code == 403 and not csrf_token:
                # Get token once if missing
                csrf_token = get_csrf_token()
            elif resp.status_code == 429:
                wait_time = 2 ** retries + random.uniform(0, 1)  # Exponential backoff + jitter
                print(f"[RATE LIMIT] User {user_id} - Waiting {wait_time:.2f}s before retrying...")
                time.sleep(wait_time)
            else:
                print(f"[FAILED] User {user_id} - Status {resp.status_code} - Response: {resp.text}")
                break

            retries += 1
        else:
            print(f"[GIVE UP] User {user_id} after {MAX_RETRIES} retries.")

    except Exception as e:
        print(f"[ERROR] User {user_id} - Exception: {e}")
    finally:
        thread_limiter.release()

def main():
    threads = []
    for user_id in range(START_USER_ID, END_USER_ID + 1):
        t = threading.Thread(target=follow_user, args=(user_id,))
        t.start()
        threads.append(t)
        time.sleep(random.uniform(0.2, 0.5))  # Random delay between starting threads

    for t in threads:
        t.join()

    print("Done following users 1 to 500!")

if __name__ == "__main__":
    main()

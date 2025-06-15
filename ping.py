import requests
from threading import Thread, BoundedSemaphore
from queue import Queue
import time

# Your Roblox .ROBLOSECURITY cookie goes here — get it from your browser
ROBLOSECURITY = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhAB.CF1F7D8AF5BC575CEEC93ED3CC538DF6B09BDA559A47955ADAEF41285E50FFC11A304E63CDEE4541FDB8CDFAADEEFAB08174D25756C5C166810E8B9A61B3303F5179723CAC07399D6DB6D16143F165B7BEAC1FD7CE0A13379AE79D07B09F6E5DB62675767734421BAA2EE4A6B5A5074968C0C3D3F1BB18F15E956B756A9096A95D7B824B8ABBD32F1DC84890C04003399130D21111ACD1FD46DA7C83C69D52E118D0673A33CE943E7CE3E51DBF0088E573EF22988E7F052C2B11CA2EE7B8012772AD0E3899A563A85BFD5493B0B7736536D865E38C5E8172249BFA88E9CCE876FB8ABF995F0470AD202B8565DA6080DED3116B9DA83154C6EE31C9C1ADF19E67203004BD4ECEEE3039937D2EBFC9E170E9269DAF5C51B20AC29A1BA7A8F4D9F22917FBE41CFD806584D46E400C8A8CB2320D369C9FD3DD32805F27B7FCAA2319A7C50B21EF12F4DE3AFB8B9E5167F9DC6607856242A42006F9180042187AC007241B82D260E7A31F030D8DE112931D7DAEAE38166EF6A279E47072D0F2647091993C4EA78922B10C40116850C695287493F1898B447CFA29CDA6A505DE14EDDEC587858E3CE27FEA3C5A7F335B6A47BE727815F5B322F5A7EF13D6E3234406313F8E3DE1600DDCEC683CC9814B429D43D7FC8789656B97013688CFC17AA9659A567D0999891B29E25A83E13919DED078BC9E3EEB0F23A95E558F84FC3510425E8986FD5ED164EBEB2B2B80A27DB1BCAEF6136277CDCAEA190AFA875218F889B4D2BE2556D352969EC5CCAE124D5B60CD455CB79A042093AD5DAF3DC7BB86BE800A24266C3A6AF52644B5203366930B90AC1B8B7967A5C3B3CD31F1E493E9EB5C9AD15193314D30E36E88FF71C06CB0CB799B203550708B60167F38CF84164CA6B1BFE94F7E1E547C5113641524B4EAAA15ACB893A8DFCAE4162750B72458F7B6B6936AA0F5CD5756E2B72AB0E1358C2903116B40A39EB8E3C4D72FB91A20D193E2DFFD4860380EC91CC7E91DC6EAD91051D8CCFAC0E7C6AB3811144F9CBD90993C2C00E9A7750996F3F3A17CF70EEAAEA6D114E052114CB45381B5BC9F30925456F70C3C3B27AF7F11CEA4D896B9C439FD47A12F"

# Max number of threads for concurrency
MAX_THREADS = 20

# Range of user IDs to follow
START_USER_ID = 1
END_USER_ID = 500

# Threading semaphore to limit concurrency
semaphore = BoundedSemaphore(MAX_THREADS)

# Session with cookie
session = requests.Session()
session.cookies.set('.ROBLOSECURITY', ROBLOSECURITY)

def get_csrf_token():
    """Get fresh CSRF token by sending a POST with no token and grabbing the header."""
    url = "https://friends.roblox.com/v1/users/1/follow"  # dummy user id 1
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    resp = session.post(url, headers=headers)
    if resp.status_code == 403 and "x-csrf-token" in resp.headers:
        token = resp.headers["x-csrf-token"]
        return token
    else:
        # If we got 200 or other status, no token needed or token already valid
        return None

def follow_user(user_id):
    semaphore.acquire()
    try:
        url = f"https://friends.roblox.com/v1/users/{user_id}/follow"
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        # Get CSRF token (could cache this outside but Roblox tokens expire fast)
        token = get_csrf_token()
        if token:
            headers["x-csrf-token"] = token

        resp = session.post(url, headers=headers)

        # Retry once with token if 403
        if resp.status_code == 403 and token is None:
            token = get_csrf_token()
            if token:
                headers["x-csrf-token"] = token
                resp = session.post(url, headers=headers)

        if resp.status_code == 200:
            print(f"[SUCCESS] Followed user {user_id}")
        else:
            print(f"[FAILED] User {user_id} - Status {resp.status_code} - Response: {resp.text}")

    except Exception as e:
        print(f"[ERROR] User {user_id} - {e}")
    finally:
        semaphore.release()

def main():
    threads = []
    for user_id in range(START_USER_ID, END_USER_ID + 1):
        t = Thread(target=follow_user, args=(user_id,))
        t.start()
        threads.append(t)
        time.sleep(0.05)  # slight delay to avoid instant spamming

    for t in threads:
        t.join()

    print("Done following users 1 to 500!")

if __name__ == "__main__":
    main()

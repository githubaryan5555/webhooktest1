import time
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1383413490399707237/LosTBV_1Bo093VoXYak3k3-2H0ylnffrFHEtq8UBp13E_9DVBZJSGEy7axYVE3oh48_6"

payload = {
    "content": "@everyone Give respect to <@1278508393199435848>. FOR he has sacrificed himself",
    "allowed_mentions": {
        "parse": ["everyone"],
        "users": ["1278508393199435848"]
    }
}

def ping_discord():
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Pinged @everyone and the user!")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    while True:
        ping_discord()
        time.sleep(1)

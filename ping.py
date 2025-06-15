import requests, time

url = "https://discord.com/api/webhooks/1383413490399707237/LosTBV_1Bo093VoXYak3k3-2H0ylnffrFHEtq8UBp13E_9DVBZJSGEy7axYVE3oh48_6"
data = {"content": "@everyone Give respect to <@1278508393199435848> for sacrificing himself."}

while True:
    requests.post(url, json=data)
    time.sleep(0.25)

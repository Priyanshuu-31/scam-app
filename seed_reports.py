import requests
import random
import time

url = "http://127.0.0.1:8000/api/v1/reports"

samples = [
    {"value": "+919876543210", "type": "phone", "description": "Pretending to be bank manager."},
    {"value": "admin-verification-kyc.com", "type": "url", "description": "Phishing link for KYC update."},
    {"value": "payment@upi-verify", "type": "upi", "description": "Asked for QR code scan."},
    {"value": "You won an iPhone 16", "type": "message_text", "description": "SMS scam asking for shipping fee."},
    {"value": "+12025550189", "type": "phone", "description": "IRS/Tax refund scam call."},
]

print("Seeding Reports...")
for s in samples:
    try:
        res = requests.post(url, json=s)
        if res.status_code == 200:
            print(f"Added: {s['value']}")
        else:
            print(f"Failed: {res.text}")
        time.sleep(0.5) 
    except Exception as e:
        print(e)

print("Done.")

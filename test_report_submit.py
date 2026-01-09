import requests
import json

url = "http://127.0.0.1:8000/api/v1/reports"
data = {
    "value": "+919999999999",
    "type": "phone",
    "description": "Test report execution"
}

try:
    print(f"Sending POST to {url}...")
    res = requests.post(url, json=data)
    print(f"Status Code: {res.status_code}")
    print(f"Response Body: {res.text}")
except Exception as e:
    print(f"Request failed: {e}")

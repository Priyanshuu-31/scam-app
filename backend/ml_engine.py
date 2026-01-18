import os
import requests
import time

# Use Hugging Face Inference API to save RAM on free tier
# Fallback to SMS Spam model (reliable)
API_URL = "https://api-inference.huggingface.co/models/mrm8488/bert-tiny-finetuned-sms-spam-detection"
HF_TOKEN = os.environ.get("HF_API_KEY")

def analyze_text(text: str):
    """
    Analyzes text using the Hugging Face Inference API.
    This avoids loading the heavy model into local RAM.
    """
    if not text:
        return {"label": "UNKNOWN", "score": 0.0}

    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    
    payload = {"inputs": text[:512]}

    try:
        # Retry logic for model loading (503 error)
        for _ in range(3):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 503:
                # Model is loading, wait a bit
                print("Model loading on HF... retrying")
                time.sleep(2)
                continue
            
            if response.status_code != 200:
                print(f"HF API Error {response.status_code}: {response.text}")
                # Fallback for demo if model is 410/503
                return {"label": "eRROR", "score": 0.0}
            
            # Successful response
            result = response.json()
            print(f"DEBUG_ML_RESULT: {result}")

            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                # Get the highest scoring label
                top_result = max(result[0], key=lambda x: x['score'])
                
                # Normalize labels for our app
                # The model cybersectony/phishing-email-detection-distilbert_v2.1 often returns 'Phishing' and 'Safe'
                label = top_result['label'].upper()
                print(f"DEBUG_ML_LABEL: {label}")
                
                if label in ["PHISHING", "FRAUD", "SCAM", "MALICIOUS", "LABEL_1"]: 
                     top_result['label'] = "SCAM"
                
                return top_result
            elif isinstance(result, dict) and 'error' in result:
                 print(f"HF API Model Error: {result}")
                 return {"label": "eRROR", "score": 0.0}
            
            return {"label": "UNKNOWN", "score": 0.0}
            
    except Exception as e:
        print(f"ML API Connection Error: {e}")
        return {"label": "UNKNOWN", "score": 0.0}

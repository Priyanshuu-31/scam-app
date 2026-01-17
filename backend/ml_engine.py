try:
    from transformers import pipeline
except ImportError:
    pipeline = None
    print("Warning: transformers module not found. ML features will be disabled.")

import functools

@functools.lru_cache(maxsize=1)
def get_scam_classifier():
    if pipeline is None:
        return None
    try:
        return pipeline("text-classification", model="mshenoda/roberta-spam")
    except Exception as e:
        print(f"Failed to load ML model: {e}")
        return None

def analyze_text(text: str):
    classifier = get_scam_classifier()
    if not classifier:
        return {"label": "UNKNOWN", "score": 0.0}
    
    try:
        result = classifier(text[:512])[0]
        return result
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {"label": "ERROR", "score": 0.0}

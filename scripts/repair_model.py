from transformers import pipeline
import shutil
import os

print("Forcing clean download of 'pippinnie/scam_text_classifier'...")

try:
    # force_download=True will ignore cached files and re-fetch
    classifier = pipeline("text-classification", model="pippinnie/scam_text_classifier", force_download=True)
    print("Download Success!")
    
    # Test it
    res = classifier("You have a package delivery waiting click here")
    print(f"Test Result: {res}")
    
except Exception as e:
    print(f"Failed to fix: {e}")

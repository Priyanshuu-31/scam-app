from transformers import pipeline
import sys

print("Testing Alternative Model (mshenoda/roberta-spam)...")
try:
    classifier = pipeline("text-classification", model="mshenoda/roberta-spam")
    res_scam = classifier("You have a package delivery waiting click here")[0]
    res_ham = classifier("Hey mom, buying milk")[0]
    
    print(f"Scam Input -> {res_scam}")
    print(f"Ham Input -> {res_ham}")
except Exception as e:
    print(f"Error: {e}")

import sys
import os
import asyncio
import random
from datetime import datetime, timedelta

# Ensure we can import from backend
# Assuming this script is run from project root or scripts/ dir
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.database import supabase
from backend.models import EntityType

# Sample data generation
sample_reports = [
    # UPI Scams
    {
        "scammer_identifier": "scammer@okaxis",
        "category": "upi",
        "description": "Asked for payment for a fake OLX job listing.",
        "evidence_urls": ["https://imgur.com/fake_payment1"],
        "status": "verified"
    },
    {
        "scammer_identifier": "fastloan@oksbi",
        "category": "upi",
        "description": "Fake loan approval fee scam.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "win_lottery@paytm",
        "category": "upi",
        "description": "Claimed I won a lottery, asked for tax payment first.",
        "evidence_urls": ["https://imgur.com/lottery_scam"],
        "status": "verified"
    },
    {
        "scammer_identifier": "electricity_bill@upi",
        "category": "upi",
        "description": "Message claiming electricity will be cut off unless bill paid effectively immediately to this UPI.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "fake_charity@okhdfcbank",
        "category": "upi",
        "description": "Pretending to collect for a disaster relief fund.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "refund_support@postbank",
        "category": "upi",
        "description": "Scammer posing as customer support offering a refund.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "shop_payment@ybl",
        "category": "upi",
        "description": "Instagram store scam, took money never delivered clothes.",
        "evidence_urls": ["https://instagram.com/scam_store_proof"],
        "status": "verified"
    },
    {
        "scammer_identifier": "cryptoinvest@upi",
        "category": "upi",
        "description": "Crypto doubling scheme scam.",
        "evidence_urls": [],
        "status": "pending"
    },

    # Phone Scams
    {
        "scammer_identifier": "+919876543210",
        "category": "phone",
        "description": "FedEx package seized scam call. Claimed drugs found in parcel.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "+918888899999",
        "category": "phone",
        "description": "KBC lottery winner call.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "+917777766666",
        "category": "phone",
        "description": "Bank KYC update scam call.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "+1234567890",
        "category": "phone",
        "description": "International call 'one ring' scam.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "+919999900000",
        "category": "phone",
        "description": "Pretending to be a relative in trouble needing money ASAP.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "+916666655555",
        "category": "phone",
        "description": "Job offer scam, asked for registration fee.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "+919000010000",
        "category": "phone",
        "description": "Credit card points redemption scam.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "+918000020000",
        "category": "phone",
        "description": "Customs duty payment for 'gift' from abroad.",
        "evidence_urls": [],
        "status": "pending"
    },

    # URL Scams
    {
        "scammer_identifier": "http://free-iphone-offer.com",
        "category": "url",
        "description": "Phishing site promising free iPhones.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "http://sbi-kyc-update-now.net",
        "category": "url",
        "description": "Fake SBI banking login page.",
        "evidence_urls": ["https://urlscan.io/result/fake_sbi"],
        "status": "verified"
    },
    {
        "scammer_identifier": "http://amazon-big-billion-days-spin.xyz",
        "category": "url",
        "description": "Fake Amazon spin the wheel game.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "http://netflix-subscription-renew.com",
        "category": "url",
        "description": "Netflix payment method update phishing.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "http://part-time-jobs-daily-income.in",
        "category": "url",
        "description": "Task scam website.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "http://crypto-airdrop-claim.org",
        "category": "url",
        "description": "Malicious crypto wallet drainer.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "http://gov-scheme-apply-online.info",
        "category": "url",
        "description": "Fake government scheme application portal.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "http://courier-tracking-update.com",
        "category": "url",
        "description": "Fake courier tracking link asking for small payment.",
        "evidence_urls": [],
        "status": "pending"
    },

    # Message/SMS Scams
    {
        "scammer_identifier": "Dear customer, your electricity will be disconnected tonight.",
        "category": "message_text",
        "description": "Electricity bill scam SMS.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "Your bank account has been blocked. Update PAN immediately.",
        "category": "message_text",
        "description": "Bank account block panic SMS.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "Job offer: Earn 5000 daily working from home. WhatsApp now.",
        "category": "message_text",
        "description": "Generic WFH job scam SMS.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "Rs 5,00,000 credited to your account. Click link to verify.",
        "category": "message_text",
        "description": "Fake credit alert phishing.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "Hi, I am manager from HR. Need staff urgently.",
        "category": "message_text",
        "description": "WhatsApp hiring scam.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "Your package address is incomplete. Update here.",
        "category": "message_text",
        "description": "Delivery address update scam.",
        "evidence_urls": [],
        "status": "pending"
    },

    # Other Scams
    {
        "scammer_identifier": "Posing as Army Officer on OLX",
        "category": "other",
        "description": "Sent fake ID card, asked for advance for car delivery.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "QR Code Scan Scam",
        "category": "other",
        "description": "Asked me to scan QR code to 'receive' money.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "Sextortion Video Call",
        "category": "other",
        "description": "Recorded video call and threatened to upload to social media.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "Fake Investment Advisor Telegram",
        "category": "other",
        "description": "Telegram group promising 10x returns in one week.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "Friend Request from Clone Account",
        "category": "other",
        "description": "Created fake FB profile of my friend and asked for money.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "Tech Support Pop-up",
        "category": "other",
        "description": "Browser locked up with 'Microsoft Support' number.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "Date Scam",
        "category": "other",
        "description": "Met on dating app, asked for expensive gift before meeting.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "Rental Deposit Scam",
        "category": "other",
        "description": "Fake apartment listing, took security deposit and vanished.",
        "evidence_urls": [],
        "status": "verified"
    },
    
    # International Scams (High Risk)
    {
        "scammer_identifier": "+923001234567",
        "category": "phone",
        "description": "WhatsApp call from Pakistan number pretending to be KBC.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "+23480390037",
        "category": "phone",
        "description": "Email/SMS from Nigeria promising inheritance fund.",
        "evidence_urls": [],
        "status": "verified"
    },
    {
        "scammer_identifier": "+923210000000",
        "category": "phone",
        "description": "Unknown video call, potential sextortion.",
        "evidence_urls": [],
        "status": "pending"
    },

    # International Scams (General)
    {
        "scammer_identifier": "+12025550109",
        "category": "phone",
        "description": "Call from USA claiming issues with SSN/Visa.",
        "evidence_urls": [],
        "status": "pending"
    },
    {
        "scammer_identifier": "+447700900077",
        "category": "phone",
        "description": "UK number offering fake remote job.",
        "evidence_urls": [],
        "status": "verified"
    }
]

def seed_data():
    print(f"Starting seed process for {len(sample_reports)} reports...")
    
    if not supabase:
        print("Error: Supabase client not initialized. Check .env file.")
        return

    success_count = 0
    error_count = 0

    for i, report in enumerate(sample_reports):
        try:
            # Spread generation times over the last 30 days
            days_ago = random.randint(0, 30)
            created_at = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
            
            data = {
                "scammer_identifier": report["scammer_identifier"],
                "description": report["description"],
                "evidence_urls": report["evidence_urls"],
                "category": report["category"],
                "status": report["status"],
                "created_at": created_at
            }
            
            supabase.table("reports").insert(data).execute()
            print(f"[{i+1}/{len(sample_reports)}] Added: {report['scammer_identifier']} ({report['category']})")
            success_count += 1
            
        except Exception as e:
            print(f"Error adding {report['scammer_identifier']}: {repr(e)}")
            import traceback
            traceback.print_exc()
            error_count += 1

    print("\n--- Seed Complete ---")
    print(f"Successfully added: {success_count}")
    print(f"Failed: {error_count}")

if __name__ == "__main__":
    seed_data()

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import re
import uuid

from backend.models import RiskScore, RiskLevel, EntityType
from backend.database import supabase
from backend.utils import detect_type, normalize_input, extract_entities
from backend.ml_engine import analyze_text

router = APIRouter()

# --- CONSTANTS & CONFIG ---
MAX_SCORE_COMMUNITY = 70
MAX_SCORE_ML = 60
MAX_SCORE_KEYWORD = 40
CONTEXT_BOOST_SCORE = 30

DANGEROUS_KEYWORDS = [
    "lottery", "winner", "urgent", "expire", "block", "kyc", "bank", 
    "customs", "seized", "cbi", "police", "refund", "tax", "electricity", "cut"
]
OTP_KEYWORDS = ["otp", "code", "pin", "password"]

# --- HELPER FUNCTIONS ---

def get_structural_heuristics(value: str, entity_type: EntityType) -> Dict[str, any]:
    """
    Returns a dict of heuristic signals.
    e.g. {"is_high_risk_country": True, "is_short_url": False}
    """
    signals = {
        "score_impact": 0,
        "reasons": []
    }
    
    clean_val = re.sub(r"[\s\-]", "", value)
    
    if entity_type == EntityType.PHONE:
        # 1. Country Risk
        if clean_val.startswith(("+92", "92", "0092")): # Pakistan
            signals["score_impact"] = 100
            signals["reasons"].append("High-Risk Country Origin (Pakistan)")
        elif clean_val.startswith(("+234", "234")): # Nigeria
            signals["score_impact"] = 100
            signals["reasons"].append("High-Risk Country Origin (Nigeria)")
        elif clean_val.startswith(("+880", "880")): # Bangladesh
            signals["score_impact"] = 90
            signals["reasons"].append("High-Risk Country Origin (Bangladesh)")
        elif clean_val.startswith(("+855", "855", "+62", "62", "+856", "856")): # SE Asia (Cyber slavery hubs)
            signals["score_impact"] = 90
            signals["reasons"].append("High-Risk SE Asia Origin")
        elif clean_val.startswith("+") and not clean_val.startswith("+91"):
            signals["score_impact"] = max(signals["score_impact"], 60)
            signals["reasons"].append("International Number (Caution)")

        # 2. Repeated Digits (e.g. 9999999999) - often fake/burner
        if re.search(r'(\d)\1{5,}', clean_val):
            signals["score_impact"] = max(signals["score_impact"], 40)
            signals["reasons"].append("Suspicious repeated digits")

    elif entity_type == EntityType.URL:
        # 1. Shorteners
        shorteners = ["bit.ly", "tinyurl", "goo.gl", "t.co", "is.gd"]
        if any(s in value.lower() for s in shorteners):
            signals["score_impact"] += 20
            signals["reasons"].append("URL Shortener used (hides destination)")
        
        # 2. IP Address URL
        if re.match(r"https?://\d{1,3}\.\d{1,3}", value):
            signals["score_impact"] += 50
            signals["reasons"].append("Raw IP Address URL (Suspicious)")
            
    elif entity_type == EntityType.UPI:
        # Handler check
        if "@" in value:
            handle = value.split("@")[0]
            if len(handle) < 3:
                signals["reasons"].append("Unusually short UPI handle")
    
    return signals

def calculate_v2_risk_score(reports: List[dict], input_text: str) -> RiskScore:
    """
    The 'Winning' Algorithm implementation.
    """
    # 1. Normalization & Extraction
    normalized_text = normalize_input(input_text)
    entities = extract_entities(normalized_text)
    
    primary_type = detect_type(normalized_text) # Keep primary type for top-level categorization
    
    # 2. Signal Collection
    
    # A. Community Signal (Capped)
    report_count = len(reports)
    # 5 reports = 100, but capped at 70 for the weighted sum (unless overridden)
    community_score_raw = min(report_count * 20, 100)
    community_score_weighted = min(community_score_raw, MAX_SCORE_COMMUNITY) 
    
    # B. Structural Heuristics
    heuristic_signals = get_structural_heuristics(normalized_text, primary_type)
    heuristic_score = heuristic_signals["score_impact"]
    
    # C. Keyword/ML Signal
    keyword_score = 0
    ml_score = 0
    
    # Only run expensive ML if text is long enough or ambiguous
    is_text_heavy = len(normalized_text) > 10 or primary_type == EntityType.MESSAGE_TEXT
    
    found_keywords = [k for k in DANGEROUS_KEYWORDS if k in normalized_text.lower()]
    if found_keywords:
        keyword_score = min(len(found_keywords) * 20, MAX_SCORE_KEYWORD)
    
    if is_text_heavy:
        ml_res = analyze_text(normalized_text)
        if ml_res["label"] in ["SCAM", "SPAM", "LABEL_1"]:
            ml_score = min(ml_res["score"] * 100, MAX_SCORE_ML)
    
    # D. Context Awareness (Multi-vector)
    context_boost = 0
    context_reasons = []
    
    # Has Phone + OTP keywords?
    has_otp_keyword = any(k in normalized_text.lower() for k in OTP_KEYWORDS)
    if entities["phones"] and has_otp_keyword:
        context_boost += CONTEXT_BOOST_SCORE
        context_reasons.append("High Risk: Phone Number + OTP request detected")
        
    # Has URL + Urgency?
    has_urgency = "urgent" in normalized_text.lower() or "expire" in normalized_text.lower()
    if entities["urls"] and has_urgency:
        context_boost += CONTEXT_BOOST_SCORE
        context_reasons.append("High Risk: Link + Urgency detected")
        
    # 3. Calculation
    
    # Base Calculation
    # We take the Maximum of specific overrides OR the Weighted Sum
    
    # Overrides (Absolute Trust)
    # If Heuristic says 100 (e.g. Pakistan Number), we trust it 100%
    if heuristic_score >= 90:
        final_score = heuristic_score
    else:
        # Weighted Sum
        # We sum up the capped components
        # Note: Logic here is additive to catch "Weak signals -> Strong Probability"
        total_raw = community_score_weighted + ml_score + keyword_score + context_boost + heuristic_score
        
        # If we have confirmed community reports, we shouldn't dip too low
        if community_score_raw > 80:
             total_raw = max(total_raw, 80)
             
        final_score = min(total_raw, 100)
        
    # 4. Reason Generation
    reasons = []
    reasons.extend(heuristic_signals["reasons"])
    reasons.extend(context_reasons)
    
    if report_count > 0:
        reasons.append(f"Flagged by {report_count} community reports")
        
    if ml_score > 40:
        reasons.append("AI analysis detected scam intent")
        
    if found_keywords:
        reasons.append(f"Suspicious keywords found: {', '.join(found_keywords[:3])}")
        
    if not reasons and final_score < 30:
        reasons.append("No significant threats detected")
        
    # 5. Action Advice
    action = "Safe to proceed, but stay alert."
    if final_score > 70:
        action = "⛔ DO NOT ACTION. Block this number/sender. Do not click links."
        if primary_type == EntityType.UPI:
            action = "⛔ DO NOT PAY. High risk of fraud detected."
    elif final_score > 30:
        action = "⚠️ Exercise Caution. Verify identity through another channel."
        
    # 6. Confidence & Levels
    # Confidence is high if we have Reports or Strong Heuristics
    confidence = 60 # Base
    if report_count > 2 or heuristic_score > 80:
        confidence = 95
    elif ml_score > 90:
        confidence = 85
    elif context_boost > 0:
        confidence = 80
        
    level = RiskLevel.SAFE
    if final_score > 30:
        level = RiskLevel.CAUTION
    if final_score > 70:
        level = RiskLevel.CRITICAL
        
    return RiskScore(
        value=input_text,
        risk_score=int(final_score),
        level=level,
        report_count=report_count,
        reports=reports,
        confidence_score=confidence,
        reasons=list(set(reasons)), # Dedup
        action_advice=action,
        scan_id=str(uuid.uuid4())
    )

@router.get("/scan", response_model=RiskScore)
async def scan_entity(q: str):
    # 1. Normalize
    normalized_q = normalize_input(q)
    
    # 2. DB Search (Community Intelligence)
    reports = []
    try:
        # Search exact match or partial if text
        if supabase:
            # We try to match the normalized identifier
            # For phones, we might want to also match without country code? 
            # For now, let's stick to simple flexible match
            response = supabase.table("reports").select("*").ilike("scammer_identifier", f"%{normalized_q}%").execute()
            reports = response.data
    except Exception as e:
        print(f"DB Error: {e}")

    # 3. Calculate
    return calculate_v2_risk_score(reports, q)

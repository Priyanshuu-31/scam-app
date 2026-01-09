from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import re

from backend.models import RiskScore, RiskLevel, EntityType
from backend.database import supabase
from backend.utils import detect_type
from backend.ml_engine import analyze_text

router = APIRouter()

def calculate_risk_score(reports: List[dict], value: str) -> RiskScore:
    """
    Calculates a risk score (0-100) based on:
    1. ML Model Analysis (RoBERTa)
    2. Community Report Volume
    3. Keyword Matching
    4. Recency of reports
    """
    ml_result = analyze_text(value)
    ml_score = 0
    
    label = str(ml_result['label']).upper()
    if label in ['LABEL_1', 'SCAM', 'SPAM']:
        ml_score = ml_result['score'] * 100
    elif label == 'LABEL_0':
        ml_score = 0

    count = len(reports)
    report_score = min(count * 20, 100)

    keyword_score = 0
    keywords = [
        "winner", "lottery", "urgent", "bank", "kyc", "block", "verify", "expire",
        "package", "delivery", "shipping", "customs", "click here", "link"
    ]
    if any(k in value.lower() for k in keywords):
        keyword_score = 100

    recency_score = 0
    last_report_date = None
    
    if reports:
        try:
            last_report_date = max(datetime.fromisoformat(r['created_at'].replace('Z', '')) for r in reports)
            if datetime.utcnow() - last_report_date < timedelta(days=7):
                recency_score = 100
        except Exception:
            pass

    entity_type = detect_type(value)
    
    if entity_type in [EntityType.PHONE, EntityType.UPI]:
         final_score = (report_score * 0.7) + (recency_score * 0.2) + (keyword_score * 0.1)
    else:
         final_score = (ml_score * 0.5) + (report_score * 0.3) + (keyword_score * 0.2)
         
         if ml_score < 50 and keyword_score == 100:
             final_score = max(final_score, 75)

    final_score = min(int(final_score), 100)
    
    level = RiskLevel.SAFE
    if final_score > 30:
        level = RiskLevel.CAUTION
    if final_score > 70:
        level = RiskLevel.CRITICAL
        
    return RiskScore(
        value=value,
        risk_score=final_score,
        level=level,
        report_count=count,
        last_reported_at=last_report_date,
        reports=reports
    )

@router.get("/scan", response_model=RiskScore)
async def scan_entity(q: str):
    entity_type = detect_type(q)
    
    reports = []
    try:
        if supabase:
            response = supabase.table("reports").select("*").ilike("scammer_identifier", f"%{q}%").execute()
            reports = response.data
    except Exception as e:
        print(f"DB Error: {e}")

    return calculate_risk_score(reports, q)

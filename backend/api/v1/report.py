from fastapi import APIRouter, HTTPException
from backend.models import ReportIn, EntityType
from backend.database import supabase
from backend.utils import validate_entity_type
from datetime import datetime

router = APIRouter()

@router.post("/reports")
async def create_report(report: ReportIn):
    if not validate_entity_type(report.value, report.type):
        raise HTTPException(
            status_code=400, 
            detail=f"Value '{report.value}' does not match the specified type '{report.type}'"
        )

    try:
        data = {
            "scammer_identifier": report.value,
            "description": report.description,
            "evidence_urls": report.evidence_urls,
            "category": report.type,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        if not supabase:
             raise HTTPException(status_code=503, detail="Database not configured")

        res = supabase.table("reports").insert(data).execute()
        
        return {"status": "success", "data": res.data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/recent")
async def get_recent_reports(limit: int = 10):
    if not supabase:
        return []
    
    try:
        res = supabase.table("reports").select("scammer_identifier, category, description, created_at").order("created_at", desc=True).limit(limit).execute()
        return res.data
    except Exception as e:
        print(f"Error fetching existing reports: {e}")
        return []

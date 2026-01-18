from fastapi import APIRouter
from backend.database import supabase
from datetime import datetime, timedelta
from collections import defaultdict

router = APIRouter()

@router.get("/stats")
async def get_stats():
    if not supabase:
        return {
            "total_reports": 0,
            "categories": [],
            "trend": []
        }
    
    try:
        # 1. Total Reports (Get all for now, optimization later)
        # We'll fetch last 30 days to keep it snappy for the dashboard
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        res = supabase.table("reports").select("category, created_at").gte("created_at", start_date).execute()
        reports = res.data
        
        # Total count (approximation based on last 30 days or we can do a separate count query)
        total = len(reports) 

        # 2. Category Distribution
        cat_counts = defaultdict(int)
        for r in reports:
            # Normalize category
            c = r.get("category", "other") or "other"
            cat_counts[c] += 1
            
        categories_data = [
            {"name": k.title(), "value": v} 
            for k, v in cat_counts.items()
        ]
        
        # 3. 7-Day Trend
        trend_map = defaultdict(int)
        today = datetime.utcnow().date()
        
        # Initialize last 7 days with 0
        dates = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            dates.append(d_str)
            trend_map[d_str] = 0
            
        for r in reports:
            try:
                # Handle ISO format with potential Z
                created_at = r['created_at'].replace('Z', '')
                # Truncate microseconds if present
                if '.' in created_at:
                    created_at = created_at.split('.')[0]
                
                dt = datetime.fromisoformat(created_at).date()
                d_str = dt.strftime("%Y-%m-%d")
                
                if d_str in trend_map:
                    trend_map[d_str] += 1
            except Exception as e:
                # print(f"Date parse error: {e}")
                pass

        trend_data = [{"date": d, "count": trend_map[d]} for d in dates]
        
        return {
            "total_reports": total,
            "categories": categories_data,
            "trend": trend_data
        }
        
    except Exception as e:
        print(f"Stats Error: {e}")
    except Exception as e:
        print(f"Stats Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

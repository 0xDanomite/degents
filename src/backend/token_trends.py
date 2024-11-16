from fastapi import APIRouter, HTTPException
from services.token_trend_service import TokenTrendService
from typing import List, Dict
from datetime import datetime

router = APIRouter()
token_service = TokenTrendService()

@router.get("/api/token-trends")
async def get_token_trends() -> Dict[str, List[Dict]]:
    """Get current token trends"""
    try:
        trends = await token_service.detect_token_trends()
        return {
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tokens/{symbol}")
async def get_token_details(symbol: str) -> Dict:
    """Get details about a specific token"""
    try:
        details = await token_service.get_token_details(symbol.upper())
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add to your main.py or app.py
app.include_router(router)

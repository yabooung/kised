# api/logs.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_log_db
from app.models.logs import APILog, ErrorLog
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/logs/api")
async def get_api_logs(
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_log_db)
):
    query = select(APILog).order_by(APILog.timestamp.desc())
    
    if start_date:
        query = query.where(APILog.timestamp >= start_date)
    if end_date:
        query = query.where(APILog.timestamp <= end_date)
    
    result = await db.execute(query.limit(limit))
    return result.scalars().all()

@router.get("/logs/errors")
async def get_error_logs(
    days: int = 7,
    db: AsyncSession = Depends(get_log_db)
):
    start_date = datetime.utcnow() - timedelta(days=days)
    query = select(ErrorLog)\
        .where(ErrorLog.timestamp >= start_date)\
        .order_by(ErrorLog.timestamp.desc())
    
    result = await db.execute(query)
    return result.scalars().all()
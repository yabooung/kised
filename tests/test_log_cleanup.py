import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text
from scripts.async_log_cleanup import LogCleaner
from core.database import get_log_db

@pytest.fixture
async def log_cleaner():
    return LogCleaner()

@pytest.fixture
async def test_db():
    async with get_log_db() as db:
        yield db
        # 테스트 후 정리
        await db.execute(text("DELETE FROM api_logs"))
        await db.commit()

async def insert_test_logs(db, days_old):
    """테스트용 로그 데이터 삽입"""
    timestamp = datetime.now() - timedelta(days=days_old)
    query = text("""
        INSERT INTO api_logs (method, path, timestamp)
        VALUES (:method, :path, :timestamp)
    """)
    await db.execute(query, {
        "method": "GET",
        "path": "/test",
        "timestamp": timestamp
    })
    await db.commit()

@pytest.mark.asyncio
async def test_cleanup_old_logs(log_cleaner, test_db):
    # 테스트 데이터 준비
    await insert_test_logs(test_db, 35)  # 35일 된 로그
    await insert_test_logs(test_db, 25)  # 25일 된 로그
    
    # 정리 실행
    await log_cleaner.cleanup_old_logs()
    
    # 결과 확인
    result = await test_db.execute(text("SELECT COUNT(*) FROM api_logs"))
    count = result.scalar()
    assert count == 1  # 25일된 로그만 남아있어야 함

@pytest.mark.asyncio
async def test_backup_logs(log_cleaner, test_db):
    # 테스트 데이터 준비
    await insert_test_logs(test_db, 35)
    
    # 백업 실행
    backup_success = await log_cleaner.backup_logs(test_db)
    assert backup_success == True

@pytest.mark.asyncio
async def test_schedule_cleanup(log_cleaner):
    # 스케줄러 테스트
    cleanup_task = asyncio.create_task(log_cleaner.schedule_cleanup())
    await asyncio.sleep(1)  # 잠시 실행
    cleanup_task.cancel()  # 작업 중단
    
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass  # 정상적으로 중단됨

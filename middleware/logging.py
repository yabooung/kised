# middleware/logging.py
import uuid
import time
from fastapi import Request
from app.core.database import get_log_db
from app.models.logs import APILog
import asyncio

class AsyncAPILoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 요청 ID를 request.state에 저장
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            status_code = 500
            raise exc finally:
            # 비동기로 로그 저장
            duration = time.time() - start_time
            log_data = {
                "request_id": request_id,
                "method": request.method,
                "endpoint": str(request.url),
                "response_time": duration * 1000,
                "status_code": status_code,
                "ip_address": request.client.host
            }
            
            # 백그라운드 태스크로 로그 저장
            asyncio.create_task(self.save_log(log_data))
        
        return response

    async def save_log(self, log_data: dict):
        async with get_log_db() as db:
            try:
                db.add(APILog(**log_data))
                await db.commit()
            except Exception as e:
                await db.rollback()
                print(f"로그 저장 실패: {e}")
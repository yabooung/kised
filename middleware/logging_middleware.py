import time
import json
from fastapi import Request
from sqlalchemy.orm import Session
from models.log import APILog
from core.database import get_db

class RequestResponseLogMiddleware:
    async def __call__(self, request: Request, call_next):
        # 시작 시간 기록
        start_time = time.time()
        
        # 요청 정보 수집
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                request_body = await request.json()
                request_body = json.dumps(request_body)
            except:
                request_body = None

        # 응답 처리
        response = await call_next(request)
        
        # 응답 시간 계산
        response_time = (time.time() - start_time) * 1000  # 밀리초로 변환

        # 응답 본문 수집 (필요한 경우)
        response_body = None
        if hasattr(response, "body"):
            try:
                response_body = response.body.decode()
            except:
                response_body = None

        # DB에 로그 저장
        try:
            db: Session = next(get_db())
            log_entry = APILog(
                method=request.method,
                path=str(request.url),
                status_code=response.status_code,
                response_time=response_time,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                request_body=request_body,
                response_body=response_body
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            print(f"로그 저장 실패: {e}")

        return response
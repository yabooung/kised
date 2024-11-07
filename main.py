# main.py
from fastapi import FastAPI
from app.middleware.logging import AsyncAPILoggingMiddleware
from app.api import logs

app = FastAPI(
    title="Reg Finder",
    description="창업진흥원 규제파인더",
    version="1.0.0"
)


# 미들웨어 추가
app.add_middleware(AsyncAPILoggingMiddleware)

# 라우터 추가
app.include_router(logs.router)

@app.on_event("startup")
async def startup_event():
    # 시작 시 필요한 비동기 초기화
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # 종료 시 커넥션 정리
    await main_engine.dispose()
    await log_engine.dispose()
    await redis.close()

# 캐시 사용 예시
@app.get("/cached-data")
@async_cache(expire_seconds=300)
async def get_cached_data():
    # 무거운 비동기 작업
    return {"data": "expensive computation result"}
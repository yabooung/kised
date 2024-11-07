# utils/cache.py
import json
from functools import wraps
from app.core.database import get_redis

def async_cache(expire_seconds: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"cache:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Redis에서 캐시된 결과 확인
            async with get_redis() as redis:
                cached_result = await redis.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
                
                # 결과가 없으면 함수 실행
                result = await func(*args, **kwargs)
                
                # 결과 캐싱
                await redis.setex(
                    cache_key,
                    expire_seconds,
                    json.dumps(result)
                )
                return result
        return wrapper
    return decorator
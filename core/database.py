# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from core.config import settings

# SQL Engines
main_engine = create_async_engine(
    settings.MAIN_DB_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600  # 커넥션 재활용 시간
)

log_engine = create_async_engine(
    settings.LOG_DB_URL,
    echo=False,
    pool_size=3,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Async Session Factories
AsyncMainSession = async_sessionmaker(
    bind=main_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

AsyncLogSession = async_sessionmaker(
    bind=log_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Redis 연결
redis = Redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=10,
    socket_timeout=5,
    socket_connect_timeout=5
)

# Base Model
Base = declarative_base()

# Database Dependencies
@asynccontextmanager
async def get_main_db() -> AsyncSession:
    async with AsyncMainSession() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

@asynccontextmanager
async def get_log_db() -> AsyncSession:
    async with AsyncLogSession() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

# Redis Dependency
@asynccontextmanager
async def get_redis():
    try:
        yield redis
    except Exception as e:
        print(f"Redis error: {e}")
        raise e
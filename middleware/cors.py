# middleware/cors.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from core.config import settings

def add_cors_middleware(app: FastAPI):
    origins = settings.BACKEND_CORS_ORIGINS
    
    if settings.ENV == "development":
        # 개발 환경에서는 더 느슨한 CORS 정책
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # 운영 환경에서는 더 엄격한 CORS 정책
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["Authorization", "Content-Type"],
            expose_headers=["Content-Length"],
            max_age=600,
        )
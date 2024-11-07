# models/logs.py
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from datetime import datetime
from app.core.database import Base

class APILog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    method = Column(String(10))
    endpoint = Column(String(255))
    response_time = Column(Float)
    status_code = Column(Integer)
    ip_address = Column(String(50))
    request_id = Column(String(36))  # 요청 추적용

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    error_type = Column(String(100))
    error_message = Column(String(500))
    stack_trace = Column(String(2000))
    request_id = Column(String(36))
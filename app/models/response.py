from pydantic import BaseModel
from typing import Optional, Any, Dict
from enum import Enum


class ProcessingStatusEnum(str, Enum):
    """Estados de procesamiento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SuccessResponse(BaseModel):
    """Respuesta exitosa genérica"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Respuesta de error genérica"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class ProcessingStatus(BaseModel):
    """Estado de procesamiento"""
    job_id: str
    status: ProcessingStatusEnum
    progress: int  # 0-100
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

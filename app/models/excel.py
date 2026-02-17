from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ExcelUploadRequest(BaseModel):
    """Request para subir archivo Excel"""
    workspace_id: str = Field(..., description="ID del workspace")
    user_id: str = Field(..., description="ID del usuario")
    dashboard_name: Optional[str] = Field(None, description="Nombre personalizado del dashboard")


class ColumnInfo(BaseModel):
    """Información de una columna"""
    name: str
    type: str  # string, number, date, boolean
    nullable: bool
    unique_values: int


class ExcelValidationResponse(BaseModel):
    """Respuesta de validación de Excel"""
    valid: bool
    sheets: List[str]
    rows: int
    columns: int
    column_info: List[ColumnInfo]
    file_size: int
    errors: Optional[List[str]] = None


class ExcelProcessingResult(BaseModel):
    """Resultado del procesamiento de Excel"""
    success: bool
    dashboard_id: str
    rows_processed: int
    columns: int
    table_name: str
    widgets_created: int
    processing_time: float
    message: str


class DataPreview(BaseModel):
    """Preview de datos del Excel"""
    headers: List[str]
    rows: List[List[Any]]
    total_rows: int
    sample_size: int

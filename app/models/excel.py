from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal, Union
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


# ---------------------------------------------------------------------------
# Widget suggestion models — aligned with frontend widget.types.ts
# ---------------------------------------------------------------------------

class WidgetSuggestionBase(BaseModel):
    """Base for all auto-generated widget suggestions"""
    widget_type: str
    title: str
    table_name: str


class TableWidgetSuggestion(WidgetSuggestionBase):
    widget_type: Literal["table"] = "table"
    config: Dict[str, Any]  # {columns, sortable, filterable, pageSize}


class KPIWidgetSuggestion(WidgetSuggestionBase):
    widget_type: Literal["kpi"] = "kpi"
    config: Dict[str, Any]  # {column, aggregation, label, format, showVariation}


class BarChartWidgetSuggestion(WidgetSuggestionBase):
    widget_type: Literal["bar_chart"] = "bar_chart"
    config: Dict[str, Any]  # {xAxis, yAxis, aggregation, orientation, color, showGrid, showLegend}


class LineChartWidgetSuggestion(WidgetSuggestionBase):
    widget_type: Literal["line_chart"] = "line_chart"
    config: Dict[str, Any]  # {xAxis, yAxis, aggregation, color, showDots, showGrid, showArea, smooth}


class PieChartWidgetSuggestion(WidgetSuggestionBase):
    widget_type: Literal["pie_chart"] = "pie_chart"
    config: Dict[str, Any]  # {categoryColumn, valueColumn, aggregation, colors, showLegend, showLabels, donut}


WidgetSuggestion = Union[
    TableWidgetSuggestion,
    KPIWidgetSuggestion,
    BarChartWidgetSuggestion,
    LineChartWidgetSuggestion,
    PieChartWidgetSuggestion,
]


# ---------------------------------------------------------------------------
# Per-sheet processing result — matches ExcelSheetMetadata in auto-dashboard.ts
# ---------------------------------------------------------------------------

class SheetProcessingResult(BaseModel):
    """Result for a single Excel sheet — compatible with Next.js ExcelSheetMetadata"""
    sheet_name: str
    table_name: str
    rows: int
    columns: int
    column_types: Dict[str, str]          # {col_name: "string"|"number"|"integer"|"date"|"boolean"}
    sample_rows: List[Dict[str, Any]]     # first 5 rows for preview
    widget_suggestions: List[Dict[str, Any]]  # auto-generated widget configs
    suggests_user_import: bool = False
    user_columns: Optional[Dict[str, str]] = None  # {"email": "Correo", ...}


# ---------------------------------------------------------------------------
# Top-level /process response — replaces flat ExcelProcessingResult
# ---------------------------------------------------------------------------

class ExcelProcessResponse(BaseModel):
    """Multi-sheet response for POST /api/excel/process"""
    success: bool
    message: str
    sheets_processed: int
    sheets: List[SheetProcessingResult]   # one entry per Excel sheet
    tables: List[str]                     # all table_names created
    processing_time: float
    widgets_created: int


# ---------------------------------------------------------------------------
# Legacy flat result — kept for backward compat with /upload endpoint
# ---------------------------------------------------------------------------

class ExcelProcessingResult(BaseModel):
    """Resultado del procesamiento de Excel (legacy — single sheet)"""
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

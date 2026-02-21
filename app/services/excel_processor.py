import pandas as pd
import io
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ExcelProcessor:
    """Procesador de archivos Excel"""
    
    def __init__(self):
        self.supported_extensions = ['.xlsx', '.xls']
    
    def validate_file(self, file_content: bytes, filename: str) -> Tuple[bool, List[str]]:
        """Valida un archivo Excel"""
        errors = []
        
        # Validar extensión
        if not any(filename.lower().endswith(ext) for ext in self.supported_extensions):
            errors.append(f"Extensión no soportada. Use: {', '.join(self.supported_extensions)}")
        
        # Validar que no esté vacío
        if len(file_content) == 0:
            errors.append("El archivo está vacío")
        
        # Intentar leer el archivo
        try:
            pd.read_excel(io.BytesIO(file_content), nrows=0)
        except Exception as e:
            errors.append(f"Error al leer el archivo: {str(e)}")
        
        return len(errors) == 0, errors
    
    def analyze_file(self, file_content: bytes) -> Dict[str, Any]:
        """Analiza la estructura de un archivo Excel"""
        try:
            # Leer todas las hojas
            excel_file = pd.ExcelFile(io.BytesIO(file_content))
            sheets = excel_file.sheet_names
            
            # Leer la primera hoja para análisis
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=0)
            
            # Analizar columnas
            column_info = []
            for col in df.columns:
                col_data = df[col]
                
                # Detectar tipo de dato
                dtype = self._detect_column_type(col_data)
                
                column_info.append({
                    "name": str(col),
                    "type": dtype,
                    "nullable": col_data.isnull().any(),
                    "unique_values": col_data.nunique(),
                })
            
            return {
                "valid": True,
                "sheets": sheets,
                "rows": len(df),
                "columns": len(df.columns),
                "column_info": column_info,
                "file_size": len(file_content),
            }
            
        except Exception as e:
            logger.error(f"Error analyzing file: {str(e)}")
            return {
                "valid": False,
                "errors": [str(e)],
            }
    
    def process_excel(
        self,
        file_content: bytes,
        workspace_id: str,
        dashboard_name: str = None
    ) -> Dict[str, Any]:
        """Procesa un archivo Excel y retorna los datos estructurados"""
        try:
            start_time = datetime.now()
            
            # Leer Excel
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=0)
            
            # Limpiar nombres de columnas
            df.columns = [self._sanitize_column_name(col) for col in df.columns]
            
            # Convertir a formato JSON-friendly
            data = df.to_dict('records')
            
            # Limpiar valores NaN
            data = self._clean_nan_values(data)
            
            # Generar nombre de tabla
            table_name = self._generate_table_name(dashboard_name or "excel_data")
            
            # Calcular tiempo de procesamiento
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "data": data,
                "table_name": table_name,
                "rows_processed": len(data),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "column_types": self._get_column_types(df),
                "processing_time": processing_time,
            }
            
        except Exception as e:
            logger.error(f"Error processing Excel: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def get_data_preview(self, file_content: bytes, rows: int = 10) -> Dict[str, Any]:
        """Obtiene un preview de los datos del Excel"""
        try:
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=0, nrows=rows)
            
            return {
                "headers": list(df.columns),
                "rows": df.values.tolist(),
                "total_rows": len(df),
                "sample_size": min(rows, len(df)),
            }
        except Exception as e:
            logger.error(f"Error getting preview: {str(e)}")
            raise
    
    def _detect_column_type(self, series: pd.Series) -> str:
        """Detecta el tipo de dato de una columna"""
        # Ignorar valores nulos para la detección
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return "string"
        
        # Intentar detectar tipo
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        elif pd.api.types.is_numeric_dtype(series):
            if pd.api.types.is_integer_dtype(series):
                return "integer"
            return "number"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "date"
        else:
            return "string"
    
    def _sanitize_column_name(self, name: str) -> str:
        """Sanitiza nombres de columnas para uso en base de datos"""
        # Convertir a minúsculas
        name = str(name).lower()
        
        # Reemplazar espacios y caracteres especiales con guiones bajos
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', '_', name)
        
        # Asegurar que no empiece con número
        if name and name[0].isdigit():
            name = f"col_{name}"
        
        # Limitar longitud
        return name[:63]  # PostgreSQL limit
    
    def _generate_table_name(self, base_name: str) -> str:
        """Genera un nombre de tabla único"""
        sanitized = self._sanitize_column_name(base_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{sanitized}_{timestamp}"
    
    def _clean_nan_values(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Limpia valores NaN de los datos"""
        cleaned = []
        for row in data:
            cleaned_row = {}
            for key, value in row.items():
                if pd.isna(value):
                    cleaned_row[key] = None
                else:
                    cleaned_row[key] = value
            cleaned.append(cleaned_row)
        return cleaned
    
    def _get_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Obtiene los tipos de todas las columnas"""
        return {
            col: self._detect_column_type(df[col])
            for col in df.columns
        }

    # -----------------------------------------------------------------------
    # Multi-sheet processing (B5 — widget-payload alignment)
    # -----------------------------------------------------------------------

    def process_all_sheets(
        self,
        file_content: bytes,
        workspace_id: str,
    ) -> Dict[str, Any]:
        """Process every sheet in the workbook and return a widget-ready payload."""
        try:
            start_time = datetime.now()
            excel_file = pd.ExcelFile(io.BytesIO(file_content))
            sheet_names: List[str] = excel_file.sheet_names

            sheets_results: List[Dict[str, Any]] = []
            all_tables: List[str] = []
            total_widgets = 0

            for sheet_name in sheet_names:
                sheet_result = self._process_single_sheet(
                    file_content, sheet_name, workspace_id
                )
                sheets_results.append(sheet_result)
                all_tables.append(sheet_result["table_name"])
                total_widgets += len(sheet_result["widget_suggestions"])

            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "sheets_processed": len(sheets_results),
                "sheets": sheets_results,
                "tables": all_tables,
                "processing_time": processing_time,
                "widgets_created": total_widgets,
                "message": (
                    f"{len(sheets_results)} hoja(s) procesada(s) exitosamente. "
                    f"{total_widgets} widget(s) sugerido(s)."
                ),
            }

        except Exception as e:
            logger.error(f"Error in process_all_sheets: {str(e)}")
            return {"success": False, "error": str(e)}

    def _process_single_sheet(
        self,
        file_content: bytes,
        sheet_name: str,
        workspace_id: str,
    ) -> Dict[str, Any]:
        """Process one sheet and return its widget-ready metadata."""
        df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)
        df.columns = [self._sanitize_column_name(col) for col in df.columns]

        column_types = self._get_column_types(df)
        table_name = self._generate_table_name(sheet_name)
        sample_rows = self._clean_nan_values(df.head(5).to_dict("records"))

        widget_suggestions = self._suggest_widgets(column_types, table_name, sheet_name)

        user_import_info = self._detect_user_import(df.columns.tolist())

        return {
            "sheet_name": sheet_name,
            "table_name": table_name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_types": column_types,
            "sample_rows": sample_rows,
            "widget_suggestions": widget_suggestions,
            "suggests_user_import": user_import_info["suggests"],
            "user_columns": user_import_info["mapping"] if user_import_info["suggests"] else None,
            # raw data for storage
            "_data": self._clean_nan_values(df.to_dict("records")),
        }

    # -----------------------------------------------------------------------
    # Widget suggestion engine
    # -----------------------------------------------------------------------

    def _suggest_widgets(
        self,
        column_types: Dict[str, str],
        table_name: str,
        sheet_name: str,
    ) -> List[Dict[str, Any]]:
        """Auto-generate widget configs compatible with frontend widget.types.ts."""
        suggestions: List[Dict[str, Any]] = []
        all_cols = list(column_types.keys())
        numeric_cols = [c for c, t in column_types.items() if t in ("number", "integer")]
        date_cols = [c for c, t in column_types.items() if t == "date"]
        string_cols = [c for c, t in column_types.items() if t == "string"]

        # 1. Table widget — always suggested
        suggestions.append({
            "widget_type": "table",
            "title": sheet_name,
            "table_name": table_name,
            "config": {
                "columns": all_cols,
                "sortable": True,
                "filterable": True,
                "pageSize": 20,
            },
        })

        # 2. KPI widget — one per numeric column (max 3)
        for col in numeric_cols[:3]:
            suggestions.append({
                "widget_type": "kpi",
                "title": f"Total {col}",
                "table_name": table_name,
                "config": {
                    "column": col,
                    "aggregation": "SUM",
                    "label": col.replace("_", " ").title(),
                    "format": "number",
                    "showVariation": False,
                },
            })

        # 3. Bar chart — date/string x-axis + first numeric y-axis
        x_axis = (date_cols + string_cols)[:1]
        if x_axis and numeric_cols:
            suggestions.append({
                "widget_type": "bar_chart",
                "title": f"{sheet_name} — Barras",
                "table_name": table_name,
                "config": {
                    "xAxis": x_axis[0],
                    "yAxis": numeric_cols[0],
                    "aggregation": "SUM",
                    "orientation": "vertical",
                    "color": "#228BE6",
                    "showGrid": True,
                    "showLegend": True,
                },
            })

        # 4. Line chart — date x-axis + first numeric y-axis
        if date_cols and numeric_cols:
            suggestions.append({
                "widget_type": "line_chart",
                "title": f"{sheet_name} — Tendencia",
                "table_name": table_name,
                "config": {
                    "xAxis": date_cols[0],
                    "yAxis": numeric_cols[0],
                    "aggregation": "SUM",
                    "color": "#40C057",
                    "showDots": True,
                    "showGrid": True,
                    "showArea": False,
                    "smooth": False,
                },
            })

        # 5. Pie chart — first string category + first numeric value
        if string_cols and numeric_cols:
            suggestions.append({
                "widget_type": "pie_chart",
                "title": f"{sheet_name} — Distribución",
                "table_name": table_name,
                "config": {
                    "categoryColumn": string_cols[0],
                    "valueColumn": numeric_cols[0],
                    "aggregation": "SUM",
                    "colors": ["#228BE6", "#40C057", "#FA5252", "#FD7E14", "#BE4BDB"],
                    "showLegend": True,
                    "showLabels": True,
                    "donut": False,
                },
            })

        return suggestions

    # -----------------------------------------------------------------------
    # User-import detection
    # -----------------------------------------------------------------------

    _EMAIL_ALIASES = {"email", "correo", "e-mail", "mail"}
    _NAME_ALIASES = {"nombre", "name", "usuario", "user"}
    _ROLE_ALIASES = {"rol", "role", "cargo", "puesto"}

    def _detect_user_import(
        self, columns: List[str]
    ) -> Dict[str, Any]:
        """Detect if a sheet looks like a user list."""
        lower_cols = {c.lower(): c for c in columns}

        email_col = next((lower_cols[a] for a in self._EMAIL_ALIASES if a in lower_cols), None)
        name_col = next((lower_cols[a] for a in self._NAME_ALIASES if a in lower_cols), None)
        role_col = next((lower_cols[a] for a in self._ROLE_ALIASES if a in lower_cols), None)

        if not (email_col and name_col):
            return {"suggests": False, "mapping": None}

        mapping: Dict[str, str] = {"email": email_col, "name": name_col}
        if role_col:
            mapping["role"] = role_col

        return {"suggests": True, "mapping": mapping}

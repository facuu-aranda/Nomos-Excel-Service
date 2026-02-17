import pandas as pd
import io
import logging
from typing import Dict, Any, List, Tuple
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
        if pd.api.types.is_numeric_dtype(series):
            if pd.api.types.is_integer_dtype(series):
                return "integer"
            return "number"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "date"
        elif pd.api.types.is_bool_dtype(series):
            return "boolean"
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

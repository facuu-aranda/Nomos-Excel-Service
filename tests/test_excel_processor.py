import pytest
import pandas as pd
import io
from app.services.excel_processor import ExcelProcessor


@pytest.fixture
def excel_processor():
    return ExcelProcessor()


@pytest.fixture
def sample_excel_bytes():
    """Crea un archivo Excel de ejemplo en bytes"""
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'London', 'Paris'],
        'Salary': [50000, 60000, 70000]
    })
    
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer.getvalue()


class TestExcelProcessor:
    
    def test_validate_file_valid(self, excel_processor, sample_excel_bytes):
        """Test validación de archivo válido"""
        is_valid, errors = excel_processor.validate_file(sample_excel_bytes, "test.xlsx")
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_file_invalid_extension(self, excel_processor):
        """Test validación con extensión inválida"""
        is_valid, errors = excel_processor.validate_file(b"content", "test.txt")
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("Extensión no soportada" in error for error in errors)
    
    def test_validate_file_empty(self, excel_processor):
        """Test validación de archivo vacío"""
        is_valid, errors = excel_processor.validate_file(b"", "test.xlsx")
        
        assert is_valid is False
        assert any("vacío" in error for error in errors)
    
    def test_analyze_file(self, excel_processor, sample_excel_bytes):
        """Test análisis de archivo Excel"""
        analysis = excel_processor.analyze_file(sample_excel_bytes)
        
        assert analysis["valid"] is True
        assert analysis["rows"] == 3
        assert analysis["columns"] == 4
        assert len(analysis["column_info"]) == 4
        assert len(analysis["sheets"]) > 0
    
    def test_process_excel(self, excel_processor, sample_excel_bytes):
        """Test procesamiento completo de Excel"""
        result = excel_processor.process_excel(
            sample_excel_bytes,
            "workspace-123",
            "Test Dashboard"
        )
        
        assert result["success"] is True
        assert result["rows_processed"] == 3
        assert result["columns"] == 4
        assert "table_name" in result
        assert "processing_time" in result
    
    def test_get_data_preview(self, excel_processor, sample_excel_bytes):
        """Test obtención de preview de datos"""
        preview = excel_processor.get_data_preview(sample_excel_bytes, rows=2)
        
        assert len(preview["headers"]) == 4
        assert len(preview["rows"]) == 2
        assert preview["total_rows"] == 2
    
    def test_detect_column_type_integer(self, excel_processor):
        """Test detección de tipo integer"""
        series = pd.Series([1, 2, 3, 4, 5])
        col_type = excel_processor._detect_column_type(series)
        
        assert col_type == "integer"
    
    def test_detect_column_type_number(self, excel_processor):
        """Test detección de tipo number"""
        series = pd.Series([1.5, 2.7, 3.2])
        col_type = excel_processor._detect_column_type(series)
        
        assert col_type == "number"
    
    def test_detect_column_type_string(self, excel_processor):
        """Test detección de tipo string"""
        series = pd.Series(['a', 'b', 'c'])
        col_type = excel_processor._detect_column_type(series)
        
        assert col_type == "string"
    
    def test_sanitize_column_name(self, excel_processor):
        """Test sanitización de nombres de columnas"""
        # Espacios
        assert excel_processor._sanitize_column_name("First Name") == "first_name"
        
        # Caracteres especiales
        assert excel_processor._sanitize_column_name("Email@Address") == "emailaddress"
        
        # Números al inicio
        result = excel_processor._sanitize_column_name("123Column")
        assert result.startswith("col_")
    
    def test_generate_table_name(self, excel_processor):
        """Test generación de nombre de tabla"""
        table_name = excel_processor._generate_table_name("My Data")
        
        assert "my_data" in table_name
        assert len(table_name) > len("my_data")  # Incluye timestamp
    
    def test_clean_nan_values(self, excel_processor):
        """Test limpieza de valores NaN"""
        data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": pd.NA},
        ]
        
        cleaned = excel_processor._clean_nan_values(data)
        
        assert cleaned[0]["age"] == 25
        assert cleaned[1]["age"] is None

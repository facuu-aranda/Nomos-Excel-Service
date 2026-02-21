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

    def test_detect_column_type_boolean(self, excel_processor):
        """Test detección de tipo boolean"""
        series = pd.Series([True, False, True])
        col_type = excel_processor._detect_column_type(series)

        assert col_type == "boolean"
    
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


# ---------------------------------------------------------------------------
# B5 — Multi-sheet payload & widget suggestion tests
# ---------------------------------------------------------------------------

@pytest.fixture
def multi_sheet_excel_bytes():
    """Excel with two sheets: one sales-like, one user-like"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        sales_df = pd.DataFrame({
            "fecha": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
            "producto": ["A", "B", "C"],
            "monto": [1000.0, 2000.0, 3000.0],
            "cantidad": [10, 20, 30],
        })
        sales_df.to_excel(writer, sheet_name="Ventas", index=False)

        users_df = pd.DataFrame({
            "nombre": ["Alice", "Bob"],
            "email": ["alice@example.com", "bob@example.com"],
            "cargo": ["Admin", "User"],
        })
        users_df.to_excel(writer, sheet_name="Empleados", index=False)
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def numeric_only_excel_bytes():
    """Excel with only numeric columns (no date/string for chart axes)"""
    buf = io.BytesIO()
    df = pd.DataFrame({"val_a": [1, 2, 3], "val_b": [4, 5, 6]})
    df.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    return buf.getvalue()


class TestProcessAllSheets:

    def test_returns_success(self, excel_processor, multi_sheet_excel_bytes):
        result = excel_processor.process_all_sheets(multi_sheet_excel_bytes, "ws-1")
        assert result["success"] is True

    def test_processes_all_sheets(self, excel_processor, multi_sheet_excel_bytes):
        result = excel_processor.process_all_sheets(multi_sheet_excel_bytes, "ws-1")
        assert result["sheets_processed"] == 2
        assert len(result["sheets"]) == 2

    def test_tables_list_matches_sheets(self, excel_processor, multi_sheet_excel_bytes):
        result = excel_processor.process_all_sheets(multi_sheet_excel_bytes, "ws-1")
        assert len(result["tables"]) == 2
        for sheet in result["sheets"]:
            assert sheet["table_name"] in result["tables"]

    def test_sheet_has_required_keys(self, excel_processor, multi_sheet_excel_bytes):
        result = excel_processor.process_all_sheets(multi_sheet_excel_bytes, "ws-1")
        required = {
            "sheet_name", "table_name", "rows", "columns",
            "column_types", "sample_rows", "widget_suggestions",
            "suggests_user_import",
        }
        for sheet in result["sheets"]:
            assert required.issubset(sheet.keys())

    def test_sample_rows_max_five(self, excel_processor, multi_sheet_excel_bytes):
        result = excel_processor.process_all_sheets(multi_sheet_excel_bytes, "ws-1")
        for sheet in result["sheets"]:
            assert len(sheet["sample_rows"]) <= 5

    def test_internal_data_key_present(self, excel_processor, multi_sheet_excel_bytes):
        """_data must be present for the route to persist rows"""
        result = excel_processor.process_all_sheets(multi_sheet_excel_bytes, "ws-1")
        for sheet in result["sheets"]:
            assert "_data" in sheet
            assert len(sheet["_data"]) > 0

    def test_processing_time_positive(self, excel_processor, multi_sheet_excel_bytes):
        result = excel_processor.process_all_sheets(multi_sheet_excel_bytes, "ws-1")
        assert result["processing_time"] > 0

    def test_widgets_created_count(self, excel_processor, multi_sheet_excel_bytes):
        result = excel_processor.process_all_sheets(multi_sheet_excel_bytes, "ws-1")
        total = sum(len(s["widget_suggestions"]) for s in result["sheets"])
        assert result["widgets_created"] == total

    def test_error_on_invalid_bytes(self, excel_processor):
        result = excel_processor.process_all_sheets(b"not-an-excel", "ws-1")
        assert result["success"] is False
        assert "error" in result


class TestSuggestWidgets:

    def test_table_widget_always_present(self, excel_processor):
        col_types = {"nombre": "string", "monto": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Hoja1")
        types = [s["widget_type"] for s in suggestions]
        assert "table" in types

    def test_table_widget_config_shape(self, excel_processor):
        col_types = {"nombre": "string", "monto": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Hoja1")
        table_s = next(s for s in suggestions if s["widget_type"] == "table")
        cfg = table_s["config"]
        assert "columns" in cfg
        assert cfg["sortable"] is True
        assert cfg["filterable"] is True
        assert cfg["pageSize"] == 20

    def test_kpi_for_numeric_columns(self, excel_processor):
        col_types = {"monto": "number", "cantidad": "integer", "precio": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Ventas")
        kpi_suggestions = [s for s in suggestions if s["widget_type"] == "kpi"]
        assert len(kpi_suggestions) == 3  # max 3

    def test_kpi_max_three(self, excel_processor):
        col_types = {f"col{i}": "number" for i in range(10)}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Hoja1")
        kpi_suggestions = [s for s in suggestions if s["widget_type"] == "kpi"]
        assert len(kpi_suggestions) == 3

    def test_kpi_config_shape(self, excel_processor):
        col_types = {"monto": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Ventas")
        kpi = next(s for s in suggestions if s["widget_type"] == "kpi")
        cfg = kpi["config"]
        assert cfg["column"] == "monto"
        assert cfg["aggregation"] == "SUM"
        assert "label" in cfg
        assert "format" in cfg
        assert cfg["showVariation"] is False

    def test_bar_chart_with_string_x_axis(self, excel_processor):
        col_types = {"producto": "string", "monto": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Ventas")
        bar = next((s for s in suggestions if s["widget_type"] == "bar_chart"), None)
        assert bar is not None
        assert bar["config"]["xAxis"] == "producto"
        assert bar["config"]["yAxis"] == "monto"

    def test_bar_chart_with_date_x_axis(self, excel_processor):
        col_types = {"fecha": "date", "monto": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Ventas")
        bar = next((s for s in suggestions if s["widget_type"] == "bar_chart"), None)
        assert bar is not None
        assert bar["config"]["xAxis"] == "fecha"

    def test_line_chart_requires_date_column(self, excel_processor):
        col_types = {"producto": "string", "monto": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Ventas")
        line = next((s for s in suggestions if s["widget_type"] == "line_chart"), None)
        assert line is None  # no date column → no line chart

    def test_line_chart_with_date_column(self, excel_processor):
        col_types = {"fecha": "date", "monto": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Ventas")
        line = next((s for s in suggestions if s["widget_type"] == "line_chart"), None)
        assert line is not None
        cfg = line["config"]
        assert cfg["xAxis"] == "fecha"
        assert cfg["yAxis"] == "monto"
        assert "showDots" in cfg
        assert "showGrid" in cfg
        assert "showArea" in cfg
        assert "smooth" in cfg

    def test_pie_chart_requires_string_and_numeric(self, excel_processor):
        col_types = {"categoria": "string", "valor": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Dist")
        pie = next((s for s in suggestions if s["widget_type"] == "pie_chart"), None)
        assert pie is not None
        cfg = pie["config"]
        assert cfg["categoryColumn"] == "categoria"
        assert cfg["valueColumn"] == "valor"
        assert isinstance(cfg["colors"], list)
        assert len(cfg["colors"]) >= 3

    def test_no_chart_widgets_without_numeric(self, excel_processor):
        col_types = {"nombre": "string", "ciudad": "string"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Hoja1")
        chart_types = {"kpi", "bar_chart", "line_chart", "pie_chart"}
        found = [s["widget_type"] for s in suggestions if s["widget_type"] in chart_types]
        assert found == []

    def test_all_suggestions_have_required_keys(self, excel_processor):
        col_types = {"fecha": "date", "producto": "string", "monto": "number"}
        suggestions = excel_processor._suggest_widgets(col_types, "tbl", "Ventas")
        for s in suggestions:
            assert "widget_type" in s
            assert "title" in s
            assert "table_name" in s
            assert "config" in s
            assert s["table_name"] == "tbl"


class TestDetectUserImport:

    def test_detects_email_and_name(self, excel_processor):
        result = excel_processor._detect_user_import(["email", "nombre", "ciudad"])
        assert result["suggests"] is True
        assert result["mapping"]["email"] == "email"
        assert result["mapping"]["name"] == "nombre"

    def test_detects_aliases(self, excel_processor):
        result = excel_processor._detect_user_import(["correo", "name", "cargo"])
        assert result["suggests"] is True
        assert result["mapping"]["email"] == "correo"
        assert result["mapping"]["role"] == "cargo"

    def test_no_detection_without_email(self, excel_processor):
        result = excel_processor._detect_user_import(["nombre", "ciudad"])
        assert result["suggests"] is False

    def test_no_detection_without_name(self, excel_processor):
        result = excel_processor._detect_user_import(["email", "ciudad"])
        assert result["suggests"] is False

    def test_role_optional(self, excel_processor):
        result = excel_processor._detect_user_import(["email", "nombre"])
        assert result["suggests"] is True
        assert "role" not in result["mapping"]

    def test_case_insensitive_matching(self, excel_processor):
        result = excel_processor._detect_user_import(["EMAIL", "NOMBRE"])
        assert result["suggests"] is True

    def test_sanitized_column_names(self, excel_processor):
        """After sanitization columns are lowercase — detection must still work"""
        result = excel_processor._detect_user_import(["email", "nombre", "rol"])
        assert result["suggests"] is True
        assert result["mapping"]["role"] == "rol"

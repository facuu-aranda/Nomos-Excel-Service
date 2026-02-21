import pytest
from fastapi.testclient import TestClient
from app.main import app
import pandas as pd
import io
from app.factories import get_database_client


@pytest.fixture
def client():
    app.dependency_overrides = {}
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides = {}


@pytest.fixture
def sample_excel_file():
    """Crea un archivo Excel de ejemplo"""
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob'],
        'Age': [25, 30],
        'City': ['New York', 'London']
    })
    
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer


class TestRoutes:
    
    def test_root_endpoint(self, client):
        """Test endpoint raíz"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_health_check(self, client):
        """Test health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "healthy"
        assert "timestamp" in payload
        assert "uptime_seconds" in payload

    def test_process_excel_success(self, client, sample_excel_file):
        """Test procesamiento exitoso vía endpoint canónico /process — ExcelProcessResponse shape"""

        class MockDBClient:
            async def create_dashboard(self, workspace_id, name, description, icon="table", color="#228BE6"):
                return {"id": "dashboard-123", "name": name}

            async def store_excel_data(self, workspace_id, table_name, data, column_types):
                return len(data)

            async def create_widget(self, dashboard_id, widget_type, config):
                return {"id": "widget-123"}

            async def get_workspace(self, workspace_id):
                return {"id": workspace_id}

        app.dependency_overrides[get_database_client] = lambda: MockDBClient()

        response = client.post(
            "/api/excel/process",
            files={"file": ("test.xlsx", sample_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={
                "workspace_id": "workspace-123",
                "user_id": "user-456",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Multi-sheet response shape
        assert "sheets_processed" in data
        assert data["sheets_processed"] >= 1
        assert isinstance(data["sheets"], list)
        assert len(data["sheets"]) >= 1
        assert isinstance(data["tables"], list)
        assert data["widgets_created"] >= 1
        assert "processing_time" in data
        # Per-sheet keys
        sheet = data["sheets"][0]
        assert "sheet_name" in sheet
        assert "table_name" in sheet
        assert "rows" in sheet
        assert "columns" in sheet
        assert "column_types" in sheet
        assert "sample_rows" in sheet
        assert "widget_suggestions" in sheet
        assert isinstance(sheet["widget_suggestions"], list)
        # Table widget always present
        widget_types = [w["widget_type"] for w in sheet["widget_suggestions"]]
        assert "table" in widget_types

    def test_process_excel_multi_sheet(self, client):
        """Test that multi-sheet Excel produces one sheet entry per sheet"""
        import io as _io

        class MockDBClient:
            async def create_dashboard(self, workspace_id, name, description, icon="table", color="#228BE6"):
                return {"id": "dashboard-multi", "name": name}

            async def store_excel_data(self, workspace_id, table_name, data, column_types):
                return len(data)

            async def create_widget(self, dashboard_id, widget_type, config):
                return {"id": "widget-multi"}

            async def get_workspace(self, workspace_id):
                return {"id": workspace_id}

        app.dependency_overrides[get_database_client] = lambda: MockDBClient()

        buf = _io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            pd.DataFrame({"a": [1, 2], "b": [3, 4]}).to_excel(writer, sheet_name="Hoja1", index=False)
            pd.DataFrame({"x": ["p", "q"], "y": [10, 20]}).to_excel(writer, sheet_name="Hoja2", index=False)
        buf.seek(0)

        response = client.post(
            "/api/excel/process",
            files={"file": ("multi.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"workspace_id": "workspace-123", "user_id": "user-456"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["sheets_processed"] == 2
        assert len(data["sheets"]) == 2
        assert len(data["tables"]) == 2
        sheet_names = [s["sheet_name"] for s in data["sheets"]]
        assert "Hoja1" in sheet_names
        assert "Hoja2" in sheet_names

    def test_process_excel_invalid_extension(self, client):
        """Test error de validación cuando el archivo no es Excel"""

        class MockDBClient:
            async def create_dashboard(self, workspace_id, name, description, icon="table", color="#228BE6"):
                return {"id": "dashboard-123", "name": name}

            async def store_excel_data(self, workspace_id, table_name, data, column_types):
                return len(data)

            async def create_widget(self, dashboard_id, widget_type, config):
                return {"id": "widget-123"}

            async def get_workspace(self, workspace_id):
                return {"id": workspace_id}

        app.dependency_overrides[get_database_client] = lambda: MockDBClient()

        response = client.post(
            "/api/excel/process",
            files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")},
            data={
                "workspace_id": "workspace-123",
                "user_id": "user-456",
            },
        )

        assert response.status_code == 400
        assert "errors" in response.json()["detail"]
    
    def test_validate_excel_success(self, client, sample_excel_file):
        """Test validación exitosa de Excel"""
        response = client.post(
            "/api/excel/validate",
            files={"file": ("test.xlsx", sample_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["rows"] == 2
        assert data["columns"] == 3
    
    def test_validate_excel_invalid_extension(self, client):
        """Test validación con extensión inválida"""
        response = client.post(
            "/api/excel/validate",
            files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "errors" in data
    
    def test_preview_excel(self, client, sample_excel_file):
        """Test preview de Excel"""
        response = client.post(
            "/api/excel/preview",
            files={"file": ("test.xlsx", sample_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"rows": "2"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "headers" in data["data"]

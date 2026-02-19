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
        """Test procesamiento exitoso vía endpoint canónico /process"""

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
                "dashboard_name": "Sales Dashboard",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["dashboard_id"] == "dashboard-123"
        assert data["rows_processed"] == 2
        assert data["widgets_created"] == 1

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

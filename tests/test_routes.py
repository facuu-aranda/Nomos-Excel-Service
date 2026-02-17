import pytest
from fastapi.testclient import TestClient
from app.main import app
import pandas as pd
import io


@pytest.fixture
def client():
    return TestClient(app)


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
        assert response.json()["status"] == "healthy"
    
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

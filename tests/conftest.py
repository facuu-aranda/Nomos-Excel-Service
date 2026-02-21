"""
Pytest configuration — mock Supabase client before any app import
so tests run without a live Supabase connection or the cryptography DLL.
"""
import sys
from unittest.mock import MagicMock, AsyncMock

# ---------------------------------------------------------------------------
# Stub the entire supabase / gotrue stack before app modules are imported.
# This prevents the cryptography DLL load error on Windows dev machines.
# ---------------------------------------------------------------------------
_supabase_stub = MagicMock()
_supabase_stub.create_client.return_value = MagicMock()

for mod in (
    "supabase",
    "gotrue",
    "gotrue.errors",
    "gotrue._async",
    "gotrue._async.gotrue_client",
    "postgrest",
    "storage3",
    "realtime",
    "supafunc",
):
    sys.modules.setdefault(mod, MagicMock())

# ---------------------------------------------------------------------------
# Default MockDBClient reusable across route tests
# ---------------------------------------------------------------------------
import pytest


class MockDBClient:
    async def create_dashboard(
        self, workspace_id, name, description, icon="table", color="#228BE6"
    ):
        return {"id": "dashboard-test", "name": name}

    async def store_excel_data(self, workspace_id, table_name, data, column_types):
        return len(data)

    async def create_widget(self, dashboard_id, widget_type, config):
        return {"id": "widget-test"}

    async def get_workspace(self, workspace_id):
        return {"id": workspace_id}


@pytest.fixture
def mock_db_client():
    return MockDBClient()

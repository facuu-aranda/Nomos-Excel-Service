"""Interface for database operations"""
from typing import Protocol, Dict, Any, List, Optional


class IDatabaseClient(Protocol):
    """Protocol for database operations"""
    
    async def create_dashboard(
        self,
        workspace_id: str,
        name: str,
        description: str,
        icon: str = "table",
        color: str = "#228BE6"
    ) -> Dict[str, Any]:
        """Creates a new dashboard"""
        ...
    
    async def create_widget(
        self,
        dashboard_id: str,
        widget_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Creates a widget in a dashboard"""
        ...
    
    async def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Gets workspace information"""
        ...
    
    async def store_excel_data(
        self,
        workspace_id: str,
        table_name: str,
        data: List[Dict[str, Any]],
        column_types: Dict[str, str]
    ) -> int:
        """Stores Excel data in database"""
        ...

from supabase import create_client, Client
from app.config import settings
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Cliente de Supabase para operaciones en el workspace"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    async def create_dashboard(
        self,
        workspace_id: str,
        name: str,
        description: str,
        icon: str = "table",
        color: str = "#228BE6"
    ) -> Dict[str, Any]:
        """Crea un nuevo dashboard en el workspace"""
        try:
            # Obtener la posición más alta actual
            response = self.client.table("dashboards").select("position").eq(
                "workspace_id", workspace_id
            ).order("position", desc=True).limit(1).execute()
            
            next_position = 0
            if response.data and len(response.data) > 0:
                next_position = response.data[0]["position"] + 1
            
            # Crear dashboard
            dashboard_data = {
                "workspace_id": workspace_id,
                "name": name,
                "description": description,
                "icon": icon,
                "position": next_position,
                "grid_w": 4,
                "grid_h": 2,
                "is_system": False,
                "color": color,
            }
            
            result = self.client.table("dashboards").insert(dashboard_data).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Dashboard created: {result.data[0]['id']}")
                return result.data[0]
            else:
                raise Exception("Failed to create dashboard")
                
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            raise
    
    async def create_data_table(
        self,
        workspace_id: str,
        table_name: str,
        columns: List[Dict[str, str]]
    ) -> bool:
        """
        Crea una tabla dinámica en Supabase para almacenar datos del Excel
        Nota: En producción, esto requeriría permisos de admin o usar Supabase Management API
        """
        # Por ahora, esto es un placeholder
        # En producción real, usarías la Management API de Supabase
        logger.info(f"Table creation requested: {table_name} with {len(columns)} columns")
        return True
    
    async def insert_data(
        self,
        table_name: str,
        data: List[Dict[str, Any]]
    ) -> int:
        """Inserta datos en una tabla"""
        try:
            result = self.client.table(table_name).insert(data).execute()
            rows_inserted = len(result.data) if result.data else 0
            logger.info(f"Inserted {rows_inserted} rows into {table_name}")
            return rows_inserted
        except Exception as e:
            logger.error(f"Error inserting data: {str(e)}")
            raise
    
    async def create_widget(
        self,
        dashboard_id: str,
        widget_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crea un widget en un dashboard"""
        try:
            widget_data = {
                "dashboard_id": dashboard_id,
                "type": widget_type,
                "config": config,
                "position": 0,
                "width": 6,
                "height": 4,
            }
            
            result = self.client.table("widgets").insert(widget_data).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Widget created: {result.data[0]['id']}")
                return result.data[0]
            else:
                raise Exception("Failed to create widget")
                
        except Exception as e:
            logger.error(f"Error creating widget: {str(e)}")
            raise
    
    async def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de un workspace"""
        try:
            result = self.client.table("workspaces").select("*").eq(
                "id", workspace_id
            ).single().execute()
            
            return result.data if result.data else None
        except Exception as e:
            logger.error(f"Error getting workspace: {str(e)}")
            return None

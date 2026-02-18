"""Service for storing Excel data in Supabase"""
from typing import Dict, Any, List
import logging
from supabase import Client

logger = logging.getLogger(__name__)


class DataStorageService:
    """Handles storage of Excel data in Supabase"""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    async def store_excel_data(
        self,
        workspace_id: str,
        table_name: str,
        data: List[Dict[str, Any]],
        column_types: Dict[str, str]
    ) -> int:
        """
        Stores Excel data in Supabase using data_tables_metadata approach
        
        Instead of creating dynamic tables, we store data in a generic structure:
        - data_tables_metadata: stores table schema and metadata
        - data_table_rows: stores actual data as JSONB
        
        This approach:
        - Doesn't require admin permissions
        - Works with RLS
        - Allows flexible schema
        - Easier to query and manage
        """
        try:
            # 1. Create metadata entry for this table
            metadata = {
                "workspace_id": workspace_id,
                "table_name": table_name,
                "columns": [
                    {
                        "name": col_name,
                        "type": col_type,
                        "nullable": True
                    }
                    for col_name, col_type in column_types.items()
                ],
                "row_count": len(data),
                "created_at": "now()",
            }
            
            metadata_result = self.client.table("data_tables_metadata").insert(metadata).execute()
            
            if not metadata_result.data or len(metadata_result.data) == 0:
                raise Exception("Failed to create table metadata")
            
            table_id = metadata_result.data[0]["id"]
            logger.info(f"Created table metadata: {table_id} for {table_name}")
            
            # 2. Insert data rows
            # We store each row as JSONB in data_table_rows
            rows_to_insert = [
                {
                    "table_id": table_id,
                    "workspace_id": workspace_id,
                    "row_data": row,
                    "row_number": idx
                }
                for idx, row in enumerate(data, start=1)
            ]
            
            # Insert in batches of 100 to avoid payload limits
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(rows_to_insert), batch_size):
                batch = rows_to_insert[i:i + batch_size]
                result = self.client.table("data_table_rows").insert(batch).execute()
                
                if result.data:
                    total_inserted += len(result.data)
            
            logger.info(f"Inserted {total_inserted} rows for table {table_name}")
            
            # 3. Update row count in metadata
            self.client.table("data_tables_metadata").update({
                "row_count": total_inserted
            }).eq("id", table_id).execute()
            
            return total_inserted
            
        except Exception as e:
            logger.error(f"Error storing Excel data: {str(e)}")
            raise
    
    async def get_table_data(
        self,
        table_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieves data from a stored table"""
        try:
            result = self.client.table("data_table_rows").select("row_data, row_number").eq(
                "table_id", table_id
            ).order("row_number").range(offset, offset + limit - 1).execute()
            
            if result.data:
                return [row["row_data"] for row in result.data]
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving table data: {str(e)}")
            raise

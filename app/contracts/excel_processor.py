"""Interface for Excel processing"""
from typing import Protocol, Dict, Any, List, Tuple


class IExcelProcessor(Protocol):
    """Protocol for Excel processing operations"""
    
    def validate_file(self, file_content: bytes, filename: str) -> Tuple[bool, List[str]]:
        """Validates an Excel file"""
        ...
    
    def analyze_file(self, file_content: bytes) -> Dict[str, Any]:
        """Analyzes Excel file structure"""
        ...
    
    def process_excel(
        self,
        file_content: bytes,
        workspace_id: str,
        dashboard_name: str = None
    ) -> Dict[str, Any]:
        """Processes Excel file and returns structured data (single-sheet, legacy)"""
        ...
    
    def process_all_sheets(
        self,
        file_content: bytes,
        workspace_id: str,
    ) -> Dict[str, Any]:
        """Processes all sheets and returns widget-ready multi-sheet payload"""
        ...
    
    def get_data_preview(self, file_content: bytes, rows: int = 10) -> Dict[str, Any]:
        """Gets a preview of Excel data"""
        ...

"""Factory functions for creating service instances with DI"""
from app.services import ExcelProcessor, SupabaseClient
from app.contracts import IExcelProcessor, IDatabaseClient


def get_excel_processor() -> IExcelProcessor:
    """Factory function for ExcelProcessor (Dependency Injection)"""
    return ExcelProcessor()


def get_database_client() -> IDatabaseClient:
    """Factory function for SupabaseClient (Dependency Injection)"""
    return SupabaseClient()

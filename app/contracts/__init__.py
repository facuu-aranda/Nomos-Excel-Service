"""Contracts (interfaces) for dependency injection"""
from .excel_processor import IExcelProcessor
from .database_client import IDatabaseClient

__all__ = ['IExcelProcessor', 'IDatabaseClient']

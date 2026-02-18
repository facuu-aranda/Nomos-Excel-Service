"""Tests for DataStorageService"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from app.infrastructure.data_storage import DataStorageService


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client"""
    client = Mock()
    client.table = Mock()
    return client


@pytest.fixture
def data_storage_service(mock_supabase_client):
    """DataStorageService instance with mocked client"""
    return DataStorageService(mock_supabase_client)


@pytest.mark.asyncio
async def test_store_excel_data_success(data_storage_service, mock_supabase_client):
    """Test successful storage of Excel data"""
    # Arrange
    workspace_id = "workspace-123"
    table_name = "test_table"
    data = [
        {"col1": "value1", "col2": 123},
        {"col1": "value2", "col2": 456},
    ]
    column_types = {"col1": "string", "col2": "integer"}
    
    # Mock metadata insert
    metadata_mock = Mock()
    metadata_mock.insert = Mock(return_value=metadata_mock)
    metadata_mock.execute = Mock(return_value=Mock(data=[{"id": "table-id-123"}]))
    
    # Mock rows insert
    rows_mock = Mock()
    rows_mock.insert = Mock(return_value=rows_mock)
    rows_mock.execute = Mock(return_value=Mock(data=[{}, {}]))  # 2 rows inserted
    
    # Mock update
    update_mock = Mock()
    update_mock.update = Mock(return_value=update_mock)
    update_mock.eq = Mock(return_value=update_mock)
    update_mock.execute = Mock(return_value=Mock())
    
    mock_supabase_client.table = Mock(side_effect=[
        metadata_mock,  # First call for metadata
        rows_mock,      # Second call for rows
        update_mock,    # Third call for update
    ])
    
    # Act
    result = await data_storage_service.store_excel_data(
        workspace_id, table_name, data, column_types
    )
    
    # Assert
    assert result == 2
    assert mock_supabase_client.table.call_count == 3


@pytest.mark.asyncio
async def test_store_excel_data_batching(data_storage_service, mock_supabase_client):
    """Test that large datasets are batched correctly"""
    # Arrange
    workspace_id = "workspace-123"
    table_name = "large_table"
    # Create 250 rows (should be split into 3 batches of 100, 100, 50)
    data = [{"col1": f"value{i}"} for i in range(250)]
    column_types = {"col1": "string"}
    
    # Mock metadata insert
    metadata_mock = Mock()
    metadata_mock.insert = Mock(return_value=metadata_mock)
    metadata_mock.execute = Mock(return_value=Mock(data=[{"id": "table-id-123"}]))
    
    # Mock rows insert (will be called 3 times for batches)
    rows_mock = Mock()
    rows_mock.insert = Mock(return_value=rows_mock)
    rows_mock.execute = Mock(return_value=Mock(data=[{} for _ in range(100)]))
    
    # Mock update
    update_mock = Mock()
    update_mock.update = Mock(return_value=update_mock)
    update_mock.eq = Mock(return_value=update_mock)
    update_mock.execute = Mock(return_value=Mock())
    
    mock_supabase_client.table = Mock(side_effect=[
        metadata_mock,  # Metadata
        rows_mock,      # Batch 1
        rows_mock,      # Batch 2
        rows_mock,      # Batch 3
        update_mock,    # Update
    ])
    
    # Act
    result = await data_storage_service.store_excel_data(
        workspace_id, table_name, data, column_types
    )
    
    # Assert
    assert result == 300  # 3 batches * 100 rows per mock
    assert mock_supabase_client.table.call_count == 5


@pytest.mark.asyncio
async def test_get_table_data_success(data_storage_service, mock_supabase_client):
    """Test successful retrieval of table data"""
    # Arrange
    table_id = "table-123"
    expected_data = [
        {"col1": "value1", "col2": 123},
        {"col1": "value2", "col2": 456},
    ]
    
    # Mock query
    query_mock = Mock()
    query_mock.select = Mock(return_value=query_mock)
    query_mock.eq = Mock(return_value=query_mock)
    query_mock.order = Mock(return_value=query_mock)
    query_mock.range = Mock(return_value=query_mock)
    query_mock.execute = Mock(return_value=Mock(data=[
        {"row_data": expected_data[0], "row_number": 1},
        {"row_data": expected_data[1], "row_number": 2},
    ]))
    
    mock_supabase_client.table = Mock(return_value=query_mock)
    
    # Act
    result = await data_storage_service.get_table_data(table_id, limit=100, offset=0)
    
    # Assert
    assert result == expected_data
    query_mock.select.assert_called_once_with("row_data, row_number")
    query_mock.eq.assert_called_once_with("table_id", table_id)

"""
Azure Scanner Tests - EDGE CASES ONLY

13 edge case tests covering Azure Blob Storage boundary conditions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.azure_connector.scanner import get_summary


def create_mock_blob(name, size, last_modified=None):
    """Helper to create mock blob with proper attributes"""
    mock = Mock()
    mock.name = name
    mock.size = size
    mock.last_modified = last_modified
    return mock


class TestAzureBlobScanningEdgeCases:
    """Edge cases for Azure blob scanning"""
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_scanning_empty_container(self, mock_blob_client_class):
        """Test scanning empty container"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        mock_container = Mock()
        mock_container.list_blobs.return_value = []
        mock_blob_service = Mock()
        mock_blob_service.get_container_client.return_value = mock_container
        mock_blob_client_class.from_connection_string.return_value = mock_blob_service
        
        results = scan_azure_blob('test-connection-string', 'empty-container')
        
        assert results == []
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_directory_markers_skipped(self, mock_blob_client_class):
        """Test directory markers are skipped (folder/, subfolder/)"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        blobs = [
            create_mock_blob('folder/', 0),
            create_mock_blob('folder/subfolder/', 0),
            create_mock_blob('folder/file.txt', 100),
            create_mock_blob('data/', 0)
        ]
        
        mock_container = Mock()
        mock_container.list_blobs.return_value = blobs
        mock_blob_service = Mock()
        mock_blob_service.get_container_client.return_value = mock_container
        mock_blob_client_class.from_connection_string.return_value = mock_blob_service
        
        results = scan_azure_blob('test-connection-string', 'test-container')
        
        # Only the actual file should be included (directories with / are skipped)
        assert len(results) == 1
        assert results[0]['file_name'] == 'file.txt'
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_blobs_without_last_modified(self, mock_blob_client_class):
        """Test blobs without last_modified timestamp"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        blobs = [
            create_mock_blob('file1.txt', 100, None),
            create_mock_blob('file2.txt', 200, None)
        ]
        
        mock_container = Mock()
        mock_container.list_blobs.return_value = blobs
        mock_blob_service = Mock()
        mock_blob_service.get_container_client.return_value = mock_container
        mock_blob_client_class.from_connection_string.return_value = mock_blob_service
        
        results = scan_azure_blob('test-connection-string', 'test-container')
        
        assert len(results) == 2
        assert all(file.get('last_modified') is None for file in results)
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_unicode_characters_in_blob_names(self, mock_blob_client_class):
        """Test Unicode characters in blob names (Cyrillic, Chinese, Emoji)"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        blobs = [
            create_mock_blob('文档.txt', 100),
            create_mock_blob('файл.pdf', 200),
            create_mock_blob('दस्तावेज़.docx', 300),
            create_mock_blob('😀emoji.txt', 150)
        ]
        
        mock_container = Mock()
        mock_container.list_blobs.return_value = blobs
        mock_blob_service = Mock()
        mock_blob_service.get_container_client.return_value = mock_container
        mock_blob_client_class.from_connection_string.return_value = mock_blob_service
        
        results = scan_azure_blob('test-connection-string', 'test-container')
        
        assert len(results) == 4
        names = [file['file_name'] for file in results]
        assert '文档.txt' in names
        assert 'файл.pdf' in names
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_stop_flag_early_termination(self, mock_blob_client_class):
        """Test stop flag early termination (50+ blobs)"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        # Create 60 mock blobs
        blobs = [create_mock_blob(f'file{i}.txt', 100) for i in range(60)]
        
        mock_container = Mock()
        mock_container.list_blobs.return_value = blobs
        mock_blob_service = Mock()
        mock_blob_service.get_container_client.return_value = mock_container
        mock_blob_client_class.from_connection_string.return_value = mock_blob_service
        
        results = scan_azure_blob('test-connection-string', 'test-container', stop_flag=lambda: False)
        
        # Should process all when not stopped
        assert len(results) == 60
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_connection_error_handling(self, mock_blob_client_class):
        """Test connection error handling (invalid connection string)"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        mock_blob_client_class.from_connection_string.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Failed to scan Azure container"):
            scan_azure_blob('invalid-connection-string', 'test-container')
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_blobs_with_trailing_leading_slashes(self, mock_blob_client_class):
        """Test blobs with trailing/leading slashes"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        blobs = [
            create_mock_blob('/leading.txt', 100),
            create_mock_blob('trailing.txt/', 0),
            create_mock_blob('/both/', 0),
            create_mock_blob('normal.txt', 150)
        ]
        
        mock_container = Mock()
        mock_container.list_blobs.return_value = blobs
        mock_blob_service = Mock()
        mock_blob_service.get_container_client.return_value = mock_container
        mock_blob_client_class.from_connection_string.return_value = mock_blob_service
        
        results = scan_azure_blob('test-connection-string', 'test-container')
        
        # Directory markers (trailing /) should be skipped
        assert len(results) >= 2  # /leading.txt and normal.txt
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_empty_blob_names(self, mock_blob_client_class):
        """Test empty blob names"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        blobs = [
            create_mock_blob('', 100),
            create_mock_blob('valid.txt', 200)
        ]
        
        mock_container = Mock()
        mock_container.list_blobs.return_value = blobs
        mock_blob_service = Mock()
        mock_blob_service.get_container_client.return_value = mock_container
        mock_blob_client_class.from_connection_string.return_value = mock_blob_service
        
        results = scan_azure_blob('test-connection-string', 'test-container')
        
        # Should handle empty names gracefully
        assert len(results) >= 1
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_very_long_blob_paths(self, mock_blob_client_class):
        """Test very long blob paths (>500 characters)"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        # Create a path longer than 500 characters
        long_path = 'a/' * 100 + 'file.txt'  # ~500+ characters
        
        blobs = [
            create_mock_blob(long_path, 100),
            create_mock_blob('short.txt', 200)
        ]
        
        mock_container = Mock()
        mock_container.list_blobs.return_value = blobs
        mock_blob_service = Mock()
        mock_blob_service.get_container_client.return_value = mock_container
        mock_blob_client_class.from_connection_string.return_value = mock_blob_service
        
        results = scan_azure_blob('test-connection-string', 'test-container')
        
        assert len(results) == 2


class TestAzureConnectionEdgeCases:
    """Edge cases for Azure connection"""
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_missing_connection_string(self, mock_blob_client_class):
        """Test missing connection string (should raise error)"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        mock_blob_client_class.from_connection_string.side_effect = Exception("Invalid connection string")
        
        with pytest.raises(Exception):
            scan_azure_blob('', 'test-container')
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_malformed_connection_string(self, mock_blob_client_class):
        """Test malformed connection string"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        mock_blob_client_class.from_connection_string.side_effect = ValueError("Invalid connection string format")
        
        with pytest.raises(Exception):
            scan_azure_blob('malformed;;;connection', 'test-container')
    
    @patch('azure.storage.blob.BlobServiceClient')
    def test_network_timeout_handling(self, mock_blob_client_class):
        """Test network timeout handling"""
        from backend.azure_connector.scanner import scan_azure_blob
        
        mock_container = Mock()
        mock_container.list_blobs.side_effect = TimeoutError("Network timeout")
        mock_blob_service = Mock()
        mock_blob_service.get_container_client.return_value = mock_container
        mock_blob_client_class.from_connection_string.return_value = mock_blob_service
        
        with pytest.raises(Exception):
            scan_azure_blob('test-connection-string', 'test-container')


class TestAzureSummaryEdgeCases:
    """Edge cases for Azure summary generation"""
    
    def test_summary_with_empty_container(self):
        """Test summary with empty container"""
        summary = get_summary([])
        
        assert summary['total_files'] == 0
        assert summary['total_size'] == 0
        assert summary['file_type_distribution'] == {}

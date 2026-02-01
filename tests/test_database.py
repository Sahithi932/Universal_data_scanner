"""
Database Tests - EDGE CASES ONLY

8 edge case tests covering database boundary conditions and error scenarios
"""

import pytest
import sqlite3
import os
import tempfile
from backend.local_connector import database as local_db


@pytest.fixture
def temp_db_dir(tmp_path):
    """Create temporary database directory"""
    db_dir = tmp_path / "test_db"
    db_dir.mkdir()
    
    # Set up temporary database paths
    original_scans_db = local_db.SCANS_DB
    original_files_db = local_db.FILES_DB
    
    local_db.SCANS_DB = str(db_dir / "scanner.db")
    local_db.FILES_DB = str(db_dir / "files.db")
    
    yield db_dir
    
    # Restore original paths
    local_db.SCANS_DB = original_scans_db
    local_db.FILES_DB = original_files_db


class TestDatabaseEdgeCases:
    """Edge cases for database operations"""
    
    def test_duplicate_scan_id_prevention(self, temp_db_dir):
        """Test duplicate scan_id prevention (IntegrityError)"""
        local_db.init_db()
        
        scan_id = "duplicate-scan"
        local_db.create_scan(scan_id, "Test 1", "/path1")
        
        # Attempting duplicate should raise IntegrityError
        with pytest.raises(sqlite3.IntegrityError):
            local_db.create_scan(scan_id, "Test 2", "/path2")
    
    def test_save_files_without_scan(self, temp_db_dir):
        """Test save files without scan (foreign key)"""
        local_db.init_db()
        
        files = [{
            'file_name': 'test.txt',
            'file_path': '/test/test.txt',
            'file_type': 'Document',
            'mime_type': 'text/plain',
            'file_size': 100,
            'last_modified': '2024-01-01T00:00:00',
            'storage_type': 'local',
            'eligible_for_ocr': False
        }]
        
        # This should not raise error (no foreign key constraint enforced)
        local_db.save_files("nonexistent-scan", files)
        
        # But files should still be saved
        count = local_db.get_total_files_count("nonexistent-scan")
        assert count == 1
    
    def test_complete_nonexistent_scan(self, temp_db_dir):
        """Test complete nonexistent scan (no error, no rows updated)"""
        local_db.init_db()
        
        # Should not raise error, just no rows updated
        local_db.complete_scan("nonexistent-scan", 10, 1000)
        
        scans = local_db.get_all_scans()
        assert len(scans) == 0
    
    def test_get_files_from_empty_scan(self, temp_db_dir):
        """Test get files from empty scan"""
        local_db.init_db()
        
        scan_id = "empty-scan"
        local_db.create_scan(scan_id, "Empty Scan", "/empty")
        
        files = local_db.get_scan_files(scan_id)
        assert files == []
    
    def test_special_characters_in_names(self, temp_db_dir):
        """Test special characters in names (quotes, apostrophes, Unicode)"""
        local_db.init_db()
        
        scan_id = "special-chars"
        local_db.create_scan(scan_id, "Test's \"Scan\" with 'quotes'", "/path")
        
        files = [{
            'file_name': "file's & \"name\" with 'quotes'.txt",
            'file_path': '/path/file\'s & "name" with \'quotes\'.txt',
            'file_type': 'Document',
            'mime_type': 'text/plain',
            'file_size': 100,
            'last_modified': '2024-01-01T00:00:00',
            'storage_type': 'local',
            'eligible_for_ocr': False
        }]
        
        local_db.save_files(scan_id, files)
        
        retrieved_files = local_db.get_scan_files(scan_id)
        assert len(retrieved_files) == 1
        assert retrieved_files[0]['file_name'] == "file's & \"name\" with 'quotes'.txt"
    
    def test_unicode_characters(self, temp_db_dir):
        """Test Unicode characters (中文, Русский)"""
        local_db.init_db()
        
        scan_id = "unicode-test"
        local_db.create_scan(scan_id, "测试扫描 Тест", "/测试/путь")
        
        files = [{
            'file_name': '文档файл.txt',
            'file_path': '/测试/путь/文档файл.txt',
            'file_type': 'Document',
            'mime_type': 'text/plain',
            'file_size': 100,
            'last_modified': '2024-01-01T00:00:00',
            'storage_type': 'local',
            'eligible_for_ocr': False
        }]
        
        local_db.save_files(scan_id, files)
        
        retrieved_files = local_db.get_scan_files(scan_id)
        assert len(retrieved_files) == 1
        assert retrieved_files[0]['file_name'] == '文档файл.txt'
    
    def test_null_values_handling(self, temp_db_dir):
        """Test NULL values handling"""
        local_db.init_db()
        
        scan_id = "null-test"
        local_db.create_scan(scan_id, "Null Test", "/null")
        
        conn = sqlite3.connect(local_db.SCANS_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        scan = dict(cursor.fetchone())
        conn.close()
        
        # Initially these should be NULL
        assert scan['end_time'] is None
        assert scan['total_files'] is None
        assert scan['total_size'] is None
    
    def test_pagination_with_offset_beyond_count(self, temp_db_dir):
        """Test pagination with offset beyond total count"""
        local_db.init_db()
        
        scan_id = "pagination-test"
        local_db.create_scan(scan_id, "Pagination Test", "/page")
        
        # Create only 10 files
        files = [
            {
                'file_name': f'file{i}.txt',
                'file_path': f'/page/file{i}.txt',
                'file_type': 'Document',
                'mime_type': 'text/plain',
                'file_size': 100,
                'last_modified': '2024-01-01T00:00:00',
                'storage_type': 'local',
                'eligible_for_ocr': False
            }
            for i in range(10)
        ]
        
        local_db.save_files(scan_id, files)
        
        # Request with offset beyond count
        result = local_db.get_scan_files(scan_id, limit=10, offset=100)
        
        # Should return empty list, not error
        assert result == []

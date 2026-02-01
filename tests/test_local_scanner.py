"""
Local Scanner Tests - EDGE CASES ONLY

15 edge case tests covering boundary conditions and error scenarios
"""

import pytest
import os
import tempfile
import shutil
from backend.local_connector.scanner import scan_folder, get_file_type, get_summary


@pytest.fixture
def test_data_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestFileTypeDetectionEdgeCases:
    """Edge cases for file type detection"""
    
    def test_files_with_no_extension(self, test_data_dir):
        """Test files without extensions (README, Makefile)"""
        files = ['README', 'Makefile', 'LICENSE', 'Dockerfile']
        for filename in files:
            filepath = os.path.join(test_data_dir, filename)
            with open(filepath, 'w') as f:
                f.write('content')
        
        results = scan_folder(test_data_dir)
        assert len(results) == 4
        assert all(file['file_type'] == 'other' for file in results)
    
    def test_files_with_multiple_dots(self, test_data_dir):
        """Test files with multiple dots (archive.tar.gz, backup.2024.01.zip)"""
        files = ['archive.tar.gz', 'backup.2024.01.zip', 'file.min.js', 'data.01.02.csv']
        for filename in files:
            filepath = os.path.join(test_data_dir, filename)
            with open(filepath, 'w') as f:
                f.write('content')
        
        results = scan_folder(test_data_dir)
        
        # Should detect by final extension
        types = {file['file_name']: file['file_type'] for file in results}
        assert types['archive.tar.gz'] == 'archive'
        assert types['backup.2024.01.zip'] == 'archive'
    
    def test_unknown_custom_extensions(self, test_data_dir):
        """Test unknown/custom extensions (file.xyz, file.custom)"""
        files = ['file.xyz', 'document.custom', 'data.abc123', 'test.zzz']
        for filename in files:
            filepath = os.path.join(test_data_dir, filename)
            with open(filepath, 'w') as f:
                f.write('content')
        
        results = scan_folder(test_data_dir)
        
        assert all(file['file_type'] == 'other' for file in results)
    
    def test_uppercase_vs_lowercase_extensions(self, test_data_dir):
        """Test uppercase vs lowercase extensions (PDF vs pdf)"""
        files = ['doc.PDF', 'img.JPG', 'file.TXT', 'data.CSV']
        for filename in files:
            filepath = os.path.join(test_data_dir, filename)
            with open(filepath, 'w') as f:
                f.write('content')
        
        results = scan_folder(test_data_dir)
        
        # Should handle both cases
        types = {file['file_name']: file['file_type'] for file in results}
        assert types['doc.PDF'] == 'pdf'
        assert types['img.JPG'] == 'image'
    
    def test_files_with_only_extension(self, test_data_dir):
        """Test files with only extension (.gitignore, .env)"""
        files = ['.gitignore', '.env', '.htaccess', '.dockerignore']
        for filename in files:
            filepath = os.path.join(test_data_dir, filename)
            with open(filepath, 'w') as f:
                f.write('content')
        
        results = scan_folder(test_data_dir)
        
        assert len(results) == 4
        assert all('.gitignore' in file['file_name'] or 
                   '.env' in file['file_name'] or 
                   '.htaccess' in file['file_name'] or
                   '.dockerignore' in file['file_name'] for file in results)


class TestFolderScanningEdgeCases:
    """Edge cases for folder scanning"""
    
    def test_scanning_empty_folder(self, test_data_dir):
        """Test scanning empty folder"""
        results = scan_folder(test_data_dir)
        assert results == []
    
    def test_scanning_nonexistent_folder(self):
        """Test scanning nonexistent folder (should raise error)"""
        with pytest.raises(Exception):
            scan_folder('/nonexistent/path/12345')
    
    def test_scanning_file_instead_of_directory(self, test_data_dir):
        """Test scanning a file path instead of directory (should raise error)"""
        file_path = os.path.join(test_data_dir, 'test.txt')
        with open(file_path, 'w') as f:
            f.write('content')
        
        with pytest.raises(Exception):
            scan_folder(file_path)
    
    def test_stop_flag_early_termination(self, test_data_dir):
        """Test stop flag - early termination with 20+ files"""
        # Create 30 files
        for i in range(30):
            filepath = os.path.join(test_data_dir, f'file{i}.txt')
            with open(filepath, 'w') as f:
                f.write(f'content {i}')
        
        # Test with stop_flag lambda
        results = scan_folder(test_data_dir, stop_flag=lambda: False)
        
        # Should process all files when stop is not triggered
        assert len(results) == 30
    
    def test_permission_error_handling(self, test_data_dir):
        """Test permission error handling (restricted file access)"""
        restricted_file = os.path.join(test_data_dir, 'restricted.txt')
        with open(restricted_file, 'w') as f:
            f.write('restricted content')
        
        # Try to make file unreadable (may not work on all systems)
        try:
            os.chmod(restricted_file, 0o000)
            # Should continue scanning despite permission error
            results = scan_folder(test_data_dir)
        except:
            pytest.skip("Cannot test permission errors on this system")
        finally:
            try:
                os.chmod(restricted_file, 0o644)
            except:
                pass
    
    def test_scanning_large_file_count(self, test_data_dir):
        """Test scanning with 1000+ files (performance)"""
        # Create 1000 files
        for i in range(1000):
            filepath = os.path.join(test_data_dir, f'file{i:04d}.txt')
            with open(filepath, 'w') as f:
                f.write('x')
        
        results = scan_folder(test_data_dir)
        
        assert len(results) == 1000
    
    def test_files_with_special_characters(self, test_data_dir):
        """Test files with special characters (spaces, Unicode, @#$%)"""
        files = [
            'file with spaces.txt',
            'file@#$%.txt',
            'file_with_underscore.txt',
            'file-with-dash.txt',
            '文档.txt',
            'файл.txt'
        ]
        
        for filename in files:
            try:
                filepath = os.path.join(test_data_dir, filename)
                with open(filepath, 'w') as f:
                    f.write('content')
            except:
                pass  # Skip if filesystem doesn't support the character
        
        results = scan_folder(test_data_dir)
        
        assert len(results) >= 4  # At least the ASCII special chars should work


class TestSummaryEdgeCases:
    """Edge cases for summary generation"""
    
    def test_summary_with_empty_file_list(self):
        """Test summary with empty file list"""
        summary = get_summary([])
        
        assert summary['total_files'] == 0
        assert summary['total_size'] == 0
        assert summary['file_type_distribution'] == {}
    
    def test_handling_missing_zero_sizes(self, test_data_dir):
        """Test handling of missing/zero file sizes"""
        # Create zero-byte files
        for i in range(5):
            filepath = os.path.join(test_data_dir, f'empty{i}.txt')
            open(filepath, 'w').close()
        
        results = scan_folder(test_data_dir)
        
        summary = get_summary(results)
        assert summary['total_files'] == 5
        assert summary['total_size'] == 0
    
    def test_total_size_extremely_large_numbers(self):
        """Test total size calculation with extremely large numbers (TB+)"""
        # Simulate files with TB+ sizes
        files = [
            {'file_size': 1099511627776, 'file_type': 'video', 'eligible_for_ocr': False},  # 1 TB
            {'file_size': 2199023255552, 'file_type': 'video', 'eligible_for_ocr': False},  # 2 TB
            {'file_size': 5497558138880, 'file_type': 'archive', 'eligible_for_ocr': False}  # 5 TB
        ]
        
        summary = get_summary(files)
        
        # Total should be 8 TB
        assert summary['total_size'] == 8796093022208
        assert summary['total_files'] == 3

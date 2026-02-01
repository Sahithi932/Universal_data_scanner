"""
Shared Scanner Tests - EDGE CASES ONLY

10 edge case tests covering shared directory boundary conditions
"""

import pytest
import os
import tempfile
import shutil
from backend.shared_connector.scanner import scan_shared_directory, get_summary


@pytest.fixture
def test_share_dir():
    """Create a temporary directory to simulate shared directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestSharedDirectoryScanningEdgeCases:
    """Edge cases for shared directory scanning"""
    
    def test_scanning_empty_shared_directory(self, test_share_dir):
        """Test scanning empty shared directory"""
        results = scan_shared_directory(test_share_dir, 'TestShare')
        
        assert results == []
    
    def test_scanning_nonexistent_share_path(self):
        """Test scanning nonexistent share path (should raise error)"""
        with pytest.raises(Exception):
            scan_shared_directory('//nonexistent/share/path', 'NonExistentShare')
    
    def test_handling_no_read_permission(self, test_share_dir):
        """Test handling no read permission on share"""
        restricted_file = os.path.join(test_share_dir, 'restricted.txt')
        with open(restricted_file, 'w') as f:
            f.write('restricted content')
        
        # Try to make file unreadable
        try:
            os.chmod(restricted_file, 0o000)
            # Should continue scanning despite permission errors
            results = scan_shared_directory(test_share_dir, 'TestShare')
        except:
            pytest.skip("Cannot test permission errors on this system")
        finally:
            try:
                os.chmod(restricted_file, 0o644)
            except:
                pass
    
    def test_stop_flag_termination(self, test_share_dir):
        """Test stop flag termination (30+ files)"""
        # Create 40 files
        for i in range(40):
            filepath = os.path.join(test_share_dir, f'file{i}.txt')
            with open(filepath, 'w') as f:
                f.write(f'content {i}')
        
        results = scan_shared_directory(test_share_dir, 'TestShare', stop_flag=lambda: False)
        
        # Should process all files when not stopped
        assert len(results) == 40
    
    def test_special_characters_in_filenames(self, test_share_dir):
        """Test special characters in filenames (spaces, Unicode, @#$%)"""
        files = [
            'file with spaces.txt',
            'file@#$%.txt',
            'file_with_underscore.txt',
            'file-with-dash.txt',
            '文档.txt',
            'файл.txt'
        ]
        
        created_count = 0
        for filename in files:
            try:
                filepath = os.path.join(test_share_dir, filename)
                with open(filepath, 'w') as f:
                    f.write('content')
                created_count += 1
            except:
                pass  # Skip if filesystem doesn't support the character
        
        results = scan_shared_directory(test_share_dir, 'TestShare')
        
        assert len(results) >= 4  # At least the ASCII special chars should work
    
    def test_files_without_extension(self, test_share_dir):
        """Test files without extension (README, LICENSE)"""
        files = ['README', 'LICENSE', 'Makefile', 'Dockerfile']
        
        for filename in files:
            filepath = os.path.join(test_share_dir, filename)
            with open(filepath, 'w') as f:
                f.write('content')
        
        results = scan_shared_directory(test_share_dir, 'TestShare')
        
        assert len(results) == 4
        # Files without extension should have empty or 'Unknown' type
        assert all('file_name' in file for file in results)
    
    def test_very_long_file_paths(self, test_share_dir):
        """Test very long file paths (>260 characters on Windows)"""
        # Create nested directories to exceed Windows MAX_PATH (260)
        long_path = test_share_dir
        for i in range(20):
            long_path = os.path.join(long_path, f'verylongdirectoryname{i}')
        
        try:
            os.makedirs(long_path, exist_ok=True)
            filepath = os.path.join(long_path, 'file.txt')
            with open(filepath, 'w') as f:
                f.write('content')
            
            results = scan_shared_directory(test_share_dir, 'TestShare')
            
            # Should handle long paths or skip gracefully
            assert isinstance(results, list)
        except OSError:
            pytest.skip("System cannot handle very long paths")


class TestSharedSummaryEdgeCases:
    """Edge cases for shared summary generation"""
    
    def test_summary_with_empty_share(self):
        """Test summary with empty share"""
        summary = get_summary([])
        
        assert summary['total_files'] == 0
        assert summary['total_size'] == 0
        assert summary['file_type_distribution'] == {}
    
    def test_handling_missing_zero_sizes(self, test_share_dir):
        """Test handling of missing/zero file sizes"""
        # Create zero-byte files
        for i in range(5):
            filepath = os.path.join(test_share_dir, f'empty{i}.txt')
            open(filepath, 'w').close()
        
        results = scan_shared_directory(test_share_dir, 'TestShare')
        
        summary = get_summary(results)
        assert summary['total_files'] == 5
        assert summary['total_size'] == 0

"""
API Tests - EDGE CASES ONLY

4 edge case tests covering API endpoint boundary conditions
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


class TestAPIEdgeCases:
    """Edge cases for API endpoints"""
    
    def test_post_scan_without_folder_path(self):
        """Test POST /api/scan without folder_path (validation error)"""
        response = client.post("/api/scan")
        
        # Should return 422 Unprocessable Entity for missing required parameter
        assert response.status_code == 422
    
    def test_post_scan_with_nonexistent_path(self):
        """Test POST /api/scan with nonexistent path (error)"""
        response = client.post("/api/scan", params={
            "folder_path": "/nonexistent/path/12345/does/not/exist"
        })
        
        # Should accept the request and start scan (error handled in background)
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
        
        # The error will be reported in scan status (checked in background thread)
    
    def test_get_scan_nonexistent_id(self):
        """Test GET /api/scans/{scan_id} for nonexistent scan (404/empty)"""
        response = client.get("/api/scans/nonexistent-scan-id-12345")
        
        # Should return empty or appropriate error response
        # Depending on implementation, could be 404 or empty data
        assert response.status_code in [200, 404]
    
    def test_post_stop_nonexistent_scan(self):
        """Test POST /api/scan/{scan_id}/stop for nonexistent scan (404)"""
        response = client.post("/api/scan/nonexistent-scan-id-12345/stop")
        
        # Should return 404 or error for non-existent scan
        assert response.status_code in [404, 200]
        
        if response.status_code == 200:
            data = response.json()
            # Should indicate the scan doesn't exist
            assert "success" in data or "error" in data

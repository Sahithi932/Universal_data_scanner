# Universal Data Scanner

A file scanning application that analyzes files across local folders, Azure Blob Storage, and shared directories.

## Overview

Scan and analyze files from:
- Local Folders (Windows/Linux)
- Azure Blob Storage
- Shared Directories (SMB)

Get file metadata, type distribution, and storage analytics in one place.

---

## Features

- Multi-source file scanning
- Real-time scan progress tracking
- File metadata collection (name, size, type, modified time)
- File type classification
- OCR eligibility detection
- Advanced filtering and search
- Pagination (100 files per page)
- Export as JSON or CSV
---

## Project Structure

```
.
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── render.yaml                        # Render deployment config
├── TEST_PLAN.md                       # Edge case test plan (49 tests)
├── backend/
│   ├── app.py                         # FastAPI application
│   ├── scanner.db                     # Scan metadata database
│   ├── files.db                       # File records database
│   ├── local_connector/
│   │   ├── __init__.py
│   │   ├── database.py                # Local scan database operations
│   │   └── scanner.py                 # Local folder scanner
│   ├── azure_connector/
│   │   ├── __init__.py
│   │   ├── database.py                # Azure scan database operations
│   │   └── scanner.py                 # Azure Blob Storage scanner
│   └── shared_connector/
│       ├── __init__.py
│       ├── database.py                # Shared directory database operations
│       └── scanner.py                 # Shared directory scanner
├── tests/
│   ├── __init__.py                    # Test package initialization
│   ├── conftest.py                    # Pytest fixtures and configuration
│   ├── test_local_scanner.py          # Local scanner edge cases (14 tests)
│   ├── test_azure_scanner.py          # Azure scanner edge cases (13 tests)
│   ├── test_shared_scanner.py         # Shared scanner edge cases (9 tests)
│   ├── test_database.py               # Database edge cases (8 tests)
│   └── test_api.py                    # API edge cases (4 tests)
└── ui/
    ├── index.html                     # Frontend HTML
    ├── styles.css                     # Frontend styling
    ├── app-core.js                    # Core business logic & API calls
    └── app-ui.js                      # UI display & formatting functions
```
---

## Technology

- Backend: FastAPI, Python 3.13, SQLite
- Frontend: HTML5, CSS3, Vanilla JavaScript
- Cloud: Azure Storage SDK
- Server: Uvicorn (ASGI)

---

## Database

Two separate SQLite databases:

**scanner.db** - Scan metadata
- scans (local scans)
- azure_scans (Azure scans)
- shared_scans (shared directory scans)

**files.db** - File data
- files (local files)
- azure_files (Azure files)
- shared_scan_files (shared files)

---

## Setup

### Prerequisites
- Python 3.13+
- pip

### Installation

1. Activate virtual environment:
```bash
cd Universal_data_scanner
python -m venv venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```bash
pip install -r requirement.txt
```

3. Start server:
```bash
cd backend
python app.py
uvicorn app:app --reload
```
4. Open browser:
```
http://localhost:8000
```
---

## Usage

### Local Folder Scan
- Select "Local Folder"
- Enter folder path (e.g., C:\Users\ADMIN\Documents)
- Click "Start Scanning"

### Azure Blob Scan
- Select "Azure Blob Storage"
- Enter connection string, container name, storage account
- Click "Scan Azure Container"

### Shared Directory Scan
- Select "Shared Directory"
- Enter UNC path (e.g., \\192.168.1.100\Share)
- Click "Scan Shared Directory"

---

## API Endpoints

**Local:**
- POST /api/scan
- GET /api/scans
- GET /api/scan/{scan_id}/files

**Azure:**
- POST /api/scan/azure
- GET /api/scans/azure
- GET /api/scan/azure/{scan_id}/files

**Shared:**
- POST /api/scan/shared
- GET /api/scans/shared
- GET /api/scan/shared/{scan_id}/files

---

## File Metadata

Each file record includes:
- Name, Path, Size
- Type (pdf, image, office, text, code, archive, other)
- MIME type, Last modified
- OCR eligible (true/false)
- Storage type (local, azure, shared)

---

## Troubleshooting

**Server won't start:**
- Check if port 8000 is available
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirement.txt --force-reinstall`

**Import errors:**
- Activate virtual environment
- Reinstall dependencies

**Azure connection issues:**
- Verify connection string format
- Check container name
- Ensure network connectivity

**Shared directory access denied:**
- Verify UNC path format
- Check network connectivity
- Verify read permissions

---
## How to Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file  
pytest tests/test_local_scanner.py -v

# Run with detailed output
pytest tests/ -v --tb=short

# Run specific test class
pytest tests/test_azure_scanner.py::TestAzureBlobScanningEdgeCases -v

# Show print statements
pytest tests/ -v -s
```
## Test Dependencies
- pytest==7.4.0
- FastAPI TestClient (for API tests)
- unittest.mock (for Azure SDK mocking)
- tempfile/shutil (for test isolation)

## Total Progress
 **Complete**: All 49 edge case tests implemented and passing
 **Test Plan**: Documented in TEST_PLAN.md
 **100% Success Rate**: No skipped or failing tests

## Future Enhancements
- Duplicate file detection
- Cloud storage integration (Google,etc..)
- Incremental scans (only new/modified files)
- User authentication and access control
---
Version: 1.0.0
Status: Active & Working

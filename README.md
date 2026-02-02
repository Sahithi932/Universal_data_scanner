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

## Setup & Installation

### Option 1: Docker (Recommended) 🐳

**Prerequisites:**
- Docker Desktop installed and running
- Virtualization enabled in BIOS (required for Docker)

**Quick Start:**

1. **Build Docker image:**
```bash
docker build -t uds-app .
```
2. **Run the application:**
```bash
docker run -p 8000:8000 uds-app
```
3. **Open in browser:**
```
http://localhost:8000
```
---
### Option 2: Local Python Setup

**Prerequisites:**
- Python 3.13+
- pip package manager

**Installation Steps:**

1. **Create and activate virtual environment:**
```bash
python -m venv venv
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start server:**
```bash
uvicorn backend.app:app --reload
```

4. **Open in browser:**
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

**Docker not working?**
- Enable virtualization in BIOS and restart
- Open Docker Desktop and wait for "Engine running"

**Server won't start?**
- Check port 8000 is free
- Activate virtual environment: `.venv\Scripts\Activate.ps1`
- Reinstall: `pip install -r requirements.txt`

**Import errors?**
- Activate virtual environment first
- Run: `pip install -r requirements.txt`

**Azure connection failed?**
- Check connection string and container name

**Can't access shared folder?**
- Verify network path and permissions

---

## Testing

### Test Suite Overview
- **Total Tests:** 49 edge case tests
- **Coverage:** API, Database, Local/Azure/Shared scanners
- **Status:** ✅ All tests passing
- **Documentation:** See (TEST_PLAN.md)

### Running Tests in Docker (Recommended)

**Run all tests inside Docker container:**
```bash
docker run uds-app bash run_tests.sh
```

**Interactive testing:**
```bash
docker run -it uds-app bash
pytest tests/ -v
exit
```

### Running Tests Locally

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_local_scanner.py -v
pytest tests/test_azure_scanner.py -v
pytest tests/test_database.py -v
pytest tests/test_api.py -v
pytest tests/test_shared_scanner.py -v
```

**Run with coverage report:**
```bash
pytest tests/ -v --cov=backend --cov-report=html
```

**Run specific test class:**
```bash
pytest tests/test_azure_scanner.py::TestAzureBlobScanningEdgeCases -v
```

## Docker Commands Reference

```bash
# Build image
docker build -t uds-app .

# Run application
docker run -p 8000:8000 uds-app

# Run tests
docker run uds-app bash run_tests.sh

# Interactive mode
docker run -it uds-app bash

# View running containers
docker ps

# Stop container
docker stop <container_id>

# View images
docker images

# Remove image
docker rmi uds-app
```
---
## Project Status

**Version:** 1.0.0  
**Status:** ✅ Active & Working  
**Tests:** ✅ 49/49 Passing  
**Docker:** ✅ Containerized  
**Deployment:** Ready for production

---
## Future Enhancements
- Duplicate file detection
- Cloud storage integration (Google,etc..)
- Incremental scans (only new/modified files)
- User authentication and access control
---
Version: 1.0.0
Status: Active & Working

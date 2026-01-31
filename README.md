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
├── requirement.txt                    # Python dependencies
├── backend/
│   ├── app.py                         # FastAPI application
│   ├── scanner.db                     # Scan metadata database
│   ├── files.db                       # File records database
│   ├── local_connector/
│   │   ├── database.py                # Local scan database operations
│   │   └── scanner.py                 # Local folder scanner
│   ├── azure_connector/
│   │   ├── database.py                # Azure scan database operations
│   │   └── scanner.py                 # Azure Blob Storage scanner
│   └── shared_connector/
│       ├── database.py                # Shared directory database operations
│       └── scanner.py                 # Shared directory scanner
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
.venv\Scripts\Activate
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

## Test Cases

### Local Folder Scan

#### Best Case (Medium Folder - Fast Scan)
**Input:**
- Path: `C:\Users\ADMIN\Documents`
- Files: 500-1000 files
- Total Size: ~2-5 GB
- Mixed file types (PDFs, DOCX, images)

**Expected Result:**
- Scan Duration: 5-10 seconds
- All files detected correctly
- File types classified accurately
- Dates displayed properly

**Status:** ✅ Passed

---

#### Average Case (Large Folder)
**Input:**
- Path: `C:\Users\ADMIN`
- Files: 1000-3000 files
- Total Size: Dependent on folder content (typically 10-30 GB)
- Mixed file types (office, images, code, archives, videos)
- Multiple nested folders

**Result:**
- Scan Duration: 15-60 seconds
- All files processed correctly
- Stop scan button functional during scan
- Background scanning without UI freeze

**Status:** ✅ Passed

---

#### Worst Case (Very Large Folder - Long Scan)
**Input:**
- Path: Large directory with deep nested folders
- Files: 3000+ files
- Deep folder hierarchy with multiple levels
- Various file types and sizes

** Result:**
- Scan Duration: 3-4 minutes (86 GB test)
- Background scanning without blocking UI
- Stop scan button stops backend processing immediately

**Status:** ✅ Passed (after fixes)

---

### Azure Blob Storage Scan

#### Test Case
**Input:**
- Connection String: `DefaultEndpointsProtocol=https;AccountName=****
- Container Name: Your container name
- Storage Account: Your account name
- Files: 250 files tested(example folder,hierarchy with multiple folders)
**Status:** ✅ Passed

---

### Shared Directory Scan

#### Test Case
**Input:**
- Share Path: `\\192.168.x.x\SharedFolder` (from friend's shared folder)
- Share Name: `shared-1`
- Files: 800 files
**Status:** Passed

---

## Future Enhancements
- Duplicate file detection
- Cloud storage integration (Google,etc..)
- Incremental scans (only new/modified files)
- User authentication and access control
---

---
Version: 1.0.0
Status: Active & Working

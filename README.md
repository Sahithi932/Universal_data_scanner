# Universal Data Scanner

A file scanning application that analyzes files across local folders, Azure Blob Storage, and shared directories.

## Overview

Scan and analyze files from:
- Local Folders (Windows/Linux)
- Azure Blob Storage
- Shared Directories (SMB/CIFS)

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
backend/
  ├── app.py                    # FastAPI application
  ├── scanner.db              # Scan metadata
  ├── files.db                # File data
  ├── local_connector/        # Local folder scanner
  ├── azure_connector/        # Azure Blob scanner
  └── shared_connector/       # Shared directory scanner

ui/
  ├── index.html             # HTML structure
  ├── styles.css             # Styling
  └── app.js                 # Frontend logic

requirement.txt              # Dependencies
README.md                    # This file
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
cd to the current folder
python -m venv myenv
.venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirement.txt
```

3. Start server:
```bash
cd backend
python app.py
python uvicorn app:app --reload
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

## Security Notes

- No authentication implemented (add for production)
- Database files are unencrypted (add encryption for production)
- Connection strings sent via HTTP (use HTTPS for production)
- No rate limiting (add for production)

---

## Future Enhancements

- Authentication & user management
- HTTPS/SSL support
- Database encryption
- Scheduled scans
- Email notifications
- More cloud providers (AWS S3, Google Cloud)

---

Version: 1.0.0
Status: Active & Working

# Universal Data Scanner - Requirements

## Core Dependencies
```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
```

## Cloud Storage SDKs
```
azure-storage-blob==12.18.0
google-cloud-storage==2.10.0
```

## Python Version
- Python 3.8 or higher

## Installation

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install fastapi uvicorn python-multipart azure-storage-blob google-cloud-storage
```

## Optional Dependencies (for development)
```
black==23.0.0      # Code formatting
pylint==3.0.0      # Code linting
pytest==7.4.0      # Testing
```

## Supported Features

### Local Folder Scanning
- ✅ Recursive folder traversal
- ✅ File metadata extraction
- ✅ No additional authentication needed

### Azure Blob Storage
- ✅ Container scanning
- ✅ Requires: Connection string
- ✅ Scans: All blobs in container

### Google Cloud Storage
- ✅ Bucket scanning
- ✅ Requires: Project ID + GCP credentials
- ✅ Supports: Service account JSON or default credentials

## System Requirements

- **OS**: Windows, macOS, Linux
- **RAM**: 512 MB minimum (2 GB recommended)
- **Disk**: 100 MB for application + database
- **Network**: Required only for cloud storage scanning

## Database

- **Type**: SQLite3 (built-in Python)
- **Location**: `c:\uds\backend\scanner.db`
- **Size**: Grows with scan history (~1 KB per 100 files scanned)

## Port

- **API Server**: http://localhost:8000
- **Configurable**: Change in app.py last line

## Running the Application

```bash
cd c:\uds\backend
python app.py

# Server will start at http://localhost:8000
# Frontend available at http://localhost:8000/
```

## Troubleshooting Installation

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### "No module named 'google.cloud'"
```bash
pip install google-cloud-storage
```

### "No module named 'azure.storage'"
```bash
pip install azure-storage-blob
```

### Port 8000 already in use
Edit `app.py` last line:
```python
uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)  # Use 8001 instead
```

Then access at http://localhost:8001

"""
Universal Data Scanner API
FastAPI backend for scanning local folders, Azure Blob Storage, and Shared directories
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime

# Import Local connector
from local_connector import (
    init_db, create_scan, save_files, complete_scan, fail_scan,
    get_all_scans, get_scan_files, get_total_files_count,
    scan_folder, get_summary
)
# Import Azure connector
from azure_connector import (
    scan_azure_blob, get_summary as azure_get_summary,
    create_scan as azure_create_scan, save_files as azure_save_files,
    complete_scan as azure_complete_scan, fail_scan as azure_fail_scan,
    get_all_scans as azure_get_all_scans, get_scan_files as azure_get_scan_files,
    init_db as azure_init_db, get_total_files_count as azure_get_total_files_count
)
# Import Shared Directory connector
from shared_connector import (
    scan_shared_directory, get_summary as shared_get_summary,
    create_scan as shared_create_scan, save_files as shared_save_files,
    complete_scan as shared_complete_scan, fail_scan as shared_fail_scan,
    get_all_scans as shared_get_all_scans, get_scan_files as shared_get_scan_files,
    init_db as shared_init_db, get_total_files_count as shared_get_total_files_count
)
# Create FastAPI app
app = FastAPI(
    title="Universal Data Scanner",
    description="Scan local folders and Azure Blob Storage",
    version="1.0.0"
)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_db()
    azure_init_db()
    shared_init_db()

# ========== API ENDPOINTS ==========

@app.post("/api/scan")
async def start_scan(
    folder_path: str = Query(..., description="Folder path to scan"),
    scan_name: str = Query(None, description="Optional scan name")
):
    """Start scanning a folder"""
    scan_id = str(uuid.uuid4())
    name = scan_name or f"Scan {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}"
    start_time = datetime.now()
    
    try:
        # Create scan record
        create_scan(scan_id, name, folder_path)
        
        # Scan the folder
        files = scan_folder(folder_path)
        
        # Save files
        save_files(scan_id, files)
        
        # Get summary
        summary = get_summary(files)
        
        # Complete scan
        complete_scan(scan_id, summary['total_files'], summary['total_size'])
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "scan_id": scan_id,
            "scan_name": name,
            "folder_path": folder_path,
            "total_files": summary['total_files'],
            "total_size": summary['total_size'],
            "duration_seconds": duration,
            "file_type_distribution": summary['file_type_distribution'],
            "ocr_eligible_count": summary['ocr_eligible_count'],
            "sample_files": files[:5]
        }
        
    except FileNotFoundError as e:
        fail_scan(scan_id)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        fail_scan(scan_id)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/scans")
async def get_scans():
    """Get all scans"""
    scans = get_all_scans()
    return {
        "success": True,
        "count": len(scans),
        "scans": scans
    }


@app.get("/api/scan/{scan_id}")
async def get_scan_details(scan_id: str, limit: int = 100, offset: int = 0):
    """Get scan details and files with pagination"""
    files = get_scan_files(scan_id, limit, offset)
    total_count = get_total_files_count(scan_id)
    
    if total_count == 0:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "success": True,
        "scan_id": scan_id,
        "total_files": total_count,
        "limit": limit,
        "offset": offset,
        "returned_count": len(files),
        "files": files
    }

# ========== AZURE ENDPOINTS ==========
@app.post("/api/scan/azure")
async def scan_azure(
    connection_string: str = Query(..., description="Azure storage connection string"),
    container_name: str = Query(..., description="Container name to scan"),
    storage_account: str = Query(..., description="Storage account name"),
    scan_name: str = Query(None, description="Optional scan name")
):
    """Scan Azure Blob Storage container"""
    scan_id = str(uuid.uuid4())
    name = scan_name or f"Azure Scan {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}"
    start_time = datetime.now()
    
    try:
        # Create scan record
        azure_create_scan(scan_id, name, container_name, storage_account)
        
        # Scan Azure container
        files = scan_azure_blob(connection_string, container_name)
        
        # Save files
        azure_save_files(scan_id, files)
        
        # Get summary
        summary = azure_get_summary(files)
        
        # Complete scan
        azure_complete_scan(scan_id, summary['total_files'], summary['total_size'])
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "scan_id": scan_id,
            "scan_name": name,
            "storage_type": "azure_blob",
            "container_name": container_name,
            "total_files": summary['total_files'],
            "total_size": summary['total_size'],
            "duration_seconds": duration,
            "file_type_distribution": summary['file_type_distribution'],
            "ocr_eligible_count": summary['ocr_eligible_count'],
            "sample_files": files[:5]
        }
        
    except Exception as e:
        azure_fail_scan(scan_id)
        raise HTTPException(status_code=500, detail=f"Azure scan error: {str(e)}")

@app.get("/api/scans/azure")
async def get_azure_scans():
    """Get all Azure scans"""
    scans = azure_get_all_scans()
    return {
        "success": True,
        "count": len(scans),
        "scans": scans
    }

@app.get("/api/scan/azure/{scan_id}")
async def get_azure_scan_details(scan_id: str, limit: int = 100, offset: int = 0):
    """Get Azure scan details and files with pagination"""
    files = azure_get_scan_files(scan_id, limit, offset)
    total_count = azure_get_total_files_count(scan_id)
    
    if total_count == 0:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "success": True,
        "scan_id": scan_id,
        "total_files": total_count,
        "limit": limit,
        "offset": offset,
        "returned_count": len(files),
        "files": files
    }

# ========== SHARED DIRECTORY ENDPOINTS ==========

@app.post("/api/scan/shared")
async def scan_shared(
    share_path: str = Query(..., description="UNC path to shared folder (e.g., \\\\192.168.1.100\\Share)"),
    share_name: str = Query(..., description="Shared folder name/identifier"),
    scan_name: str = Query(None, description="Optional scan name")
):
    """Scan a shared directory (SMB/CIFS share)"""
    scan_id = str(uuid.uuid4())
    name = scan_name or f"Shared Scan {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}"
    start_time = datetime.now()
    
    try:
        # Create scan record
        shared_create_scan(scan_id, name, share_path, share_name)
        
        # Scan shared directory
        files = scan_shared_directory(share_path, share_name)
        
        # Save files
        shared_save_files(scan_id, files)
        
        # Get summary
        summary = shared_get_summary(files)
        
        # Complete scan
        shared_complete_scan(scan_id, summary['total_files'], summary['total_size'])
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "scan_id": scan_id,
            "scan_name": name,
            "storage_type": "shared_directory",
            "share_path": share_path,
            "share_name": share_name,
            "total_files": summary['total_files'],
            "total_size": summary['total_size'],
            "duration_seconds": duration,
            "file_type_distribution": summary['file_type_distribution'],
            "ocr_eligible_count": summary['ocr_eligible_count'],
            "sample_files": files[:5]
        }
        
    except FileNotFoundError as e:
        shared_fail_scan(scan_id)
        raise HTTPException(status_code=404, detail=f"Shared path not found: {str(e)}")
    except PermissionError as e:
        shared_fail_scan(scan_id)
        raise HTTPException(status_code=403, detail=f"Permission denied: {str(e)}")
    except Exception as e:
        shared_fail_scan(scan_id)
        raise HTTPException(status_code=500, detail=f"Shared scan error: {str(e)}")


@app.get("/api/scans/shared")
async def get_shared_scans():
    """Get all shared directory scans"""
    scans = shared_get_all_scans()
    return {
        "success": True,
        "count": len(scans),
        "scans": scans
    }


@app.get("/api/scan/shared/{scan_id}")
async def get_shared_scan_details(scan_id: str, limit: int = 100, offset: int = 0):
    """Get shared directory scan details and files with pagination"""
    files = shared_get_scan_files(scan_id, limit, offset)
    total_count = shared_get_total_files_count(scan_id)
    
    if total_count == 0:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "success": True,
        "scan_id": scan_id,
        "total_files": total_count,
        "limit": limit,
        "offset": offset,
        "returned_count": len(files),
        "files": files
    }

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {"status": "ok", "message": "Scanner is running"}

# Mount frontend
app.mount("/", StaticFiles(directory="../ui", html=True), name="ui")
# Run
if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting Local Data Scanner...")
    print("📍 http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

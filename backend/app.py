"""
Universal Data Scanner API
FastAPI backend for scanning local folders, Azure Blob Storage, and Shared directories
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime
import os
import threading
from dotenv import load_dotenv
load_dotenv()

# Global dictionary to track active scans and their stop flags
active_scans = {}
active_scans_lock = threading.Lock()

# Import Local connector
from .local_connector import (
    init_db, create_scan, save_files, complete_scan, fail_scan,
    get_all_scans, get_scan_files, get_total_files_count,
    scan_folder, get_summary
)
# Import Azure connector
from .azure_connector import (
    scan_azure_blob, get_summary as azure_get_summary,
    create_scan as azure_create_scan, save_files as azure_save_files,
    complete_scan as azure_complete_scan, fail_scan as azure_fail_scan,
    get_all_scans as azure_get_all_scans, get_scan_files as azure_get_scan_files,
    init_db as azure_init_db, get_total_files_count as azure_get_total_files_count
)
# Import Shared Directory connector
from .shared_connector import (
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
    
    # Initialize scan tracking
    with active_scans_lock:
        active_scans[scan_id] = {
            "stop": False, 
            "type": "local",
            "status": "scanning",
            "result": None,
            "error": None
        }
    
    def scan_thread():
        try:
            # Create scan record
            create_scan(scan_id, name, folder_path)
            
            # Scan the folder with stop flag
            files = scan_folder(folder_path, stop_flag=lambda: active_scans.get(scan_id, {}).get("stop", False))
            
            # Check if stopped
            if active_scans.get(scan_id, {}).get("stop", False):
                fail_scan(scan_id)
                with active_scans_lock:
                    if scan_id in active_scans:
                        active_scans[scan_id]["status"] = "stopped"
                return
            
            # Save files
            save_files(scan_id, files)
            
            # Get summary
            summary = get_summary(files)
            
            # Complete scan
            complete_scan(scan_id, summary['total_files'], summary['total_size'])
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Store result
            result = {
                "success": True,
                "scan_id": scan_id,
                "scan_name": name,
                "folder_path": folder_path,
                "total_files": summary['total_files'],
                "total_size": summary['total_size'],
                "duration_seconds": duration,
                "file_type_distribution": summary['file_type_distribution'],
                "ocr_eligible_count": summary['ocr_eligible_count']
            }
            
            with active_scans_lock:
                if scan_id in active_scans:
                    active_scans[scan_id]["status"] = "completed"
                    active_scans[scan_id]["result"] = result
            
        except Exception as e:
            fail_scan(scan_id)
            with active_scans_lock:
                if scan_id in active_scans:
                    active_scans[scan_id]["status"] = "failed"
                    active_scans[scan_id]["error"] = str(e)
    
    # Start scan in background thread
    thread = threading.Thread(target=scan_thread, daemon=True)
    thread.start()
    
    return {
        "success": True,
        "scan_id": scan_id,
        "scan_name": name,
        "folder_path": folder_path,
        "message": "Scan started in background"
    }

@app.post("/api/scan/browser")
async def save_browser_scan(data: dict):
    """Save browser-scanned data"""
    try:
        scan_id = data.get('scan_id')
        scan_name = data.get('scan_name')
        folder_path = data.get('folder_path')
        files = data.get('files', [])
        total_files = data.get('total_files', 0)
        total_size = data.get('total_size', 0)
        
        # Create scan record
        create_scan(scan_id, scan_name, folder_path)
        
        # Save files
        save_files(scan_id, files)
        
        # Complete scan
        complete_scan(scan_id, total_files, total_size)
        
        return {
            "success": True,
            "scan_id": scan_id,
            "message": "Browser scan saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scans")
async def get_scans():
    """Get all scans from all storage types (local, azure, shared)"""
    local_scans = get_all_scans()
    azure_scans = azure_get_all_scans()
    shared_scans = shared_get_all_scans()
    
    # Add storage_type to each scan and normalize field names
    for scan in local_scans:
        scan['storage_type'] = 'local'
    
    for scan in azure_scans:
        scan['storage_type'] = 'azure'
    
    for scan in shared_scans:
        scan['storage_type'] = 'shared'
        # Normalize field names for shared scans (created_at -> start_time, scan_name -> name)
        if 'created_at' in scan:
            scan['start_time'] = scan['created_at']
        if 'scan_name' in scan:
            scan['name'] = scan['scan_name']
    
    # Combine all scans
    all_scans = local_scans + azure_scans + shared_scans
    
    # Sort by start_time descending (most recent first)
    all_scans.sort(key=lambda x: x.get('start_time', ''), reverse=True)
    
    return {
        "success": True,
        "count": len(all_scans),
        "scans": all_scans
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
    container_name: str = Query(..., description="Container name to scan"),
    storage_account: str = Query(None, description="Storage account name"),
    scan_name: str = Query(None, description="Optional scan name"),
    connection_string: str = Query(None, description="Optional: Azure connection string (if not in .env)")
):
    """Scan Azure Blob Storage container"""
    scan_id = str(uuid.uuid4())
    name = scan_name or f"Azure Scan {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}"
    start_time = datetime.now()
    
    # Get connection string from parameter or environment variable
    conn_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    if not conn_string:
        raise HTTPException(
            status_code=400, 
            detail="Azure connection string not provided. Set AZURE_STORAGE_CONNECTION_STRING in .env file or pass it as a parameter."
        )
    
    # Get storage account from parameter or extract from connection string
    storage_acc = storage_account or os.getenv("AZURE_STORAGE_ACCOUNT", "unknown")
    
    # Initialize scan tracking
    with active_scans_lock:
        active_scans[scan_id] = {
            "stop": False,
            "type": "azure",
            "status": "scanning",
            "result": None,
            "error": None
        }
    
    def scan_thread():
        try:
            # Create scan record
            azure_create_scan(scan_id, name, container_name, storage_acc)
            
            # Scan Azure container with stop flag
            files = scan_azure_blob(conn_string, container_name, stop_flag=lambda: active_scans.get(scan_id, {}).get("stop", False))
            
            # Check if stopped
            if active_scans.get(scan_id, {}).get("stop", False):
                azure_fail_scan(scan_id)
                with active_scans_lock:
                    if scan_id in active_scans:
                        active_scans[scan_id]["status"] = "stopped"
                return
            
            # Save files
            azure_save_files(scan_id, files)
            
            # Get summary
            summary = azure_get_summary(files)
            
            # Complete scan
            azure_complete_scan(scan_id, summary['total_files'], summary['total_size'])
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Store result
            result = {
                "success": True,
                "scan_id": scan_id,
                "scan_name": name,
                "storage_type": "azure_blob",
                "container_name": container_name,
                "total_files": summary['total_files'],
                "total_size": summary['total_size'],
                "duration_seconds": duration,
                "file_type_distribution": summary['file_type_distribution'],
                "ocr_eligible_count": summary['ocr_eligible_count']
            }
            
            with active_scans_lock:
                if scan_id in active_scans:
                    active_scans[scan_id]["status"] = "completed"
                    active_scans[scan_id]["result"] = result
            
        except Exception as e:
            azure_fail_scan(scan_id)
            with active_scans_lock:
                if scan_id in active_scans:
                    active_scans[scan_id]["status"] = "failed"
                    active_scans[scan_id]["error"] = str(e)
    
    # Start scan in background thread
    thread = threading.Thread(target=scan_thread, daemon=True)
    thread.start()
    
    return {
        "success": True,
        "scan_id": scan_id,
        "scan_name": name,
        "container_name": container_name,
        "message": "Azure scan started in background"
    }

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
    share_path: str = Query(None, description="UNC path to shared folder (e.g., \\\\192.168.1.100\\Share)"),
    share_name: str = Query(..., description="Shared folder name/identifier"),
    scan_name: str = Query(None, description="Optional scan name")
):
    """Scan a shared directory (SMB/CIFS share)"""
    scan_id = str(uuid.uuid4())
    name = scan_name or f"Shared Scan {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}"
    start_time = datetime.now()
    
    # Get share path from parameter or environment variable
    path = share_path or os.getenv("SHARED_DIRECTORY_PATH")
    
    if not path:
        raise HTTPException(
            status_code=400, 
            detail="Shared directory path not provided. Set SHARED_DIRECTORY_PATH in .env file or pass share_path as a parameter."
        )
    
    # Initialize scan tracking
    with active_scans_lock:
        active_scans[scan_id] = {
            "stop": False,
            "type": "shared",
            "status": "scanning",
            "result": None,
            "error": None
        }
    
    def scan_thread():
        try:
            # Create scan record
            shared_create_scan(scan_id, name, path, share_name)
            
            # Scan shared directory with stop flag
            files = scan_shared_directory(path, share_name, stop_flag=lambda: active_scans.get(scan_id, {}).get("stop", False))
            
            # Check if stopped
            if active_scans.get(scan_id, {}).get("stop", False):
                shared_fail_scan(scan_id)
                with active_scans_lock:
                    if scan_id in active_scans:
                        active_scans[scan_id]["status"] = "stopped"
                return
            
            # Save files
            shared_save_files(scan_id, files)
            
            # Get summary
            summary = shared_get_summary(files)
            
            # Complete scan
            shared_complete_scan(scan_id, summary['total_files'], summary['total_size'])
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Store result
            result = {
                "success": True,
                "scan_id": scan_id,
                "scan_name": name,
                "storage_type": "shared_directory",
                "share_path": path,
                "share_name": share_name,
                "total_files": summary['total_files'],
                "total_size": summary['total_size'],
                "duration_seconds": duration,
                "file_type_distribution": summary['file_type_distribution'],
                "ocr_eligible_count": summary['ocr_eligible_count']
            }
            
            with active_scans_lock:
                if scan_id in active_scans:
                    active_scans[scan_id]["status"] = "completed"
                    active_scans[scan_id]["result"] = result
            
        except Exception as e:
            shared_fail_scan(scan_id)
            with active_scans_lock:
                if scan_id in active_scans:
                    active_scans[scan_id]["status"] = "failed"
                    active_scans[scan_id]["error"] = str(e)
    
    # Start scan in background thread
    thread = threading.Thread(target=scan_thread, daemon=True)
    thread.start()
    
    return {
        "success": True,
        "scan_id": scan_id,
        "scan_name": name,
        "share_path": path,
        "message": "Shared scan started in background"
    }


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

# ========== SCAN STATUS ENDPOINTS ==========

@app.get("/api/scan/{scan_id}/status")
async def get_scan_status(scan_id: str):
    """Get the status of an active scan"""
    with active_scans_lock:
        if scan_id in active_scans:
            scan_info = active_scans[scan_id]
            response = {
                "scan_id": scan_id,
                "status": scan_info["status"],
                "type": scan_info["type"]
            }
            
            if scan_info["status"] == "completed" and scan_info["result"]:
                response["result"] = scan_info["result"]
            elif scan_info["status"] == "failed" and scan_info["error"]:
                response["error"] = scan_info["error"]
            
            return response
        else:
            raise HTTPException(status_code=404, detail="Scan not found")

# ========== STOP SCAN ENDPOINTS ==========

@app.post("/api/scan/{scan_id}/stop")
async def stop_scan(scan_id: str):
    """Stop an active local scan"""
    with active_scans_lock:
        if scan_id in active_scans and active_scans[scan_id]["type"] == "local":
            active_scans[scan_id]["stop"] = True
            return {"success": True, "message": "Stop signal sent to local scan"}
        else:
            raise HTTPException(status_code=404, detail="Active local scan not found")

@app.post("/api/scan/azure/{scan_id}/stop")
async def stop_azure_scan(scan_id: str):
    """Stop an active Azure scan"""
    with active_scans_lock:
        if scan_id in active_scans and active_scans[scan_id]["type"] == "azure":
            active_scans[scan_id]["stop"] = True
            return {"success": True, "message": "Stop signal sent to Azure scan"}
        else:
            raise HTTPException(status_code=404, detail="Active Azure scan not found")

@app.post("/api/scan/shared/{scan_id}/stop")
async def stop_shared_scan(scan_id: str):
    """Stop an active shared directory scan"""
    with active_scans_lock:
        if scan_id in active_scans and active_scans[scan_id]["type"] == "shared":
            active_scans[scan_id]["stop"] = True
            return {"success": True, "message": "Stop signal sent to shared scan"}
        else:
            raise HTTPException(status_code=404, detail="Active shared scan not found")

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {"status": "ok", "message": "Scanner is running"}

# Mount frontend
ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
if os.path.exists(ui_dir):
    app.mount("/", StaticFiles(directory=ui_dir, html=True), name="ui")
# Run
if __name__ == "__main__":
    import uvicorn
    print("Starting Local Data Scanner...")
    print("http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

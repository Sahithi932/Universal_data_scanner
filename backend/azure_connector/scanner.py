"""
Azure Blob Storage Scanner
Scans Azure Blob Storage containers and collects file metadata
"""
from datetime import datetime
import mimetypes


def get_file_type(filename):
    """Determine file type from extension"""
    if '.' not in filename:
        return 'other'
    
    ext = filename.split('.')[-1].lower()
    
    file_types = {
        'pdf': 'pdf',
        'doc': 'office', 'docx': 'office', 'xls': 'office', 'xlsx': 'office', 'ppt': 'office', 'pptx': 'office',
        'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'bmp': 'image', 'tiff': 'image',
        'txt': 'text', 'log': 'text', 'csv': 'text',
        'zip': 'archive', 'rar': 'archive', '7z': 'archive', 'tar': 'archive', 'gz': 'archive',
        'py': 'code', 'js': 'code', 'java': 'code', 'cpp': 'code', 'html': 'code', 'css': 'code', 'sql': 'code',
        'json': 'data', 'xml': 'data', 'yaml': 'data',
    }
    
    return file_types.get(ext, 'other')


def get_mime_type(filename):
    """Get MIME type for file"""
    mime, _ = mimetypes.guess_type(filename)
    return mime or 'application/octet-stream'


def is_ocr_eligible(file_type):
    """Check if file is eligible for OCR"""
    return file_type in ['pdf', 'image', 'office']


def scan_azure_blob(connection_string, container_name, stop_flag=None):
    """
    Scan Azure Blob Storage container and return file metadata
    
    Args:
        connection_string: Azure storage account connection string
        container_name: Name of blob container to scan
        stop_flag: Callable that returns True if scan should stop
        
    Returns:
        List of file dictionaries with metadata
    """
    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError:
        raise ImportError("Azure SDK not installed. Run: pip install azure-storage-blob")
    
    files = []
    
    try:
        # Connect to blob service
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        
        # List all blobs
        blobs = container_client.list_blobs()
        
        for blob in blobs:
            # Check stop flag periodically (every 10 files)
            if stop_flag and stop_flag() and len(files) % 10 == 0:
                print(f"Azure scan stopped by user after processing {len(files)} files")
                return files
                
            # Skip if it's a directory
            if blob.name.endswith('/'):
                continue
            
            # Get file type
            file_type = get_file_type(blob.name)
            mime_type = get_mime_type(blob.name)
            ocr_eligible = is_ocr_eligible(file_type)
            
            # Create file record
            file_record = {
                'file_name': blob.name.split('/')[-1],
                'file_path': f"azure://{container_name}/{blob.name}",
                'blob_path': blob.name,
                'file_type': file_type,
                'mime_type': mime_type,
                'file_size': blob.size,
                'last_modified': blob.last_modified.isoformat() if blob.last_modified else None,
                'storage_type': 'azure_blob',
                'eligible_for_ocr': ocr_eligible,
                'container': container_name
            }
            
            files.append(file_record)
        
    except Exception as e:
        raise Exception(f"Failed to scan Azure container: {str(e)}")
    
    return files


def get_summary(files):
    """Get summary statistics from files"""
    if not files:
        return {
            'total_files': 0,
            'total_size': 0,
            'file_type_distribution': {},
            'ocr_eligible_count': 0
        }
    
    # Count by type
    type_counts = {}
    ocr_count = 0
    total_size = 0
    
    for file in files:
        ftype = file['file_type']
        type_counts[ftype] = type_counts.get(ftype, 0) + 1
        
        if file['eligible_for_ocr']:
            ocr_count += 1
        
        total_size += file['file_size']
    
    return {
        'total_files': len(files),
        'total_size': total_size,
        'file_type_distribution': type_counts,
        'ocr_eligible_count': ocr_count
    }

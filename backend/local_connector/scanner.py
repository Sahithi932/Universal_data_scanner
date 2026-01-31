"""
Local File Scanner
Recursively scans folders and collects file metadata
"""
import os
import mimetypes
from datetime import datetime


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


def scan_folder(folder_path, stop_flag=None):
    """
    Scan a folder recursively and return file metadata
    
    Args:
        folder_path: Path to folder
        stop_flag: Callable that returns True if scan should stop
        
    Returns:
        List of file dictionaries with metadata
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Not a directory: {folder_path}")
    
    files = []
    
    # Walk through all directories and files
    for root, dirs, filenames in os.walk(folder_path):
        # Check stop flag before processing each directory
        if stop_flag and stop_flag():
            print(f"Scan stopped by user")
            break
            
        for filename in filenames:
            # Check stop flag periodically (every 10 files)
            if stop_flag and stop_flag() and len(files) % 10 == 0:
                print(f"Scan stopped by user after processing {len(files)} files")
                return files
                
            try:
                full_path = os.path.join(root, filename)
                
                # Get file stats
                stat_info = os.stat(full_path)
                
                # Get file type
                file_type = get_file_type(filename)
                mime_type = get_mime_type(filename)
                ocr_eligible = is_ocr_eligible(file_type)
                
                # Create file record
                file_record = {
                    'file_name': filename,
                    'file_path': full_path,
                    'file_type': file_type,
                    'mime_type': mime_type,
                    'file_size': stat_info.st_size,
                    'last_modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    'storage_type': 'local',
                    'eligible_for_ocr': ocr_eligible
                }
                
                files.append(file_record)
                
            except (PermissionError, OSError):
                continue
            except Exception as e:
                print(f"Warning: {filename} - {e}")
                continue
    
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

"""
Shared Directory (SMB/CIFS) Scanner
Scans Windows shared folders accessible via UNC paths
"""
import os
from pathlib import Path

def scan_shared_directory(share_path, share_name):
    """
    Scan a shared directory via UNC path
    
    Args:
        share_path: UNC path (e.g., \\192.168.1.100\Share or \\server\folder)
        share_name: Human-readable share name
    
    Returns:
        List of file metadata dictionaries
    """
    files = []
    errors = []
    
    # Validate path exists and is accessible
    if not os.path.exists(share_path):
        raise FileNotFoundError(f"Shared path not accessible: {share_path}")
    
    if not os.access(share_path, os.R_OK):
        raise PermissionError(f"No read permissions on: {share_path}")
    
    try:
        # Walk through shared directory
        for root, dirs, filenames in os.walk(share_path):
            for filename in filenames:
                try:
                    file_path = os.path.join(root, filename)
                    stat = os.stat(file_path)
                    
                    files.append({
                        'file_name': filename,
                        'file_path': file_path,
                        'file_size': stat.st_size,
                        'last_modified': stat.st_mtime,
                        'is_file': True,
                        'extension': Path(filename).suffix.lower(),
                    })
                except (OSError, IOError) as e:
                    errors.append(f"Error reading {filename}: {str(e)}")
                    continue
        
        return files
    
    except Exception as e:
        raise Exception(f"Failed to scan shared directory {share_path}: {str(e)}")


def get_summary(files):
    """Generate scan summary from file list"""
    if not files:
        return {
            'total_files': 0,
            'total_size': 0,
            'file_type_distribution': {},
            'ocr_eligible_count': 0,
        }
    
    total_size = sum(f.get('file_size', 0) for f in files)
    
    # Count by file type
    file_types = {}
    ocr_eligible = ['pdf', 'png', 'jpg', 'jpeg', 'bmp', 'tiff']
    ocr_count = 0
    
    for f in files:
        ext = f.get('extension', 'unknown').lower().lstrip('.')
        if ext:
            file_types[ext] = file_types.get(ext, 0) + 1
        if f.get('extension', '').lower().lstrip('.') in ocr_eligible:
            ocr_count += 1
    
    return {
        'total_files': len(files),
        'total_size': total_size,
        'file_type_distribution': dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]),
        'ocr_eligible_count': ocr_count,
    }

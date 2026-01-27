"""
Database operations for Azure scan metadata
"""
import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scanner.db')


def init_db():
    """Initialize database and create tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create azure_scans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS azure_scans (
            id TEXT PRIMARY KEY,
            name TEXT,
            container_name TEXT,
            storage_account TEXT,
            status TEXT,
            total_files INTEGER,
            total_size INTEGER,
            start_time TEXT,
            end_time TEXT
        )
    ''')
    
    # Create azure_files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS azure_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT,
            file_name TEXT,
            blob_path TEXT,
            file_type TEXT,
            mime_type TEXT,
            file_size INTEGER,
            last_modified TEXT,
            container_name TEXT,
            eligible_for_ocr BOOLEAN,
            FOREIGN KEY (scan_id) REFERENCES azure_scans(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Azure Database initialized")


def create_scan(scan_id, name, container_name, storage_account):
    """Create a new Azure scan record"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO azure_scans (id, name, container_name, storage_account, status, start_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (scan_id, name, container_name, storage_account, 'running', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def save_files(scan_id, files):
    """Save files to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for file in files:
        cursor.execute('''
            INSERT INTO azure_files (
                scan_id, file_name, blob_path, file_type, mime_type, 
                file_size, last_modified, container_name, eligible_for_ocr
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_id,
            file['file_name'],
            file['blob_path'],
            file['file_type'],
            file['mime_type'],
            file['file_size'],
            file['last_modified'],
            file['container'],
            file['eligible_for_ocr']
        ))
    
    conn.commit()
    conn.close()


def complete_scan(scan_id, total_files, total_size):
    """Mark Azure scan as completed"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE azure_scans 
        SET status = 'completed', total_files = ?, total_size = ?, end_time = ?
        WHERE id = ?
    ''', (total_files, total_size, datetime.now().isoformat(), scan_id))
    
    conn.commit()
    conn.close()


def fail_scan(scan_id):
    """Mark Azure scan as failed"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE azure_scans SET status = 'failed', end_time = ? WHERE id = ?
    ''', (datetime.now().isoformat(), scan_id))
    
    conn.commit()
    conn.close()


def get_all_scans():
    """Get all Azure scans"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM azure_scans ORDER BY start_time DESC LIMIT 10")
    scans = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return scans


def get_scan_files(scan_id, limit=100, offset=0):
    """Get files for an Azure scan with pagination"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM azure_files WHERE scan_id = ? ORDER BY file_name LIMIT ? OFFSET ?", 
                   (scan_id, limit, offset))
    files = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return files


def get_total_files_count(scan_id):
    """Get total file count for an Azure scan"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM azure_files WHERE scan_id = ?", (scan_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else 0

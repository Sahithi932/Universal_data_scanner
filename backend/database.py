"""
Database operations for scan metadata
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
    
    # Create scans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            name TEXT,
            folder_path TEXT,
            status TEXT,
            total_files INTEGER,
            total_size INTEGER,
            start_time TEXT,
            end_time TEXT
        )
    ''')
    
    # Create files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT,
            file_name TEXT,
            file_path TEXT,
            file_type TEXT,
            mime_type TEXT,
            file_size INTEGER,
            last_modified TEXT,
            storage_type TEXT,
            eligible_for_ocr BOOLEAN,
            FOREIGN KEY (scan_id) REFERENCES scans(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")


def create_scan(scan_id, name, folder_path):
    """Create a new scan record"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scans (id, name, folder_path, status, start_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (scan_id, name, folder_path, 'running', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def save_files(scan_id, files):
    """Save files to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for file in files:
        cursor.execute('''
            INSERT INTO files (
                scan_id, file_name, file_path, file_type, mime_type, 
                file_size, last_modified, storage_type, eligible_for_ocr
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_id,
            file['file_name'],
            file['file_path'],
            file['file_type'],
            file['mime_type'],
            file['file_size'],
            file['last_modified'],
            file['storage_type'],
            file['eligible_for_ocr']
        ))
    
    conn.commit()
    conn.close()


def complete_scan(scan_id, total_files, total_size):
    """Mark scan as completed"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE scans 
        SET status = 'completed', total_files = ?, total_size = ?, end_time = ?
        WHERE id = ?
    ''', (total_files, total_size, datetime.now().isoformat(), scan_id))
    
    conn.commit()
    conn.close()


def fail_scan(scan_id):
    """Mark scan as failed"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE scans SET status = 'failed', end_time = ? WHERE id = ?
    ''', (datetime.now().isoformat(), scan_id))
    
    conn.commit()
    conn.close()


def get_all_scans():
    """Get all scans"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM scans ORDER BY start_time DESC LIMIT 10")
    scans = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return scans


def get_scan_files(scan_id, limit=100, offset=0):
    """Get files for a scan with pagination"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM files WHERE scan_id = ? ORDER BY file_name LIMIT ? OFFSET ?", 
                   (scan_id, limit, offset))
    files = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return files


def get_total_files_count(scan_id):
    """Get total file count for a scan"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM files WHERE scan_id = ?", (scan_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else 0

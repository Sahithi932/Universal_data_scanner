"""
Shared Directory Scanner - Database operations
"""
import sqlite3
import os
from datetime import datetime

# Database paths - separated for scans and files
SCANS_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scanner.db')
FILES_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'files.db')

def init_db():
    """Initialize shared scans database"""
    # Initialize scans database
    conn = sqlite3.connect(SCANS_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_scans (
            id TEXT PRIMARY KEY,
            scan_name TEXT NOT NULL,
            share_path TEXT NOT NULL,
            share_name TEXT NOT NULL,
            status TEXT DEFAULT 'running',
            total_files INTEGER,
            total_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Initialize files database
    conn = sqlite3.connect(FILES_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_scan_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            last_modified REAL,
            extension TEXT,
            file_type TEXT,
            FOREIGN KEY (scan_id) REFERENCES shared_scans(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_scan(scan_id, scan_name, share_path, share_name):
    """Create a new scan record"""
    conn = sqlite3.connect(SCANS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO shared_scans (id, scan_name, share_path, share_name, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (scan_id, scan_name, share_path, share_name, datetime.now()))
    conn.commit()
    conn.close()

def save_files(scan_id, files):
    """Save scanned files to database"""
    conn = sqlite3.connect(FILES_DB)
    cursor = conn.cursor()
    for file in files:
        cursor.execute('''
            INSERT INTO shared_scan_files 
            (scan_id, file_name, file_path, file_size, last_modified, extension, file_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_id,
            file.get('file_name'),
            file.get('file_path'),
            file.get('file_size', 0),
            file.get('last_modified'),
            file.get('extension'),
            file.get('file_type')
        ))
    conn.commit()
    conn.close()

def complete_scan(scan_id, total_files, total_size):
    """Mark scan as complete"""
    conn = sqlite3.connect(SCANS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE shared_scans 
        SET status = 'completed', total_files = ?, total_size = ?, completed_at = ?
        WHERE id = ?
    ''', (total_files, total_size, datetime.now(), scan_id))
    conn.commit()
    conn.close()

def fail_scan(scan_id):
    """Mark scan as failed"""
    conn = sqlite3.connect(SCANS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE shared_scans 
        SET status = 'failed', completed_at = ?
        WHERE id = ?
    ''', (datetime.now(), scan_id))
    conn.commit()
    conn.close()

def get_all_scans():
    """Get all shared scans"""
    conn = sqlite3.connect(SCANS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shared_scans ORDER BY created_at DESC')
    scans = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return scans

def get_scan_files(scan_id, limit=100, offset=0):
    """Get files from a specific scan"""
    conn = sqlite3.connect(FILES_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM shared_scan_files 
        WHERE scan_id = ? 
        LIMIT ? OFFSET ?
    ''', (scan_id, limit, offset))
    files = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return files

def get_total_files_count(scan_id):
    """Get total file count for a scan"""
    conn = sqlite3.connect(FILES_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM shared_scan_files WHERE scan_id = ?', (scan_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

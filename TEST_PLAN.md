# Universal Data Scanner - Test Plan

## Test Cases Overview - EDGE CASES ONLY

This document outlines edge case and boundary condition tests for the Universal Data Scanner project.

**Total Test Cases: 49**

---

## 1. Local Scanner Tests (`test_local_scanner.py`) - 14 cases

### File Type Detection Edge Cases (5 cases)
1. Test files with no extension (README, Makefile)
2. Test files with multiple dots (archive.tar.gz, backup.2024.01.zip)
3. Test unknown/custom extensions (file.xyz, file.custom)
4. Test uppercase vs lowercase extensions (PDF vs pdf)
5. Test files with only extension (.gitignore, .env)

### Folder Scanning Edge Cases (6 cases)
6. Test scanning empty folder
7. Test scanning nonexistent folder (should raise error)
8. Test scanning a file path instead of directory (should raise error)
9. Test stop flag - early termination with 20+ files
10. Test permission error handling (restricted file access)
11. Test scanning with 1000+ files (performance)
12. Test files with special characters (spaces, Unicode, @#$%)

### Summary Edge Cases (3 cases)
14. Test summary with empty file list
15. Test handling of missing/zero file sizes
16. Test total size calculation with extremely large numbers (TB+)

---

## 2. Azure Scanner Tests (`test_azure_scanner.py`) - 13 cases

### Azure Blob Scanning Edge Cases (9 cases)
1. Test scanning empty container
2. Test directory markers are skipped (folder/, subfolder/)
3. Test blobs without last_modified timestamp
4. Test Unicode characters in blob names (Cyrillic, Chinese, Emoji)
5. Test stop flag early termination (50+ blobs)
6. Test connection error handling (invalid connection string)
7. Test blobs with trailing/leading slashes
8. Test empty blob names
9. Test very long blob paths (>500 characters)

### Azure Connection Edge Cases (3 cases)
10. Test missing connection string (should raise error)
11. Test malformed connection string
12. Test network timeout handling

### Azure Summary Edge Cases (1 case)
13. Test summary with empty container

---

## 3. Shared Scanner Tests (`test_shared_scanner.py`) - 9 cases

### Shared Directory Scanning Edge Cases (7 cases)
1. Test scanning empty shared directory
2. Test scanning nonexistent share path (should raise error)
3. Test handling no read permission on share
4. Test stop flag termination (30+ files)
5. Test special characters in filenames (spaces, Unicode, @#$%)
6. Test files without extension (README, LICENSE)
7. Test very long file paths (>260 characters on Windows)

### Shared Summary Edge Cases (2 cases)
8. Test summary with empty share
9. Test handling of missing/zero file sizes

---

## 4. Database Tests (`test_database.py`) - 8 cases

### Database Edge Cases (8 cases)
1. Test duplicate scan_id prevention (IntegrityError)
2. Test save files without scan (foreign key)
3. Test complete nonexistent scan (no error, no rows updated)
4. Test get files from empty scan
5. Test special characters in names (quotes, apostrophes, Unicode)
6. Test Unicode characters (中文, Русский)
7. Test NULL values handling
8. Test pagination with offset beyond total count

---

## 5. API Endpoint Tests (`test_api.py`) - 4 cases

### API Edge Cases (4 cases)
1. Test POST /api/scan without folder_path (validation error)
2. Test POST /api/scan with nonexistent path (error)
3. Test GET /api/scans/{scan_id} for nonexistent scan (404/empty)
4. Test POST /api/scan/{scan_id}/stop for nonexistent scan (404)

---

## Test Execution Strategy

- **Unit Tests**: Fast, isolated, mocked dependencies
- **Integration Tests**: Real database operations, API calls
- **Edge Case Tests**: Boundary conditions, error handling

## Coverage Goals

- **Line Coverage**: >80%
- **Branch Coverage**: >75%
- **Function Coverage**: >85%

## Test Data Requirements

- Temporary directories for file system tests
- Mock Azure SDK for cloud tests
- Temporary SQLite databases
- Test fixtures in conftest.py

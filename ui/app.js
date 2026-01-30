const API_URL = 'http://localhost:8000/api';
let activeScanSessions = {};  // { scan_id: { name, type, files, offset, total, result } }
let activeScanId = null;  // Currently viewing
let currentScanFiles = [];
let currentStorageType = 'local';
const PAGE_SIZE = 100;
// 🔹 UI Section Switcher (Dashboard / Explorer / History)
function showMainSection(section) {

    // Hide main content sections
    document.getElementById('tabsSection').style.display = 'none';
    document.getElementById('explorerSection').style.display = 'none';

    const historySection = document.querySelectorAll('.section')[3]; 
    if (historySection) historySection.style.display = 'none';

    // Show selected section
    if (section === 'dashboard') {
        document.getElementById('tabsSection').style.display = 'block';
    }
    else if (section === 'explorer') {
        document.getElementById('explorerSection').style.display = 'block';
    }
    else if (section === 'history') {
        if (historySection) historySection.style.display = 'block';
    }
}

function toggleStorageType() {
    currentStorageType = document.querySelector('input[name="storageType"]:checked').value;
    
    if (currentStorageType === 'local') {
        document.getElementById('localInputs').style.display = 'grid';
        document.getElementById('azureInputs').style.display = 'none';
        document.getElementById('sharedInputs').style.display = 'none';
    } else if (currentStorageType === 'azure') {
        document.getElementById('localInputs').style.display = 'none';
        document.getElementById('azureInputs').style.display = 'block';
        document.getElementById('sharedInputs').style.display = 'none';
    } else if (currentStorageType === 'shared') {
        document.getElementById('localInputs').style.display = 'none';
        document.getElementById('azureInputs').style.display = 'none';
        document.getElementById('sharedInputs').style.display = 'block';
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatScanDateTime(dateString) {
    if (!dateString) return 'Unknown Date';
    
    try {
        let date;
        
        if (typeof dateString === 'string') {
            // Handle ISO format with Z
            date = new Date(dateString);
        } else if (typeof dateString === 'number') {
            date = new Date(dateString * 1000);
        } else {
            return 'Unknown Date';
        }
        
        if (isNaN(date.getTime())) {
            return 'Unknown Date';
        }
        
        return date.toLocaleString();
    } catch (e) {
        return 'Unknown Date';
    }
}

async function startLocalScan() {
    const folderPath = document.getElementById('folderPath').value.trim();
    const scanName = document.getElementById('scanName').value.trim();
    
    if (!folderPath) {
        showMessage('Please enter a folder path', 'error');
        return;
    }
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Scanning...';
    
    try {
        const url = `${API_URL}/scan?folder_path=${encodeURIComponent(folderPath)}&scan_name=${encodeURIComponent(scanName)}`;
        const response = await fetch(url, { method: 'POST' });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Scan failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Store scan session
            activeScanSessions[result.scan_id] = {
                name: result.scan_name,
                type: 'local',
                files: [],
                offset: 0,
                total: result.total_files,
                result: result
            };
            
            // Set as active scan
            activeScanId = result.scan_id;
            
            // Update UI
            updateScanTabs();
            showScanResult(result.scan_id);
            loadScans();
            showMessage('✅ Scan completed successfully!', 'success');
        }
        
    } catch (error) {
        showMessage('❌ ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Start Scanning';
    }
}

async function startAzureScan() {
    const connectionString = document.getElementById('connectionString').value.trim();
    const containerName = document.getElementById('containerName').value.trim();
    const storageAccount = document.getElementById('storageAccount').value.trim();
    const scanName = document.getElementById('azureScanName').value.trim();
    
    if (!connectionString || !containerName || !storageAccount) {
        showMessage('Please fill in all Azure fields', 'error');
        return;
    }
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Scanning Azure...';
    
    try {
        const url = `${API_URL}/scan/azure?connection_string=${encodeURIComponent(connectionString)}&container_name=${encodeURIComponent(containerName)}&storage_account=${encodeURIComponent(storageAccount)}&scan_name=${encodeURIComponent(scanName)}`;
        const response = await fetch(url, { method: 'POST' });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Scan failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Store scan session
            activeScanSessions[result.scan_id] = {
                name: result.scan_name,
                type: 'azure',
                files: [],
                offset: 0,
                total: result.total_files,
                result: result
            };
            
            // Set as active scan
            activeScanId = result.scan_id;
            
            // Update UI
            updateScanTabs();
            showScanResult(result.scan_id);
            loadScans();
            showMessage('✅ Azure scan completed successfully!', 'success');
        }
        
    } catch (error) {
        showMessage('❌ ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Scan Azure Container';
    }
}

async function startSharedScan() {
    const sharePath = document.getElementById('sharePath').value.trim();
    const shareName = document.getElementById('shareName').value.trim();
    const scanName = document.getElementById('sharedScanName').value.trim();
    
    if (!sharePath || !shareName) {
        showMessage('Please fill in Share Path and Share Name', 'error');
        return;
    }
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Scanning Shared...';
    
    try {
        const url = `${API_URL}/scan/shared?share_path=${encodeURIComponent(sharePath)}&share_name=${encodeURIComponent(shareName)}&scan_name=${encodeURIComponent(scanName)}`;
        const response = await fetch(url, { method: 'POST' });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Scan failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Store scan session
            activeScanSessions[result.scan_id] = {
                name: result.scan_name,
                type: 'shared',
                files: [],
                offset: 0,
                total: result.total_files,
                result: result
            };
            
            // Set as active scan
            activeScanId = result.scan_id;
            
            // Update UI
            updateScanTabs();
            showScanResult(result.scan_id);
            loadScans();
            showMessage('✅ Shared directory scan completed successfully!', 'success');
        }
        
    } catch (error) {
        showMessage('❌ ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Scan Shared Directory';
    }
}

function displayDashboard(result) {
    document.getElementById('totalFiles').textContent = result.total_files;
    document.getElementById('totalSize').textContent = formatBytes(result.total_size);
    document.getElementById('scanDuration').textContent = result.duration_seconds.toFixed(1) + 's';
    document.getElementById('ocrCount').textContent = result.ocr_eligible_count;
    
    // File type distribution
    let distHTML = '';
    for (const [type, count] of Object.entries(result.file_type_distribution)) {
        distHTML += `
            <div class="dist-box">
                <div class="dist-count">${count}</div>
                <div>${type.toUpperCase()}</div>
            </div>
        `;
    }
    document.getElementById('fileTypeDistribution').innerHTML = distHTML;
    
    // Load all files via pagination
    loadMoreFiles();
    
    // Store for export
    window.lastScanResult = result;
}

function updateScanTabs() {
    const tabsContainer = document.getElementById('scanTabs');
    tabsContainer.innerHTML = '';
    
    for (const scanId in activeScanSessions) {
        const session = activeScanSessions[scanId];
        const isActive = scanId === activeScanId;
        const icon = session.type === 'local' ? '📁' : session.type === 'azure' ? '☁️' : '�';
        
        const tab = document.createElement('button');
        tab.className = `tab-btn ${isActive ? 'active' : ''}`;
        tab.textContent = `${icon} ${session.name}`;
        tab.onclick = () => switchTab(scanId);
        
        tabsContainer.appendChild(tab);
    }
}

function switchTab(scanId) {
    activeScanId = scanId;
    updateScanTabs();
    loadActiveTabData();
}

function showScanResult(scanId) {
    document.getElementById('tabsSection').style.display = 'block';
    document.getElementById('mainOptions').style.display = 'block';
    updateScanTabs();
    loadActiveTabData();
}

function loadActiveTabData() {
    if (!activeScanId || !activeScanSessions[activeScanId]) {
        return;
    }
    
    const session = activeScanSessions[activeScanId];
    currentStorageType = session.type;
    currentScanFiles = session.files;
    
    displayDashboard(session.result);
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown Date';
    
    try {
        let date;

        // If it's a string, try to detect numeric string vs ISO string
        if (typeof dateString === 'string') {
            const cleaned = dateString.trim();

            // Numeric string (e.g. '1609459200' or '1609459200000')
            if (/^-?\d+(?:\.\d+)?$/.test(cleaned)) {
                const n = parseFloat(cleaned);
                // If number looks like milliseconds (large), use directly; otherwise treat as seconds
                if (n > 1e12) {
                    date = new Date(n);
                } else {
                    date = new Date(n * 1000);
                }
            } else {
                // Try ISO parse
                date = new Date(cleaned);
            }
        } else if (typeof dateString === 'number') {
            const n = dateString;
            if (n > 1e12) {
                date = new Date(n); // already milliseconds
            } else {
                date = new Date(n * 1000); // seconds -> ms
            }
        } else {
            return 'Unknown Date';
        }

        if (isNaN(date.getTime())) return 'Unknown Date';
        return date.toLocaleDateString();
    } catch (e) {
        console.error('Date parsing error:', e, 'for value:', dateString);
        return 'Unknown Date';
    }
}

function displayFiles(files) {
    // Debug: log first file to see actual data format
    if (files && files.length > 0) {
        console.log('First file data:', files[0]);
        console.log('last_modified value:', files[0].last_modified, 'type:', typeof files[0].last_modified);
    }
    
    let html = '';
    files.forEach(file => {
        html += `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-name">${file.file_name}</div>
                    <div class="file-meta">
                        ${formatBytes(file.file_size)} • ${formatDate(file.last_modified)}
                    </div>
                </div>
                <span class="file-type-badge">${file.file_type}</span>
            </div>
        `;
    });
    
    document.getElementById('fileList').innerHTML = html || '<p style="padding: 20px; text-align: center;">No files</p>';
}

async function loadMoreFiles() {
    if (!activeScanId || !activeScanSessions[activeScanId]) return;
    
    const session = activeScanSessions[activeScanId];
    
    try {
        // Determine which endpoint to use based on storage type
        let endpoint = `/scan/${activeScanId}`;
        if (session.type === 'azure') {
            endpoint = `/scan/azure/${activeScanId}`;
        } else if (session.type === 'shared') {
            endpoint = `/scan/shared/${activeScanId}`;
        }
        
        const url = `${API_URL}${endpoint}?limit=${PAGE_SIZE}&offset=${session.offset}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.files) {
            session.files = session.files.concat(data.files);
            currentScanFiles = session.files;
            displayFiles(currentScanFiles);
            
            // Update offset for next load
            session.offset += data.returned_count;
            
            // Show/hide load more button
            const btn = document.getElementById('loadMoreBtn');
            if (btn) {
                if (session.offset >= session.total) {
                    btn.style.display = 'none';
                } else {
                    btn.style.display = 'block';
                }
            }
            
            // Update pagination info
            const info = document.getElementById('paginationInfo');
            if (info) {
                info.textContent = `Showing ${currentScanFiles.length} of ${session.total} files`;
                info.style.display = 'block';
            }
            
            // Update file count
            document.getElementById('fileCount').textContent = currentScanFiles.length;
        }
    } catch (error) {
        console.error('Error loading files:', error);
    }
}


function applyFilters() {
    const type = document.getElementById('filterType').value;
    const minSize = parseInt(document.getElementById('minSize').value) * 1024 || 0;
    const maxSize = parseInt(document.getElementById('maxSize').value) * 1024 * 1024 || Infinity;
    const search = document.getElementById('searchFile').value.toLowerCase();
    
    let filtered = currentScanFiles.filter(f => {
        return (!type || f.file_type === type) &&
               f.file_size >= minSize &&
               f.file_size <= maxSize &&
               f.file_name.toLowerCase().includes(search);
    });
    
    displayFiles(filtered);
    document.getElementById('fileCount').textContent = filtered.length;
}

async function loadScans() {
    try {
        const response = await fetch(`${API_URL}/scans`);
        const data = await response.json();
        
        let html = '';
        if (data.scans && data.scans.length > 0) {
            data.scans.forEach(scan => {
                const statusClass = `status-${scan.status}`;
                // Get storage type icon
                let storageIcon = '📁'; // default local
                if (scan.storage_type === 'azure') {
                    storageIcon = '☁️';
                } else if (scan.storage_type === 'shared') {
                    storageIcon = '🌐';
                }
                
                html += `
                    <div class="scan-item" onclick="viewScan('${scan.id}', '${scan.storage_type || 'local'}')">
                        <div class="scan-header">
                            <div>
                                <strong>${storageIcon} ${scan.name}</strong>
                                <div style="font-size: 0.9rem; color: #666; margin-top: 5px;">
                                    ${scan.total_files || 0} files • ${formatBytes(scan.total_size || 0)} • ${formatScanDateTime(scan.start_time)}
                                </div>
                            </div>
                            <span class="status-badge ${statusClass}">${scan.status}</span>
                        </div>
                    </div>
                `;
            });
        }
        document.getElementById('scanHistory').innerHTML = html || '<p style="padding: 20px;">No scans yet</p>';
        
    } catch (error) {
        console.error('Error loading scans:', error);
    }
}

function viewScan(scanId, storageType) {
    // Load scan details and switch to explorer view
    loadHistoricalScan(scanId, storageType);
}

async function loadHistoricalScan(scanId, storageType) {
    try {
        // Determine which endpoint to use
        let endpoint = `/scan/${scanId}`;
        if (storageType === 'azure') {
            endpoint = `/scan/azure/${scanId}`;
        } else if (storageType === 'shared') {
            endpoint = `/scan/shared/${scanId}`;
        }
        
        // Fetch scan details
        const url = `${API_URL}${endpoint}?limit=10000&offset=0`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to load scan');
        }
        
        // Store in active sessions
        activeScanSessions[scanId] = {
            name: `Historical ${storageType} Scan`,
            type: storageType,
            files: data.files || [],
            offset: 0,
            total: data.total_files,
            result: {
                total_files: data.total_files,
                total_size: 0,
                duration_seconds: 0,
                file_type_distribution: {},
                ocr_eligible_count: 0
            }
        };
        
        activeScanId = scanId;
        updateScanTabs();
        loadActiveTabData();
        showMainSection('explorer');
        showMessage(`✅ Loaded historical ${storageType} scan`, 'success');
        
    } catch (error) {
        showMessage('❌ Error loading scan: ' + error.message, 'error');
        console.error('Load scan error:', error);
    }
}

async function exportJSON() {
    if (!activeScanId || !activeScanSessions[activeScanId]) {
        alert('No scan data to export');
        return;
    }
    
    const session = activeScanSessions[activeScanId];
    
    try {
        showMessage('📦 Fetching all files for export...', 'success');
        
        // Determine which endpoint to use
        let endpoint = `/scan/${activeScanId}`;
        if (session.type === 'azure') {
            endpoint = `/scan/azure/${activeScanId}`;
        } else if (session.type === 'shared') {
            endpoint = `/scan/shared/${activeScanId}`;
        }
        
        // Fetch ALL files (use high limit to get everything in one request)
        const url = `${API_URL}${endpoint}?limit=10000&offset=0`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (!response.ok || !data.files) {
            throw new Error(data.detail || 'Failed to fetch files');
        }
        
        // Build complete export object
        const exportData = {
            success: true,
            scan_id: activeScanId,
            scan_name: session.name,
            scan_type: session.type,
            total_files: data.files.length,
            total_size: session.result?.total_size || 0,
            duration_seconds: session.result?.duration_seconds || 0,
            file_type_distribution: session.result?.file_type_distribution || {},
            ocr_eligible_count: session.result?.ocr_eligible_count || 0,
            all_files: data.files  // ALL files with complete metadata
        };
        
        const jsonStr = JSON.stringify(exportData, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url2 = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url2;
        a.download = `scan-${data.files.length}files-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url2);
        
        showMessage(`✅ Exported all ${data.files.length} files to JSON!`, 'success');
    } catch (error) {
        showMessage('❌ Error exporting: ' + error.message, 'error');
        console.error('Export error:', error);
    }
}

async function exportCSV() {
    if (!activeScanId || !activeScanSessions[activeScanId]) {
        alert('No scan data to export');
        return;
    }
    
    const session = activeScanSessions[activeScanId];
    
    try {
        showMessage('📦 Fetching all files for export...', 'success');
        
        // Determine which endpoint to use
        let endpoint = `/scan/${activeScanId}`;
        if (session.type === 'azure') {
            endpoint = `/scan/azure/${activeScanId}`;
        } else if (session.type === 'shared') {
            endpoint = `/scan/shared/${activeScanId}`;
        }
        
        // Fetch ALL files
        const url = `${API_URL}${endpoint}?limit=10000&offset=0`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (!response.ok || !data.files) {
            throw new Error(data.detail || 'Failed to fetch files');
        }
        
        const files = data.files;
        let csv = 'File Name,File Path,File Type,MIME Type,File Size (Bytes),Last Modified,OCR Eligible\n';
        
        files.forEach(file => {
            const fileName = file.file_name ? file.file_name.replace(/"/g, '""') : '';
            const filePath = file.file_path ? file.file_path.replace(/"/g, '""') : '';
            const fileType = file.file_type || '';
            const mimeType = file.mime_type || '';
            const fileSize = file.file_size || 0;
            const lastMod = file.last_modified || '';
            const ocr = file.eligible_for_ocr ? 'Yes' : 'No';
            
            csv += `"${fileName}","${filePath}","${fileType}","${mimeType}",${fileSize},"${lastMod}","${ocr}"\n`;
        });
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url2 = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url2;
        a.download = `scan-${files.length}files-${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url2);
        
        showMessage(`✅ Exported all ${files.length} files to CSV!`, 'success');
    } catch (error) {
        showMessage('❌ Error exporting: ' + error.message, 'error');
        console.error('Export error:', error);
    }
}

function showMessage(msg, type) {
    const el = document.getElementById('scanMessage');
    el.innerHTML = `<div class="${type}">${msg}</div>`;
    setTimeout(() => el.innerHTML = '', 5000);
}

function showSection(section) {
    document.getElementById('dashboardSection').style.display = 'none';
    document.getElementById('explorerSection').style.display = 'none';
    document.getElementById('historySection').style.display = 'none';

    if (section === 'dashboard') {
        document.getElementById('dashboardSection').style.display = 'block';
    } 
    else if (section === 'explorer') {
        document.getElementById('explorerSection').style.display = 'block';
    } 
    else if (section === 'history') {
        document.getElementById('historySection').style.display = 'block';
    }
}
// Load scans on page load
document.addEventListener('DOMContentLoaded', () => {
    loadScans();
});

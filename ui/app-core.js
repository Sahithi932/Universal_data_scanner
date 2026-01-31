// CORE - Shared Variables & Scan Operations
const API_URL = 'http://localhost:8000/api';
let activeScanSessions = {};  // { scan_id: { name, type, files, offset, total, result } }
let activeScanId = null;  // Currently viewing
let currentScanFiles = [];
let currentStorageType = 'local';
const PAGE_SIZE = 100;

// ========== SCAN OPERATIONS ==========

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
        
        const startResult = await response.json();
        
        if (startResult.success) {
            const scanId = startResult.scan_id;
            
            // Set as active scan immediately
            activeScanId = scanId;
            activeScanSessions[scanId] = {
                name: startResult.scan_name,
                type: 'local',
                files: [],
                offset: 0,
                total: 0,
                result: null
            };
            
            showMessage(`📂 Scanning started: ${startResult.scan_name}`, 'success');
            
            // Poll for completion
            const pollInterval = setInterval(async () => {
                try {
                    const statusResponse = await fetch(`${API_URL}/scan/${scanId}/status`);
                    const statusData = await statusResponse.json();
                    
                    if (statusData.status === 'completed' && statusData.result) {
                        clearInterval(pollInterval);
                        
                        const result = statusData.result;
                        
                        // Update scan session with results
                        activeScanSessions[scanId].total = result.total_files;
                        activeScanSessions[scanId].result = result;
                        
                        // Update UI
                        updateScanTabs();
                        showScanResult(scanId);
                        loadScans();
                        showMessage('✅ Scan completed successfully!', 'success');
                        
                        btn.disabled = false;
                        btn.textContent = 'Start Scanning';
                        
                    } else if (statusData.status === 'failed') {
                        clearInterval(pollInterval);
                        showMessage('❌ Scan failed: ' + (statusData.error || 'Unknown error'), 'error');
                        btn.disabled = false;
                        btn.textContent = 'Start Scanning';
                        
                    } else if (statusData.status === 'stopped') {
                        clearInterval(pollInterval);
                        showMessage('🛑 Scan was stopped', 'error');
                        btn.disabled = false;
                        btn.textContent = 'Start Scanning';
                    }
                    
                } catch (error) {
                    clearInterval(pollInterval);
                    showMessage('❌ Status check failed: ' + error.message, 'error');
                    btn.disabled = false;
                    btn.textContent = 'Start Scanning';
                }
            }, 1000); // Poll every second
        }
        
    } catch (error) {
        showMessage('❌ ' + error.message, 'error');
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
        
        const startResult = await response.json();
        
        if (startResult.success) {
            const scanId = startResult.scan_id;
            
            // Set as active scan immediately
            activeScanId = scanId;
            activeScanSessions[scanId] = {
                name: startResult.scan_name,
                type: 'azure',
                files: [],
                offset: 0,
                total: 0,
                result: null
            };
            
            showMessage(`☁️ Azure scan started: ${startResult.scan_name}`, 'success');
            
            // Poll for completion
            const pollInterval = setInterval(async () => {
                try {
                    const statusResponse = await fetch(`${API_URL}/scan/${scanId}/status`);
                    const statusData = await statusResponse.json();
                    
                    if (statusData.status === 'completed' && statusData.result) {
                        clearInterval(pollInterval);
                        
                        const result = statusData.result;
                        
                        // Update scan session with results
                        activeScanSessions[scanId].total = result.total_files;
                        activeScanSessions[scanId].result = result;
                        
                        // Update UI
                        updateScanTabs();
                        showScanResult(scanId);
                        loadScans();
                        showMessage('✅ Azure scan completed successfully!', 'success');
                        
                        btn.disabled = false;
                        btn.textContent = 'Scan Azure Container';
                        
                    } else if (statusData.status === 'failed') {
                        clearInterval(pollInterval);
                        showMessage('❌ Azure scan failed: ' + (statusData.error || 'Unknown error'), 'error');
                        btn.disabled = false;
                        btn.textContent = 'Scan Azure Container';
                        
                    } else if (statusData.status === 'stopped') {
                        clearInterval(pollInterval);
                        showMessage('🛑 Azure scan was stopped', 'error');
                        btn.disabled = false;
                        btn.textContent = 'Scan Azure Container';
                    }
                    
                } catch (error) {
                    clearInterval(pollInterval);
                    showMessage('❌ Status check failed: ' + error.message, 'error');
                    btn.disabled = false;
                    btn.textContent = 'Scan Azure Container';
                }
            }, 1000); // Poll every second
        }
        
    } catch (error) {
        showMessage('❌ ' + error.message, 'error');
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
            const scanId = result.scan_id;
            
            // Set as active scan immediately
            activeScanId = scanId;
            activeScanSessions[scanId] = {
                name: result.scan_name,
                type: 'shared',
                files: [],
                offset: 0,
                total: 0,
                result: null
            };
            
            showMessage(`🌐 Shared scan started: ${result.scan_name}`, 'success');
            
            // Poll for completion
            const pollInterval = setInterval(async () => {
                try {
                    const statusResponse = await fetch(`${API_URL}/scan/${scanId}/status`);
                    const statusData = await statusResponse.json();
                    
                    if (statusData.status === 'completed' && statusData.result) {
                        clearInterval(pollInterval);
                        
                        const result = statusData.result;
                        
                        // Update scan session with results
                        activeScanSessions[scanId].total = result.total_files;
                        activeScanSessions[scanId].result = result;
                        
                        // Update UI
                        updateScanTabs();
                        showScanResult(scanId);
                        loadScans();
                        showMessage('✅ Shared scan completed successfully!', 'success');
                        
                        btn.disabled = false;
                        btn.textContent = 'Scan Shared Directory';
                        
                    } else if (statusData.status === 'failed') {
                        clearInterval(pollInterval);
                        showMessage('❌ Shared scan failed: ' + (statusData.error || 'Unknown error'), 'error');
                        btn.disabled = false;
                        btn.textContent = 'Scan Shared Directory';
                        
                    } else if (statusData.status === 'stopped') {
                        clearInterval(pollInterval);
                        showMessage('🛑 Shared scan was stopped', 'error');
                        btn.disabled = false;
                        btn.textContent = 'Scan Shared Directory';
                    }
                    
                } catch (error) {
                    clearInterval(pollInterval);
                    showMessage('❌ Status check failed: ' + error.message, 'error');
                    btn.disabled = false;
                    btn.textContent = 'Scan Shared Directory';
                }
            }, 1000); // Poll every second
        }
        
    } catch (error) {
        showMessage('❌ ' + error.message, 'error');
        btn.disabled = false;
        btn.textContent = 'Scan Shared Directory';
    }
}

// ========== STOP SCAN OPERATIONS ==========

async function stopLocalScan() {
    if (!activeScanId || !activeScanSessions[activeScanId] || activeScanSessions[activeScanId].type !== 'local') {
        showMessage('No active local scan to stop', 'error');
        return;
    }
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Stopping...';
    
    try {
        const response = await fetch(`${API_URL}/scan/${activeScanId}/stop`, { method: 'POST' });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Stop failed');
        }
        
        const result = await response.json();
        showMessage('🛑 Scan stopped successfully', 'success');
        
        // Remove from active sessions
        delete activeScanSessions[activeScanId];
        activeScanId = null;
        updateScanTabs();
        loadScans();
        
    } catch (error) {
        showMessage('❌ ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '⏹️ Stop Scan';
    }
}

async function stopAzureScan() {
    if (!activeScanId || !activeScanSessions[activeScanId] || activeScanSessions[activeScanId].type !== 'azure') {
        showMessage('No active Azure scan to stop', 'error');
        return;
    }
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Stopping...';
    
    try {
        const response = await fetch(`${API_URL}/scan/azure/${activeScanId}/stop`, { method: 'POST' });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Stop failed');
        }
        
        const result = await response.json();
        showMessage('🛑 Azure scan stopped successfully', 'success');
        
        // Remove from active sessions
        delete activeScanSessions[activeScanId];
        activeScanId = null;
        updateScanTabs();
        loadScans();
        
    } catch (error) {
        showMessage('❌ ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '⏹️ Stop Scan';
    }
}

async function stopSharedScan() {
    if (!activeScanId || !activeScanSessions[activeScanId] || activeScanSessions[activeScanId].type !== 'shared') {
        showMessage('No active shared scan to stop', 'error');
        return;
    }
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Stopping...';
    
    try {
        const response = await fetch(`${API_URL}/scan/shared/${activeScanId}/stop`, { method: 'POST' });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Stop failed');
        }
        
        const result = await response.json();
        showMessage('🛑 Shared scan stopped successfully', 'success');
        
        // Remove from active sessions
        delete activeScanSessions[activeScanId];
        activeScanId = null;
        updateScanTabs();
        loadScans();
        
    } catch (error) {
        showMessage('❌ ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '⏹️ Stop Scan';
    }
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
                    <div class="scan-item">
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

// Load scans on page load
document.addEventListener('DOMContentLoaded', () => {
    loadScans();
});

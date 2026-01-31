// UI - Display & Formatting Functions
// 🔹 UI Section Switcher (Dashboard / Explorer / History)
function showMainSection(section) {
    // Hide main content sections
    document.getElementById('tabsSection').style.display = 'none';
    document.getElementById('explorerSection').style.display = 'none';
    
    // Get the history section properly
    const historySection = document.getElementById('historySection');
    if (historySection) historySection.style.display = 'none';

    // Show selected section
    if (section === 'dashboard') {
        document.getElementById('tabsSection').style.display = 'block';
        // Reload the active tab data if there's an active scan
        if (activeScanId && activeScanSessions[activeScanId]) {
            loadActiveTabData();
        }
    }
    else if (section === 'explorer') {
        document.getElementById('explorerSection').style.display = 'block';
        // Reload file explorer if there's an active scan
        if (activeScanId && activeScanSessions[activeScanId]) {
            loadActiveTabData();
        }
    }
    else if (section === 'history') {
        if (historySection) historySection.style.display = 'block';
        loadScans(); // Reload scan history
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

function formatDate(dateString) {
    if (!dateString) return 'Unknown Date';
    
    try {
        let date;

        if (typeof dateString === 'string') {
            const cleaned = dateString.trim();
            console.log('Parsing date string:', cleaned);
            // Direct ISO string parse (handles formats like 2025-10-06T00:09:37.854322Z)
            date = new Date(cleaned);
            console.log('Parsed date:', date, 'Valid:', !isNaN(date.getTime()));
        } else if (typeof dateString === 'number') {
            // Handle Unix timestamps (seconds or milliseconds)
            const n = dateString;
            date = n > 1e12 ? new Date(n) : new Date(n * 1000);
        } else {
            return 'Unknown Date';
        }

        // Check if date is valid
        if (!date || isNaN(date.getTime())) {
            console.log('Invalid date detected for:', dateString);
            return 'Unknown Date';
        }
        
        const formatted = date.toLocaleDateString();
        console.log('Formatted date result:', formatted);
        return formatted;
    } catch (e) {
        console.error('Date parsing error:', e, 'for value:', dateString);
        return 'Unknown Date';
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
        const icon = session.type === 'local' ? '📁' : session.type === 'azure' ? '☁️' : '🌐';
        
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

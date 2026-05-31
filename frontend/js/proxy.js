/**
 * SANTOSO-GRID - Proxy JavaScript
 * Version: 1.0
 */

let proxyResults = [];
let currentFilter = 'all';

// Check proxies
async function checkProxies() {
    const proxyList = document.getElementById('proxyList').value;
    const proxyFile = document.getElementById('proxyFile');
    
    let proxies = [];
    
    // Get proxies from textarea or file
    if (proxyList.trim()) {
        proxies = proxyList.split('\n').filter(p => p.trim());
    } else if (proxyFile.files.length) {
        const content = await readFile(proxyFile.files[0]);
        proxies = content.split('\n').filter(p => p.trim());
    }
    
    if (proxies.length === 0) {
        alert('Please add some proxies to check');
        return;
    }
    
    // Show loading
    const tbody = document.getElementById('proxyTableBody');
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Checking proxies...</td></tr>';
    
    try {
        const response = await fetch('/api/proxy/check', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({proxies: proxies})
        });
        
        const data = await response.json();
        proxyResults = data.results;
        
        renderProxies();
        updateStats();
        
    } catch (e) {
        alert('Error checking proxies: ' + e.message);
    }
}

// Render proxies
function renderProxies() {
    const tbody = document.getElementById('proxyTableBody');
    
    let filtered = proxyResults;
    if (currentFilter !== 'all') {
        filtered = proxyResults.filter(p => p.status === currentFilter);
    }
    
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No proxies found</td></tr>';
        return;
    }
    
    tbody.innerHTML = filtered.map((p, i) => `
        <tr>
            <td>${i + 1}</td>
            <td>${p.proxy}</td>
            <td>${p.type.toUpperCase()}</td>
            <td><span class="status-badge ${p.status}">${p.status.toUpperCase()}</span></td>
            <td>${p.response_time}ms</td>
        </tr>
    `).join('');
}

// Filter proxies
function filterProxies(filter) {
    currentFilter = filter;
    
    // Update buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    renderProxies();
}

// Update stats
function updateStats() {
    const total = proxyResults.length;
    const working = proxyResults.filter(p => p.status === 'live').length;
    const dead = proxyResults.filter(p => p.status === 'dead').length;
    
    document.getElementById('totalProxies').textContent = total;
    document.getElementById('workingProxies').textContent = working;
    document.getElementById('deadProxies').textContent = dead;
    
    // Enable download if working proxies
    document.getElementById('downloadBtn').disabled = working === 0;
}

// Download working proxies
function downloadWorking() {
    const working = proxyResults.filter(p => p.status === 'live');
    const content = working.map(p => p.proxy).join('\n');
    
    downloadFile(content, 'working_proxies.txt', 'text/plain');
}

// Handle file upload
function handleFileUpload(inputId, callback) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        readFile(file).then(callback);
    });
}

// Read file
function readFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = e => reject(e);
        reader.readAsText(file);
    });
}

// Download file
function downloadFile(content, filename, type = 'text/plain') {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Proxy loaded');
    
    // Handle file uploads
    handleFileUpload('proxyFile', (content) => {
        document.getElementById('proxyList').value = content;
    });
});
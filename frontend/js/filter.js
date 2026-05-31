/**
 * SANTOSO-GRID - Filter JavaScript
 * Version: 1.0
 */

let domainResults = {};

// Filter emails
async function filterEmails() {
    const emailList = document.getElementById('emailList').value;
    const emailFile = document.getElementById('emailFile');
    const filterDomains = document.getElementById('filterDomains').value;
    
    let emails = [];
    
    // Get emails from textarea or file
    if (emailList.trim()) {
        emails = emailList.split('\n').map(e => e.trim()).filter(e => e);
    } else if (emailFile.files.length) {
        const content = await readFile(emailFile.files[0]);
        emails = content.split('\n').map(e => e.trim()).filter(e => e);
    }
    
    if (emails.length === 0) {
        alert('Please add some emails to filter');
        return;
    }
    
    // Parse filter domains
    let domains = filterDomains.split(',').map(d => d.trim()).filter(d => d);
    
    // If no domains specified, extract all unique domains
    if (domains.length === 0) {
        const domainSet = new Set();
        emails.forEach(email => {
            const domain = email.split('@')[1];
            if (domain) domainSet.add(domain);
        });
        domains = Array.from(domainSet);
    }
    
    try {
        const response = await fetch('/api/filter/maillist', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                emails: emails,
                domains: domains
            })
        });
        
        const data = await response.json();
        domainResults = data.results;
        
        renderDomains();
        updateFilterStats(emails.length);
        
    } catch (e) {
        // Fallback: client-side filtering
        filterEmailsClientSide(emails, domains);
    }
}

// Client-side filtering (fallback)
function filterEmailsClientSide(emails, domains) {
    domainResults = {};
    
    emails.forEach(email => {
        const domain = email.split('@')[1] || 'unknown';
        
        if (!domainResults[domain]) {
            domainResults[domain] = { count: 0, emails: [] };
        }
        domainResults[domain].count++;
        domainResults[domain].emails.push(email);
    });
    
    // Filter by domain if specified
    if (domains.length > 0) {
        const filtered = {};
        domains.forEach(d => {
            d = d.toLowerCase().replace('@', '');
            for (const [domain, data] of Object.entries(domainResults)) {
                if (domain.toLowerCase().includes(d)) {
                    filtered[domain] = data;
                }
            }
        });
        domainResults = filtered;
    }
    
    renderDomains();
    updateFilterStats(emails.length);
}

// Render domains
function renderDomains() {
    const container = document.getElementById('domainList');
    
    const domainItems = Object.entries(domainResults)
        .sort((a, b) => b[1].count - a[1].count);
    
    if (domainItems.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No domains found</p></div>';
        return;
    }
    
    container.innerHTML = domainItems.map(([domain, data]) => `
        <div class="domain-item">
            <input type="checkbox" data-domain="${domain}" checked>
            <span class="domain-name">@${domain}</span>
            <span class="domain-count">${data.count.toLocaleString()} emails</span>
            <button class="btn btn-sm btn-secondary" onclick="downloadDomain('${domain}')">
                ⬇️ Download
            </button>
        </div>
    `).join('');
}

// Select all domains
function selectAllDomains() {
    document.querySelectorAll('.domain-item input').forEach(cb => {
        cb.checked = true;
    });
}

// Deselect all domains
function deselectAllDomains() {
    document.querySelectorAll('.domain-item input').forEach(cb => {
        cb.checked = false;
    });
}

// Download selected
function downloadSelected() {
    const selected = [];
    
    document.querySelectorAll('.domain-item input:checked').forEach(cb => {
        const domain = cb.dataset.domain;
        if (domainResults[domain]) {
            selected.push(...domainResults[domain].emails);
        }
    });
    
    if (selected.length === 0) {
        alert('No domains selected');
        return;
    }
    
    const content = selected.join('\n');
    downloadFile(content, 'filtered_emails.txt', 'text/plain');
}

// Download single domain
function downloadDomain(domain) {
    if (!domainResults[domain]) return;
    
    const emails = domainResults[domain].emails;
    const content = emails.join('\n');
    downloadFile(content, `${domain}_emails.txt`, 'text/plain');
}

// Update filter stats
function updateFilterStats(totalEmails) {
    const filteredEmails = Object.values(domainResults).reduce((sum, d) => sum + d.count, 0);
    const uniqueDomains = Object.keys(domainResults).length;
    
    document.getElementById('totalEmails').textContent = totalEmails.toLocaleString();
    document.getElementById('filteredEmails').textContent = filteredEmails.toLocaleString();
    document.getElementById('uniqueDomains').textContent = uniqueDomains;
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

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Filter loaded');
    
    handleFileUpload('emailFile', (content) => {
        document.getElementById('emailList').value = content;
    });
});
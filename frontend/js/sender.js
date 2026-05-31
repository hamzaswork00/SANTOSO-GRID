/**
 * SANTOSO-GRID - Sender JavaScript
 * Version: 1.0
 */

let contentType = 'text';
let campaignRunning = false;
let statusInterval = null;
let campaignId = null;

// Set content type
function setContentType(type) {
    contentType = type;
    const btns = document.querySelectorAll('.toggle-btn');
    btns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === type);
    });
}

// Start campaign
async function startCampaign() {
    const fromName = document.getElementById('fromName').value;
    const fromEmail = document.getElementById('fromEmail').value;
    const subject = document.getElementById('subject').value;
    const content = document.getElementById('content').value;
    const maillistFile = document.getElementById('maillistFile');
    const proxyType = document.getElementById('proxyType').value;
    
    // Validation
    if (!fromName || !fromEmail || !subject || !content) {
        alert('Please fill all fields');
        return;
    }
    
    if (!maillistFile.files.length) {
        alert('Please upload a maillist file');
        return;
    }
    
    // Get maillist
    const maillist = await readFile(maillistFile.files[0]);
    const emails = maillist.split('\n').filter(e => e.trim());
    
    if (emails.length === 0) {
        alert('No valid emails found in file');
        return;
    }
    
    // Start campaign
    try {
        const response = await fetch('/api/start-campaign', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                from_name: fromName,
                from_email: fromEmail,
                subject: subject,
                content: content,
                content_type: contentType,
                maillist: emails,
                proxy_type: proxyType
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'started') {
            campaignId = data.campaign_id;
            campaignRunning = true;
            
            // Update UI
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('remainingCount').textContent = formatNumber(data.total_emails);
            
            // Start status polling
            statusInterval = setInterval(getStatus, 1000);
            
            alert(`Campaign started! ${data.total_emails} emails queued.`);
        }
    } catch (e) {
        alert('Error starting campaign: ' + e.message);
    }
}

// Stop campaign
async function stopCampaign() {
    if (!campaignRunning) return;
    
    try {
        await fetch('/api/stop-campaign', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({campaign_id: campaignId})
        });
        
        campaignRunning = false;
        clearInterval(statusInterval);
        
        document.getElementById('stopBtn').disabled = true;
        
        alert('Campaign stopped!');
    } catch (e) {
        alert('Error stopping campaign: ' + e.message);
    }
}

// Get status
async function getStatus() {
    if (!campaignRunning) return;
    
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'idle') {
            campaignRunning = false;
            clearInterval(statusInterval);
            document.getElementById('stopBtn').disabled = true;
            return;
        }
        
        // Update UI
        const sent = data.sent || 0;
        const failed = data.failed || 0;
        const remaining = data.remaining || 0;
        const total = sent + failed + remaining;
        
        // Calculate percentage
        const percent = total > 0 ? Math.round((sent + failed) / total * 100) : 0;
        
        document.getElementById('sentCount').textContent = formatNumber(sent);
        document.getElementById('failedCount').textContent = formatNumber(failed);
        document.getElementById('remainingCount').textContent = formatNumber(remaining);
        document.getElementById('progressFill').style.width = percent + '%';
        document.getElementById('progressText').textContent = percent + '%';
        document.getElementById('currentEmail').textContent = data.current || '-';
        
        // Calculate speed
        if (data.start_time) {
            const start = new Date(data.start_time);
            const now = new Date();
            const hours = (now - start) / 3600000;
            const speed = hours > 0 ? Math.round(sent / hours) : sent;
            document.getElementById('sendingSpeed').textContent = formatNumber(speed) + '/hr';
        }
    } catch (e) {
        console.error(e);
    }
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

// Format number
function formatNumber(num) {
    return num.toLocaleString();
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sender loaded');
});
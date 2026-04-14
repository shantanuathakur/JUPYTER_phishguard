const API_BASE = 'http://localhost:8000';

// DOM Elements
const navButtons = document.querySelectorAll('.nav-links button');
const sections = document.querySelectorAll('.section');
const checkBtn = document.getElementById('btn-check');
const scanBtn = document.getElementById('btn-scan');
const clearHistoryBtn = document.getElementById('btn-clear-history');
const urlInput = document.getElementById('url-input');
const emailInput = document.getElementById('email-input');
const historyTable = document.querySelector('#history-table tbody');
const blockedTable = document.querySelector('#blocked-table tbody');

// Tab Switching
navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const target = btn.dataset.target;
        
        navButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        sections.forEach(s => {
            s.classList.remove('active');
            if (s.id === target) s.classList.add('active');
        });

        if (target === 'history') loadHistory();
        if (target === 'blocked') loadBlocked();
    });
});

// --- API Functions ---

// 1. Single URL Checker
async function checkURL() {
    const url = urlInput.value.trim();
    if (!url) return alert('Please enter a URL');

    const resultDiv = document.getElementById('single-result');
    const loader = document.getElementById('check-loader');
    
    setLoading(checkBtn, loader, true);
    resultDiv.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        displaySingleResult(data);
    } catch (error) {
        console.error('Error checking URL:', error);
        alert('Failed to connect to backend.');
    } finally {
        setLoading(checkBtn, loader, false);
    }
}

function displaySingleResult(data) {
    const resultDiv = document.getElementById('single-result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = `
        <div class="result-card ${data.label}">
            <span class="badge ${data.label}">${data.label}</span>
            <h3>${data.url}</h3>
            <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
            <ul class="reasons">
                ${data.reasons.map(r => `<li>${r}</li>`).join('')}
            </ul>
            ${data.label === 'phishing' ? `<button class="primary danger small" style="margin-top:15px" onclick="blockURL('${data.url}')">Block Permanently</button>` : ''}
        </div>
    `;
}

// 2. Bulk Email Scanner
async function scanEmail() {
    const text = emailInput.value.trim();
    if (!text) return alert('Please paste some email content');

    // Extract URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const urls = [...new Set(text.match(urlRegex))];

    if (urls.length === 0) return alert('No URLs found in the text');

    const resultsDiv = document.getElementById('batch-results');
    const loader = document.getElementById('scan-loader');
    
    setLoading(scanBtn, loader, true);
    resultsDiv.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/predict-batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ urls })
        });
        
        const data = await response.json();
        displayBatchResults(data.results);
    } catch (error) {
        console.error('Error scanning batch:', error);
    } finally {
        setLoading(scanBtn, loader, false);
    }
}

function displayBatchResults(results) {
    const resultsDiv = document.getElementById('batch-results');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = '<h3>Scanner Results:</h3>';
    
    results.forEach(res => {
        resultsDiv.innerHTML += `
            <div class="result-card ${res.label}">
                <div class="flex" style="justify-content: space-between">
                    <div>
                        <span class="badge ${res.label}">${res.label}</span>
                        <span class="url-text">${res.url}</span>
                    </div>
                    ${res.label === 'phishing' ? `<button class="primary danger small" onclick="blockURL('${res.url}')">Block</button>` : ''}
                </div>
            </div>
        `;
    });
}

// 3. History Management
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/history?limit=20`);
        const data = await response.json();
        
        historyTable.innerHTML = data.history.length === 0 ? '<tr><td colspan="4">No scan history found.</td></tr>' : '';
        
        data.history.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="url-text" title="${item.url}">${item.url}</span></td>
                <td><span class="badge ${item.label}">${item.label}</span></td>
                <td>${(item.confidence * 100).toFixed(1)}%</td>
                <td>${item.label === 'phishing' ? `<button class="primary danger small" onclick="blockURL('${item.url}')">Block</button>` : '—'}</td>
            `;
            historyTable.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

async function clearHistory() {
    if (!confirm('Are you sure you want to clear all history?')) return;
    try {
        await fetch(`${API_BASE}/history`, { method: 'DELETE' });
        loadHistory();
    } catch (error) {
        console.error('Error clearing history:', error);
    }
}

// 4. Blocklist Management
async function loadBlocked() {
    try {
        const response = await fetch(`${API_BASE}/blocked`);
        const data = await response.json();
        
        blockedTable.innerHTML = data.blocked.length === 0 ? '<tr><td colspan="3">No blocked URLs.</td></tr>' : '';
        
        data.blocked.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="url-text" title="${item.url}">${item.url}</span></td>
                <td>${new Date(item.blocked_at).toLocaleString()}</td>
                <td><button class="primary outline small" onclick="unblockURL('${item.url}')">Unblock</button></td>
            `;
            blockedTable.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading blocked:', error);
    }
}

async function blockURL(url) {
    try {
        const response = await fetch(`${API_BASE}/block`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, action: 'block' })
        });
        const data = await response.json();
        if (data.success) {
            alert('URL Blocked Successfully');
            loadHistory();
            loadBlocked();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error blocking URL:', error);
    }
}

async function unblockURL(url) {
    try {
        await fetch(`${API_BASE}/block`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, action: 'unblock' })
        });
        loadBlocked();
    } catch (error) {
        console.error('Error unblocking URL:', error);
    }
}

// --- Utilities ---
function setLoading(btn, loader, isLoading) {
    btn.disabled = isLoading;
    loader.style.display = isLoading ? 'inline-block' : 'none';
}

// Event Listeners
checkBtn.onclick = checkURL;
scanBtn.onclick = scanEmail;
clearHistoryBtn.onclick = clearHistory;

// Init
loadHistory();

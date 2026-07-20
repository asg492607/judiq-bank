// ══════════════════════════════════════════════════════════
// JudiQ Bank Edition — Core Application Logic v2.0
// ══════════════════════════════════════════════════════════

const API_BASE = 'http://127.0.0.1:8000/api/v1/bank';
let authToken = localStorage.getItem('judiq_token');
let currentUser = JSON.parse(localStorage.getItem('judiq_user') || 'null');
let recoveryChartInstance = null;
let riskChartInstance = null;
let detailedRiskChartInstance = null;
let complianceChartInstance = null;
let currentAssignCaseId = null;
let currentStatusCaseId = null;
let currentDraftNoticeId = null;
let currentExportData = null;
let currentDraftDeadline = null;

// ══════════════════════════════════════
// Toast Notification System
// ══════════════════════════════════════

function showToast(message, type = 'success', duration = 3500) {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = 'position:fixed;top:20px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;pointer-events:none;';
        document.body.appendChild(container);
    }
    const icons = { success: 'check-circle', error: 'times-circle', warning: 'exclamation-triangle', info: 'info-circle' };
    const colors = { success: '#10b981', error: '#ef4444', warning: '#f59e0b', info: '#0ea5e9' };
    const toast = document.createElement('div');
    toast.style.cssText = `background:#fff;border:1px solid #e2e8f0;border-left:4px solid ${colors[type]||colors.info};border-radius:10px;padding:14px 18px;box-shadow:0 8px 25px rgba(0,0,0,0.1);display:flex;align-items:center;gap:12px;font-family:Inter,sans-serif;font-size:0.88rem;color:#1e293b;min-width:300px;max-width:420px;pointer-events:all;transform:translateX(110%);transition:transform 0.35s cubic-bezier(0.4,0,0.2,1),opacity 0.35s;opacity:0;`;
    toast.innerHTML = `<i class="fas fa-${icons[type]||'info-circle'}" style="color:${colors[type]||colors.info};font-size:1.1rem;flex-shrink:0;"></i><span style="flex:1;">${message}</span><button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:#94a3b8;font-size:1rem;padding:0;line-height:1;">&times;</button>`;
    container.appendChild(toast);
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
        });
    });
    setTimeout(() => {
        toast.style.transform = 'translateX(110%)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

// ══════════════════════════════════════
// App Init
// ══════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    if (authToken) {
        showDashboard();
    }
});

function apiHeaders(extra = {}) {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
        ...extra
    };
}

async function apiFetch(path, opts = {}) {
    const res = await fetch(API_BASE + path, {
        headers: apiHeaders(),
        ...opts
    });
    if (res.status === 401) {
        handleLogout();
        throw new Error('Session expired. Please log in again.');
    }
    return res;
}

// ══════════════════════════════════════
// Authentication
// ══════════════════════════════════════

function initAuth() {
    const loginForm = document.getElementById('loginForm');
    const regForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('loginBtn');
            const errorMsg = document.getElementById('loginError');
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;

            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
            btn.disabled = true;
            errorMsg.style.display = 'none';

            try {
                const res = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();

                if (data.success && data.access_token) {
                    authToken = data.access_token;
                    currentUser = data.user;
                    localStorage.setItem('judiq_token', authToken);
                    localStorage.setItem('judiq_user', JSON.stringify(currentUser));
                    const authScreen = document.getElementById('authScreen');
                    authScreen.style.opacity = '0';
                    setTimeout(() => {
                        authScreen.style.display = 'none';
                        showDashboard();
                    }, 400);
                } else {
                    showError('loginError', data.message || 'Invalid credentials.');
                }
            } catch (err) {
                showError('loginError', 'Server connection failed. Make sure backend is running on port 8000.');
            } finally {
                btn.innerHTML = 'Sign In to Dashboard';
                btn.disabled = false;
            }
        });
    }

    if (regForm) {
        regForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('regBtn');
            const name = document.getElementById('regName').value.trim();
            const email = document.getElementById('regEmail').value.trim();
            const password = document.getElementById('regPassword').value;

            if (password.length < 6) {
                showError('regError', 'Password must be at least 6 characters.');
                return;
            }

            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
            btn.disabled = true;

            try {
                const res = await fetch(`${API_BASE}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });
                const data = await res.json();
                if (data.success) {
                    toggleAuth('login');
                    showError('loginError', '✅ ' + data.message);
                    document.getElementById('loginError').style.color = '#10b981';
                    document.getElementById('loginError').style.display = 'block';
                } else {
                    showError('regError', data.message || 'Registration failed.');
                }
            } catch (err) {
                showError('regError', 'Server connection failed.');
            } finally {
                btn.innerHTML = 'Create Account';
                btn.disabled = false;
            }
        });
    }
}

function toggleAuth(mode) {
    document.getElementById('loginForm').style.display = mode === 'register' ? 'none' : 'block';
    document.getElementById('registerForm').style.display = mode === 'register' ? 'block' : 'none';
    document.getElementById('authSubtitle').textContent = mode === 'register' ? 'Create Officer Account' : 'Enterprise Legal & Recovery OS';
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('judiq_token');
    localStorage.removeItem('judiq_user');
    location.reload();
}

function showError(id, msg) {
    const el = document.getElementById(id);
    if (el) { el.textContent = msg; el.style.display = 'block'; }
}

// ══════════════════════════════════════
// Dashboard Initialization
// ══════════════════════════════════════

function showDashboard() {
    document.getElementById('authScreen').style.display = 'none';
    document.getElementById('appContainer').style.display = 'flex';

    updateUserProfile();
    initNavigation();
    initCharts();
    initSearch();
    fetchDashboardData();
    fetchRecentCases();
    fetchRecoveryCases();
    fetchRiskData();
    fetchNotices();
    fetchLitigationCases();
    fetchComplianceData();
    initNoticeGenerator();
    initScoringForm();
    initProfileForm();
    fetchNotifications();
    loadSystemInfo();
    checkApiHealth();
}

function updateUserProfile() {
    if (!currentUser) return;
    const name = currentUser.name || 'Admin User';
    const role = currentUser.role || 'Officer';
    const initials = name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase();

    ['sidebarAvatar', 'settingsAvatar'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = initials;
    });
    ['sidebarUserName', 'settingsUserName'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = name;
    });
    ['sidebarUserRole', 'settingsUserRole'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = role;
    });
    const nameInput = document.getElementById('profileName');
    if (nameInput) nameInput.value = name;
}

// ══════════════════════════════════════
// Navigation
// ══════════════════════════════════════

function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.getAttribute('data-view');
            navigateTo(view);
        });
    });
}

function navigateTo(view) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const navItem = document.querySelector(`.nav-item[data-view="${view}"]`);
    if (navItem) navItem.classList.add('active');

    document.querySelectorAll('.view-pane').forEach(p => {
        p.classList.remove('active');
        p.classList.add('hidden');
    });

    const target = document.getElementById(`view-${view}`);
    if (target) {
        target.classList.remove('hidden');
        target.classList.add('active');
    }

    // Refresh data on navigation
    if (view === 'litigation') fetchLitigationCases();
    if (view === 'compliance') fetchComplianceData();
    if (view === 'risk-scoring') fetchRiskData();
    if (view === 'settings') { loadSystemInfo(); checkApiHealth(); }
    if (view === 'notices') fetchNotices();
    if (view === 'recovery') fetchRecoveryCases();
}

// ══════════════════════════════════════
// Charts
// ══════════════════════════════════════

function initCharts() {
    const ctxRecovery = document.getElementById('recoveryChart');
    if (ctxRecovery && !recoveryChartInstance) {
        recoveryChartInstance = new Chart(ctxRecovery, {
            type: 'line',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#475569' } } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#e2e8f0' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }
    const ctxRisk = document.getElementById('riskChart');
    if (ctxRisk && !riskChartInstance) {
        riskChartInstance = new Chart(ctxRisk, {
            type: 'bar',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#e2e8f0' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }
}

// ══════════════════════════════════════
// Search
// ══════════════════════════════════════

function initSearch() {
    const input = document.getElementById('globalSearchInput');
    const dropdown = document.getElementById('searchDropdown');
    if (!input) return;

    let debounceTimer;
    input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const q = input.value.trim();
        if (q.length < 2) { dropdown.classList.add('hidden'); return; }
        debounceTimer = setTimeout(() => performSearch(q), 350);
    });

    document.addEventListener('click', (e) => {
        if (!document.getElementById('searchBarContainer').contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });
}

async function performSearch(q) {
    const dropdown = document.getElementById('searchDropdown');
    dropdown.innerHTML = '<div class="search-loading"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';
    dropdown.classList.remove('hidden');

    try {
        const res = await apiFetch(`/search?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        if (data.results && data.results.length > 0) {
            dropdown.innerHTML = data.results.map(r => `
                <div class="search-result-item" onclick="handleSearchClick('${r.source}')">
                    <div class="search-result-main">
                        <strong>${r.case_id}</strong> — ${r.borrower}
                        <span class="status-badge status-info" style="margin-left: 8px; font-size: 0.7rem;">${r.source}</span>
                    </div>
                    <div class="search-result-sub">${r.exposure} · ${r.status}</div>
                </div>
            `).join('');
        } else {
            dropdown.innerHTML = '<div class="search-no-result">No results found for "' + q + '"</div>';
        }
    } catch (e) {
        dropdown.innerHTML = '<div class="search-no-result">Search failed. Check backend connection.</div>';
    }
}

function handleSearchClick(source) {
    document.getElementById('searchDropdown').classList.add('hidden');
    document.getElementById('globalSearchInput').value = '';
    const viewMap = { 'intake': 'case-intake', 'recovery': 'recovery', 'litigation': 'litigation' };
    navigateTo(viewMap[source] || 'dashboard');
}

// ══════════════════════════════════════
// Dashboard Data
// ══════════════════════════════════════

async function fetchDashboardData() {
    try {
        const res = await apiFetch('/dashboard');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (data.kpis) {
            document.getElementById('kpi-exposure').textContent = '₹' + (data.kpis.total_exposure_cr || 0).toLocaleString() + ' Cr';
            document.getElementById('kpi-cases').textContent = (data.kpis.active_litigation_cases || 0).toLocaleString();
            document.getElementById('kpi-score').textContent = (data.kpis.compliance_score_percent || 0) + '%';
            document.getElementById('kpi-predicted').textContent = '₹' + (data.kpis.predicted_recovery_cr || 0).toLocaleString() + ' Cr';
        }

        if (recoveryChartInstance && data.recovery_trajectory) {
            recoveryChartInstance.data.labels = data.recovery_trajectory.labels;
            recoveryChartInstance.data.datasets = [
                {
                    label: 'Legal Recovery (Cr)',
                    data: data.recovery_trajectory.legal_recovery,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2, tension: 0.4, fill: true
                },
                {
                    label: 'Settlement Recovery (Cr)',
                    data: data.recovery_trajectory.settlement_recovery,
                    borderColor: '#0ea5e9',
                    backgroundColor: 'rgba(14, 165, 233, 0.1)',
                    borderWidth: 2, tension: 0.4, fill: true
                }
            ];
            recoveryChartInstance.update();
        }

        if (riskChartInstance && data.risk_heatmap) {
            riskChartInstance.data.labels = data.risk_heatmap.categories;
            riskChartInstance.data.datasets = [{
                label: 'Number of Cases',
                data: data.risk_heatmap.case_counts,
                backgroundColor: ['#ef4444', '#f59e0b', 'rgba(239,68,68,0.7)', 'rgba(245,158,11,0.5)', '#10b981'],
                borderWidth: 0, borderRadius: 4
            }];
            riskChartInstance.update();
        }
    } catch (err) {
        console.error('Dashboard fetch error:', err.message);
        const fields = ['kpi-exposure', 'kpi-cases', 'kpi-score', 'kpi-predicted'];
        fields.forEach(id => {
            const el = document.getElementById(id);
            if (el && el.textContent === 'Loading...') el.textContent = 'Offline';
        });
    }
}

// ══════════════════════════════════════
// Case Intake
// ══════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    if (!uploadZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(ev =>
        uploadZone.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); })
    );
    ['dragenter', 'dragover'].forEach(ev =>
        uploadZone.addEventListener(ev, () => uploadZone.classList.add('dragover'))
    );
    ['dragleave', 'drop'].forEach(ev =>
        uploadZone.addEventListener(ev, () => uploadZone.classList.remove('dragover'))
    );
    uploadZone.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
    if (fileInput) fileInput.addEventListener('change', function () { handleFiles(this.files); });
});

function handleFiles(files) {
    if (files.length > 0) simulateUploadAndOCR(files[0]);
}

function simulateUploadAndOCR(file) {
    const allowedExt = ['.pdf', '.csv', '.zip', '.txt', '.docx'];
    const ext = file.name.includes('.') ? '.' + file.name.split('.').pop().toLowerCase() : '';
    if (ext && !allowedExt.includes(ext)) {
        alert(`File type '${ext}' is not allowed.\nAccepted: PDF, CSV, ZIP, TXT, DOCX`);
        return;
    }

    const progressDiv = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const percentText = document.getElementById('uploadPercent');
    const filenameText = document.getElementById('uploadFilename');
    const resultDiv = document.getElementById('uploadResult');

    filenameText.textContent = `Processing ${file.name}...`;
    progressDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    progressFill.style.width = '0%';
    percentText.textContent = '0%';

    let progress = 0;
    const interval = setInterval(async () => {
        progress += Math.random() * 18;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch(`${API_BASE}/cases/upload`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${authToken}` },
                    body: formData
                });
                const data = await res.json();
                progressDiv.classList.add('hidden');

                if (data.success) {
                    document.getElementById('uploadResultCaseId').textContent = `✅ Case ${data.case_id} Created`;
                    document.getElementById('uploadResultDetail').textContent = `Borrower: ${data.details?.borrower_name} · Exposure: ${data.details?.exposure_formatted} · Confidence: ${(data.details?.confidence_score * 100).toFixed(0)}%`;
                    resultDiv.classList.remove('hidden');
                    showToast(`Case ${data.case_id} created successfully!`, 'success');
                    fetchRecentCases();
                } else {
                    showToast('Upload failed: ' + (data.detail || 'Unknown error'), 'error');
                }
            } catch (err) {
                progressDiv.classList.add('hidden');
                showToast('Upload failed: Could not reach the server. Is the backend running?', 'error', 5000);
            }
        }
        progressFill.style.width = progress + '%';
        percentText.textContent = Math.round(progress) + '%';
    }, 250);
}

async function fetchRecentCases() {
    const tbody = document.getElementById('recentCasesBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:16px;"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';

    try {
        const res = await apiFetch('/cases/recent');
        const data = await res.json();
        tbody.innerHTML = '';

        if (!data.cases || data.cases.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#94a3b8;">No cases yet. Upload a document to begin.</td></tr>';
            return;
        }

        data.cases.forEach(c => {
            let sc = 'status-info';
            if (c.status.includes('Completed')) sc = 'status-success';
            if (c.status.includes('Duplicate') || c.status.includes('Error')) sc = 'status-warning';
            const riskColor = c.risk === 'High' ? '#ef4444' : c.risk === 'Medium' ? '#f59e0b' : '#10b981';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${c.case_id}</strong></td>
                <td>${c.borrower}</td>
                <td>${c.exposure}</td>
                <td><span class="status-badge ${sc}">${c.status}</span></td>
                <td><button class="btn btn-sm btn-outline" onclick="openCaseDetail('${c.case_id}')"><i class="fas fa-eye"></i> View</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#ef4444;">Failed to load cases. Is the backend running?</td></tr>`;
    }
}

function openCaseDetail(caseId) {
    const modal = document.getElementById('caseDetailModal');
    const body = document.getElementById('caseDetailBody');
    body.innerHTML = '<div style="text-align:center;padding:30px;"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
    modal.style.display = 'flex';
    setTimeout(() => modal.style.opacity = '1', 10);

    apiFetch(`/cases/${caseId}`).then(r => r.json()).then(data => {
        if (data.case) {
            const c = data.case;
            body.innerHTML = `
                <div class="detail-grid">
                    <div class="detail-item"><span class="detail-label">Case ID</span><span class="detail-value"><strong>${c.case_id}</strong></span></div>
                    <div class="detail-item"><span class="detail-label">Borrower</span><span class="detail-value">${c.borrower}</span></div>
                    <div class="detail-item"><span class="detail-label">Exposure</span><span class="detail-value">${c.exposure}</span></div>
                    <div class="detail-item"><span class="detail-label">Status</span><span class="detail-value"><span class="status-badge status-info">${c.status}</span></span></div>
                    <div class="detail-item"><span class="detail-label">Risk</span><span class="detail-value">${c.risk}</span></div>
                </div>
            `;
        }
    }).catch(() => { body.innerHTML = '<div style="color:#ef4444;text-align:center;">Failed to load case details.</div>'; });
}

function closeCaseModal() {
    const modal = document.getElementById('caseDetailModal');
    modal.style.opacity = '0';
    setTimeout(() => modal.style.display = 'none', 300);
}

// ══════════════════════════════════════
// Recovery Cases
// ══════════════════════════════════════

let recoveryFilterMode = 'all';

async function fetchRecoveryCases(filter = 'all') {
    recoveryFilterMode = filter;
    const tbody = document.getElementById('recoveryCasesBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:16px;"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';

    try {
        const url = filter === 'unassigned' ? '/recovery/cases?filter=unassigned' : '/recovery/cases';
        const res = await apiFetch(url);
        const data = await res.json();
        const cases = data.cases || [];

        const unassignedCount = cases.filter(c => c.advocate === 'Unassigned').length;
        const assignedCount = cases.length - unassignedCount;
        // Compute settlement pipeline: sum exposure of cases with OTS/Settlement strategy
        const settlementExp = cases
            .filter(c => c.strategy && (c.strategy.toLowerCase().includes('ots') || c.strategy.toLowerCase().includes('settlement')))
            .reduce((sum, c) => {
                const match = c.exposure ? c.exposure.replace(/[^0-9.]/g, '') : '0';
                return sum + parseFloat(match);
            }, 0);

        const totalEl = document.getElementById('rec-kpi-total');
        const unassEl = document.getElementById('rec-kpi-unassigned');
        const settlEl = document.getElementById('rec-kpi-settlement');
        if (totalEl) totalEl.textContent = cases.length + ' Cases';
        if (unassEl) unassEl.textContent = unassignedCount + ' Cases';
        if (settlEl) settlEl.textContent = `₹${settlementExp.toFixed(1)} Cr`;
        // Update proposal count sub-text dynamically
        const settlTrend = document.querySelector('#rec-kpi-settlement')?.closest('.kpi-card')?.querySelector('.kpi-trend');
        if (settlTrend) {
            const proposalCount = cases.filter(c => c.status === 'Proposal Sent' || (c.strategy && c.strategy.toLowerCase().includes('ots'))).length;
            settlTrend.innerHTML = `<i class="fas fa-minus"></i> ${proposalCount} Proposals`;
        }

        tbody.innerHTML = '';
        if (cases.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:#94a3b8;">No recovery cases found.</td></tr>';
            return;
        }

        cases.forEach(c => {
            let sc = 'status-info';
            if (['Notice Served', 'Property Attached', 'Admitted', 'Settled'].some(s => c.status.includes(s))) sc = 'status-success';
            if (['Pending', 'Unassigned', 'Pending Review'].some(s => c.status.includes(s))) sc = 'status-warning';

            const actionBtn = c.advocate === 'Unassigned'
                ? `<button class="btn btn-sm btn-primary" onclick="openAssignModal('${c.case_id}')"><i class="fas fa-user-plus"></i> Assign</button>`
                : `<button class="btn btn-sm btn-outline" onclick="openStatusModal('${c.case_id}')"><i class="fas fa-edit"></i> Update</button>`;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${c.case_id}</strong></td>
                <td>${c.borrower}</td>
                <td>${c.exposure}</td>
                <td>${c.strategy}</td>
                <td><span class="status-badge ${sc}">${c.status}</span></td>
                <td>${c.advocate === 'Unassigned' ? '<span style="color:#ef4444;">Unassigned</span>' : c.advocate}</td>
                <td>${actionBtn}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#ef4444;">Failed to load recovery cases.</td></tr>`;
    }
}

function filterRecovery(mode) {
    fetchRecoveryCases(mode);
}

// Assign Advocate Modal
function openAssignModal(caseId) {
    currentAssignCaseId = caseId;
    document.getElementById('assignCaseId').textContent = caseId;
    document.getElementById('advocateSelect').value = '';
    document.getElementById('customAdvocateGroup').style.display = 'none';
    document.getElementById('assignError').style.display = 'none';
    showModal('assignModal');
}

function handleAdvocateSelect() {
    const val = document.getElementById('advocateSelect').value;
    document.getElementById('customAdvocateGroup').style.display = val === '__custom__' ? 'block' : 'none';
}

async function confirmAssignAdvocate() {
    const sel = document.getElementById('advocateSelect').value;
    const custom = document.getElementById('customAdvocateInput').value.trim();
    const advocate = sel === '__custom__' ? custom : sel;

    if (!advocate) {
        showError('assignError', 'Please select or enter an advocate name.');
        return;
    }

    const btn = document.querySelector('#assignModal .btn-primary');
    if (btn) { btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Assigning...'; btn.disabled = true; }

    try {
        const res = await apiFetch('/recovery/assign', {
            method: 'POST',
            body: JSON.stringify({ case_id: currentAssignCaseId, advocate_name: advocate })
        });
        const data = await res.json();
        if (data.success) {
            closeAssignModal();
            fetchRecoveryCases(recoveryFilterMode);
            showToast(`Advocate '${advocate}' assigned to ${currentAssignCaseId || 'case'} successfully.`, 'success');
        } else {
            showError('assignError', data.message || 'Failed to assign.');
        }
    } catch (e) {
        showError('assignError', 'Server error. Please try again.');
    } finally {
        if (btn) { btn.innerHTML = '<i class="fas fa-check"></i> Assign'; btn.disabled = false; }
    }
}

function closeAssignModal() {
    closeModal('assignModal');
    currentAssignCaseId = null;
}

// Update Status Modal
function openStatusModal(caseId) {
    currentStatusCaseId = caseId;
    document.getElementById('statusCaseId').textContent = caseId;
    document.getElementById('statusError').style.display = 'none';
    showModal('statusModal');
}

async function confirmUpdateStatus() {
    const status = document.getElementById('statusSelect').value;
    const btn = document.querySelector('#statusModal .btn-primary');
    if (btn) { btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...'; btn.disabled = true; }

    try {
        const res = await apiFetch('/recovery/update-status', {
            method: 'POST',
            body: JSON.stringify({ case_id: currentStatusCaseId, status })
        });
        const data = await res.json();
        if (data.success) {
            closeStatusModal();
            fetchRecoveryCases(recoveryFilterMode);
            showToast(`Status updated to '${status}' successfully.`, 'success');
        } else {
            showError('statusError', data.message || 'Update failed.');
        }
    } catch (e) {
        showError('statusError', 'Server error. Please try again.');
    } finally {
        if (btn) { btn.innerHTML = '<i class="fas fa-save"></i> Update Status'; btn.disabled = false; }
    }
}

function closeStatusModal() {
    closeModal('statusModal');
    currentStatusCaseId = null;
}

// ══════════════════════════════════════
// Risk Scoring
// ══════════════════════════════════════

async function fetchRiskData() {
    const tbody = document.getElementById('highRiskCasesBody');
    if (!tbody) return;

    try {
        const [portRes, casesRes] = await Promise.all([
            apiFetch('/risk/portfolio'),
            apiFetch('/risk/high-risk')
        ]);

        if (portRes.ok) {
            const portData = await portRes.json();
            document.getElementById('kpi-high-risk').textContent = portData.kpis.high_risk_accounts;
            document.getElementById('kpi-ews').textContent = portData.kpis.ews_alerts;
            document.getElementById('kpi-avg-risk').textContent = portData.kpis.avg_portfolio_risk;

            const ctx = document.getElementById('detailedRiskChart');
            if (ctx) {
                if (detailedRiskChartInstance) detailedRiskChartInstance.destroy();
                detailedRiskChartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: portData.risk_matrix.categories,
                        datasets: [{
                            data: portData.risk_matrix.exposure_cr,
                            backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#991b1b'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        plugins: { legend: { position: 'right', labels: { color: '#475569' } } }
                    }
                });
            }
        }

        if (casesRes.ok) {
            const casesData = await casesRes.json();
            tbody.innerHTML = '';
            (casesData.cases || []).forEach(c => {
                const badgeClass = c.risk_score >= 90 ? 'status-warning' : 'status-info';
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${c.borrower}</strong></td>
                    <td>${c.exposure}</td>
                    <td><span class="status-badge ${badgeClass}">${c.risk_score}/100</span></td>
                    <td>${c.factor}</td>
                    <td>${c.recommendation}</td>
                    <td><button class="btn btn-sm btn-outline" onclick="openStatusModal('RISK-' + '${c.borrower}'.replace(/[^a-zA-Z]/g,'').substring(0,6))"><i class="fas fa-bolt"></i> Action</button></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error('Risk data error:', e);
        if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#ef4444;">Failed to load risk data.</td></tr>`;
    }
}

function initScoringForm() {
    const form = document.getElementById('scoringForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = form.querySelector('button[type="submit"]');
        const resultDiv = document.getElementById('scoreResult');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scoring...';
        btn.disabled = true;

        try {
            const res = await apiFetch('/risk/score', {
                method: 'POST',
                body: JSON.stringify({
                    case_id: document.getElementById('scoreCase').value,
                    borrower_name: document.getElementById('scoreBorrower').value,
                    exposure: parseFloat(document.getElementById('scoreExposure').value) * 100000,
                    dpd: parseInt(document.getElementById('scoreDPD').value),
                    sector: document.getElementById('scoreSector').value
                })
            });
            const data = await res.json();
            if (data.success) {
                const color = data.risk_label === 'Critical' ? '#ef4444' : data.risk_label === 'High' ? '#f59e0b' : '#10b981';
                resultDiv.innerHTML = `
                    <div style="margin-top:16px; padding:16px; background: var(--bg-secondary); border-radius:8px; border-left: 4px solid ${color};">
                        <div style="font-size:2rem; font-weight:700; color:${color};">${data.risk_score}<span style="font-size:1rem;">/100</span></div>
                        <div style="font-weight:600; color:${color};">${data.risk_label} Risk</div>
                        <div style="margin-top:8px; color:var(--text-secondary);">${data.recommendation}</div>
                    </div>
                `;
                resultDiv.classList.remove('hidden');
            }
        } catch (e) {
            alert('Scoring failed. Check backend.');
        } finally {
            btn.innerHTML = '<i class="fas fa-robot"></i> Calculate Risk Score';
            btn.disabled = false;
        }
    });
}

// ══════════════════════════════════════
// Legal Notices
// ══════════════════════════════════════

async function fetchNotices() {
    const tbody = document.getElementById('noticesTrackingBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:16px;"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';

    try {
        const res = await apiFetch('/notices/tracking');
        const data = await res.json();
        const notices = data.notices || [];

        document.getElementById('notice-kpi-drafted').textContent = notices.length;
        document.getElementById('notice-kpi-served').textContent = notices.filter(n => n.status.includes('Served')).length;
        document.getElementById('notice-kpi-deadline').textContent = notices.filter(n => n.status === 'Drafted').length;

        tbody.innerHTML = '';
        if (notices.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#94a3b8;">No notices yet. Generate one using the AI Notice Generator.</td></tr>';
            return;
        }
        notices.forEach(n => {
            let sc = 'status-info';
            if (n.status.includes('Served') || n.status.includes('Acknowledged')) sc = 'status-success';
            if (n.status.includes('Draft') || n.status.includes('Reply')) sc = 'status-warning';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${n.notice_id}</strong></td>
                <td>${n.borrower}</td>
                <td><span style="font-size:0.8rem;">${n.type.split('—').pop().trim() || n.type}</span></td>
                <td><span class="status-badge ${sc}">${n.status}</span></td>
                <td>${n.deadline}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="viewNoticeContent('${n.notice_id}')"><i class="fas fa-eye"></i> View</button>
                    <button class="btn btn-sm btn-outline" style="margin-left:4px;" onclick="updateNoticeStatus('${n.notice_id}', 'Dispatched')"><i class="fas fa-paper-plane"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#ef4444;">Failed to load notices.</td></tr>`;
    }
}

async function viewNoticeContent(noticeId) {
    showModal('draftModal');
    document.getElementById('draftContent').textContent = 'Loading...';
    document.getElementById('draftNoticeId').textContent = noticeId;
    currentDraftNoticeId = noticeId;

    try {
        const res = await apiFetch(`/notices/${noticeId}/content`);
        const data = await res.json();
        document.getElementById('draftContent').textContent = data.content || 'Content not found.';
    } catch (e) {
        document.getElementById('draftContent').textContent = 'Failed to load notice content.';
    }
}

async function updateNoticeStatus(noticeId, status) {
    try {
        const res = await apiFetch('/notices/update-status', {
            method: 'POST',
            body: JSON.stringify({ notice_id: noticeId, status })
        });
        const data = await res.json();
        if (data.success) fetchNotices();
    } catch (e) {
        console.error('Notice status update failed:', e);
    }
}

function initNoticeGenerator() {
    const form = document.getElementById('noticeGeneratorForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('generateNoticeBtn');
        const caseId = document.getElementById('noticeCaseId').value;
        const noticeType = document.getElementById('noticeType').value;

        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        btn.disabled = true;

        try {
            const res = await apiFetch('/notices/generate', {
                method: 'POST',
                body: JSON.stringify({ case_id: caseId, notice_type: noticeType })
            });
            const data = await res.json();
            if (data.success) {
                currentDraftNoticeId = data.notice_id;
                currentDraftDeadline = data.deadline;
                document.getElementById('draftContent').textContent = data.draft_content;
                document.getElementById('draftNoticeId').textContent = data.notice_id;
                document.getElementById('draftDeadline').textContent = data.deadline;
                showModal('draftModal');
                fetchNotices();
            } else {
                alert('Failed to generate notice.');
            }
        } catch (err) {
            alert('Failed to generate notice. Check backend connection.');
        } finally {
            btn.innerHTML = '<i class="fas fa-magic"></i> Generate Draft';
            btn.disabled = false;
        }
    });
}

async function approveAndDispatch() {
    if (!currentDraftNoticeId) { closeDraftModal(); return; }
    const btn = document.querySelector('#draftModal .modal-footer .btn-primary');
    if (btn) { btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Dispatching...'; btn.disabled = true; }
    try {
        await apiFetch('/notices/update-status', {
            method: 'POST',
            body: JSON.stringify({ notice_id: currentDraftNoticeId, status: 'Dispatched' })
        });
        closeDraftModal();
        fetchNotices();
        showToast(`Notice ${currentDraftNoticeId} approved and dispatched!`, 'success');
    } catch (e) {
        closeDraftModal();
        showToast('Failed to dispatch notice. Please try again.', 'error');
    }
}

function closeDraftModal() {
    closeModal('draftModal');
    currentDraftNoticeId = null;
}

// ══════════════════════════════════════
// Litigation
// ══════════════════════════════════════

async function fetchLitigationCases() {
    const tbody = document.getElementById('litigationCasesBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:16px;"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';

    try {
        const [casesRes, kpiRes] = await Promise.all([
            apiFetch('/litigation/cases'),
            apiFetch('/litigation/kpis')
        ]);

        if (kpiRes.ok) {
            const kpiData = await kpiRes.json();
            const k = kpiData.kpis;
            document.getElementById('lit-kpi-total').textContent = k.total_cases;
            document.getElementById('lit-kpi-exposure').textContent = '₹' + k.total_exposure_cr + ' Cr';
            document.getElementById('lit-kpi-hearings').textContent = k.upcoming_hearings;
            document.getElementById('lit-kpi-unassigned').textContent = k.unassigned_cases;
        }

        if (casesRes.ok) {
            const casesData = await casesRes.json();
            const cases = casesData.cases || [];
            tbody.innerHTML = '';
            if (cases.length === 0) {
                tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:20px;color:#94a3b8;">No litigation cases found.</td></tr>';
                return;
            }
            cases.forEach(c => {
                let sc = 'status-info';
                if (['Disposed', 'Settled'].some(s => c.status.includes(s))) sc = 'status-success';
                if (['Unassigned', 'Admission'].some(s => c.status.includes(s))) sc = 'status-warning';
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${c.case_id}</strong></td>
                    <td>${c.borrower}</td>
                    <td>${c.exposure}</td>
                    <td>${c.court}</td>
                    <td>${c.case_type}</td>
                    <td><span class="status-badge ${sc}">${c.status}</span></td>
                    <td>${c.next_hearing || 'TBD'}</td>
                    <td>${c.advocate === 'Unassigned' ? '<span style="color:#ef4444;">Unassigned</span>' : c.advocate}</td>
                    <td><button class="btn btn-sm btn-outline" onclick="openUpdateHearingModal('${c.case_id}')"><i class="fas fa-calendar"></i> Update</button></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;color:#ef4444;">Failed to load litigation data.</td></tr>`;
    }
}

function openUpdateHearingModal(caseId = '') {
    document.getElementById('hearingCaseId').value = caseId;
    const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById('hearingDate').value = tomorrow.toISOString().split('T')[0];
    showModal('hearingModal');
}

async function confirmUpdateHearing() {
    const caseId = document.getElementById('hearingCaseId').value.trim();
    const date = document.getElementById('hearingDate').value;
    const status = document.getElementById('hearingStatus').value;

    if (!caseId || !date) {
        showToast('Please fill in Case ID and Hearing Date.', 'warning');
        return;
    }

    const btn = document.querySelector('#hearingModal .btn-primary');
    if (btn) { btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...'; btn.disabled = true; }

    try {
        const res = await apiFetch('/litigation/update-hearing', {
            method: 'POST',
            body: JSON.stringify({ case_id: caseId, next_hearing: date, status })
        });
        const data = await res.json();
        if (data.success) {
            closeHearingModal();
            fetchLitigationCases();
            showToast(`Hearing for ${caseId} updated to ${date}`, 'success');
        } else {
            showToast('Failed to update hearing. Please try again.', 'error');
        }
    } catch (e) {
        showToast('Server error. Please try again.', 'error');
    } finally {
        if (btn) { btn.innerHTML = '<i class="fas fa-calendar-check"></i> Update'; btn.disabled = false; }
    }
}

function closeHearingModal() { closeModal('hearingModal'); }

// ══════════════════════════════════════
// Compliance
// ══════════════════════════════════════

async function fetchComplianceData() {
    const tbody = document.getElementById('complianceItemsBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:16px;"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';

    try {
        const [itemsRes, kpiRes, auditRes] = await Promise.all([
            apiFetch('/compliance/items'),
            apiFetch('/compliance/kpis'),
            apiFetch('/compliance/audit-log')
        ]);

        if (kpiRes.ok) {
            const kpiData = await kpiRes.json();
            const k = kpiData.kpis;
            document.getElementById('comp-kpi-score').textContent = k.compliance_score + '%';
            document.getElementById('comp-kpi-total').textContent = k.total_items;
            document.getElementById('comp-kpi-open').textContent = k.open_items;
            document.getElementById('comp-kpi-critical').textContent = k.critical_items;

            // Render compliance gauge chart
            const ctx = document.getElementById('complianceGaugeChart');
            if (ctx) {
                if (complianceChartInstance) complianceChartInstance.destroy();
                complianceChartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Compliant', 'Violations'],
                        datasets: [{
                            data: [k.compliance_score, 100 - k.compliance_score],
                            backgroundColor: ['#10b981', '#e2e8f0'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        cutout: '75%',
                        plugins: {
                            legend: { display: false },
                            tooltip: { enabled: true }
                        }
                    },
                    plugins: [{
                        id: 'centerText',
                        afterDraw(chart) {
                            const { ctx, chartArea } = chart;
                            const cx = (chartArea.left + chartArea.right) / 2;
                            const cy = (chartArea.top + chartArea.bottom) / 2;
                            ctx.save();
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.font = 'bold 28px Inter';
                            ctx.fillStyle = '#0f172a';
                            ctx.fillText(k.compliance_score + '%', cx, cy);
                            ctx.restore();
                        }
                    }]
                });
            }
        }

        if (auditRes.ok) {
            const auditData = await auditRes.json();
            const auditList = document.getElementById('auditLogList');
            if (auditList) {
                auditList.innerHTML = (auditData.audit_log || []).map(entry => `
                    <div class="audit-entry">
                        <div class="audit-time">${entry.timestamp}</div>
                        <div class="audit-action"><strong>${entry.officer}</strong> — ${entry.action}</div>
                        <div class="audit-case">${entry.case_id}</div>
                    </div>
                `).join('') || '<div class="text-muted" style="text-align:center;padding:20px;">No audit log entries.</div>';
            }
        }

        if (itemsRes.ok) {
            const itemsData = await itemsRes.json();
            const items = itemsData.items || [];
            tbody.innerHTML = '';
            if (items.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:#94a3b8;">No compliance items.</td></tr>';
                return;
            }
            items.forEach(item => {
                const sevColor = {
                    'Critical': 'status-warning',
                    'High': 'status-info',
                    'Medium': 'status-info',
                    'Low': 'status-success'
                }[item.severity] || 'status-info';
                const stColor = ['Open', 'Action Required'].includes(item.status) ? 'status-warning' : 'Compliant' === item.status ? 'status-success' : 'status-info';
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.violation_id}</strong></td>
                    <td>${item.regulation}</td>
                    <td>${item.description}</td>
                    <td><span class="status-badge ${sevColor}">${item.severity}</span></td>
                    <td><span class="status-badge ${stColor}">${item.status}</span></td>
                    <td>${item.due_date || 'N/A'}</td>
                    <td><button class="btn btn-sm btn-outline"><i class="fas fa-check"></i> Resolve</button></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error('Compliance error:', e);
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#ef4444;">Failed to load compliance data.</td></tr>`;
    }
}

// ══════════════════════════════════════
// Notifications
// ══════════════════════════════════════

async function fetchNotifications() {
    try {
        const res = await apiFetch('/notifications');
        const data = await res.json();
        const badge = document.getElementById('notifBadge');
        if (badge) badge.textContent = data.unread_count || 0;

        const list = document.getElementById('notifList');
        if (list) {
            const notifs = data.notifications || [];
            if (notifs.length === 0) {
                list.innerHTML = '<div class="notif-empty">No notifications.</div>';
            } else {
                list.innerHTML = notifs.map(n => `
                    <div class="notif-item ${n.is_read ? '' : 'unread'}" onclick="markNotifRead(${n.id})">
                        <div class="notif-icon ${n.type}"><i class="fas fa-${n.type === 'alert' ? 'exclamation-triangle' : n.type === 'success' ? 'check-circle' : 'info-circle'}"></i></div>
                        <div class="notif-content">
                            <div class="notif-title">${n.title}</div>
                            <div class="notif-msg">${n.message}</div>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (e) {
        console.error('Notifications error:', e);
    }
}

function toggleNotifPanel() {
    const panel = document.getElementById('notifPanel');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) fetchNotifications();
}

async function markNotifRead(id) {
    try {
        await apiFetch('/notifications/mark-read', {
            method: 'POST',
            body: JSON.stringify({ notification_id: id })
        });
        fetchNotifications();
    } catch (e) {}
}

async function markAllRead() {
    const res = await apiFetch('/notifications');
    const data = await res.json();
    const notifs = data.notifications || [];
    await Promise.all(notifs.filter(n => !n.is_read).map(n =>
        apiFetch('/notifications/mark-read', { method: 'POST', body: JSON.stringify({ notification_id: n.id }) })
    ));
    fetchNotifications();
}

// ══════════════════════════════════════
// Export / Report
// ══════════════════════════════════════

async function exportReport() {
    showModal('exportModal');
    document.getElementById('exportReportBody').innerHTML = '<div style="text-align:center;padding:30px;"><i class="fas fa-spinner fa-spin"></i> Generating report...</div>';

    try {
        const res = await apiFetch('/export/summary');
        const data = await res.json();
        currentExportData = data;
        const k = data.kpis;

        document.getElementById('exportReportBody').innerHTML = `
            <div class="export-report">
                <div class="export-section">
                    <h4>Portfolio Overview</h4>
                    <div class="detail-grid">
                        <div class="detail-item"><span class="detail-label">Total NPA Exposure</span><span class="detail-value">₹${k.total_exposure_cr} Cr</span></div>
                        <div class="detail-item"><span class="detail-label">Active Litigation</span><span class="detail-value">${k.active_litigation_cases} Cases</span></div>
                        <div class="detail-item"><span class="detail-label">Compliance Score</span><span class="detail-value">${k.compliance_score_percent}%</span></div>
                        <div class="detail-item"><span class="detail-label">AI Predicted Recovery</span><span class="detail-value">₹${k.predicted_recovery_cr} Cr</span></div>
                    </div>
                </div>
                <div class="export-section">
                    <h4>Recovery Summary</h4>
                    <div class="detail-grid">
                        <div class="detail-item"><span class="detail-label">Total Recovery Cases</span><span class="detail-value">${data.recovery_summary.total_cases}</span></div>
                        <div class="detail-item"><span class="detail-label">Unassigned</span><span class="detail-value">${data.recovery_summary.unassigned}</span></div>
                    </div>
                </div>
                <div class="export-section">
                    <h4>Litigation Summary</h4>
                    <div class="detail-grid">
                        <div class="detail-item"><span class="detail-label">Total Litigation Cases</span><span class="detail-value">${data.litigation_summary.total_cases}</span></div>
                        <div class="detail-item"><span class="detail-label">Upcoming Hearings</span><span class="detail-value">${data.litigation_summary.upcoming_hearings}</span></div>
                    </div>
                </div>
                <div class="export-section">
                    <h4>Compliance Summary</h4>
                    <div class="detail-grid">
                        <div class="detail-item"><span class="detail-label">Open Violations</span><span class="detail-value">${data.compliance_summary.open_items}</span></div>
                        <div class="detail-item"><span class="detail-label">Critical Items</span><span class="detail-value">${data.compliance_summary.critical_items}</span></div>
                    </div>
                </div>
                <div style="margin-top:16px; color:var(--text-muted); font-size:0.8rem;">Generated: ${data.generated_at} · By: ${data.generated_by}</div>
            </div>
        `;
    } catch (e) {
        document.getElementById('exportReportBody').innerHTML = '<div style="color:#ef4444;text-align:center;">Failed to generate report.</div>';
    }
}

function downloadReport() {
    if (!currentExportData) return;
    const blob = new Blob([JSON.stringify(currentExportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `judiq_report_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function closeExportModal() { closeModal('exportModal'); }

// ══════════════════════════════════════
// Settings
// ══════════════════════════════════════

async function loadSystemInfo() {
    const body = document.getElementById('sysInfoBody');
    if (!body) return;

    const labelMap = {
        version: { label: 'Platform Version', icon: 'tag' },
        backend: { label: 'Backend Stack', icon: 'server' },
        frontend: { label: 'Frontend Stack', icon: 'code' },
        ai_engine: { label: 'AI Engine', icon: 'robot' },
        uptime: { label: 'Server Status', icon: 'heartbeat' },
        last_db_backup: { label: 'Last DB Backup', icon: 'database' },
        api_base_url: { label: 'API Endpoint', icon: 'plug' }
    };

    try {
        const res = await apiFetch('/settings/system-info');
        const data = await res.json();
        const s = data.system;
        body.innerHTML = Object.entries(s).map(([k, v]) => {
            const meta = labelMap[k] || { label: k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()), icon: 'info-circle' };
            const isOnline = v === 'Online';
            const valHtml = isOnline
                ? `<span style="color:#10b981;font-weight:600;"><i class="fas fa-circle" style="font-size:0.6rem;margin-right:4px;"></i>${v}</span>`
                : `<span style="font-weight:500;">${v}</span>`;
            return `
            <div class="sys-info-row">
                <div class="sys-info-icon"><i class="fas fa-${meta.icon}"></i></div>
                <div class="sys-info-content">
                    <div class="sys-info-label">${meta.label}</div>
                    <div class="sys-info-value">${valHtml}</div>
                </div>
            </div>`;
        }).join('');
    } catch (e) {
        body.innerHTML = '<div class="text-muted" style="text-align:center;padding:20px;"><i class="fas fa-plug" style="margin-bottom:8px;display:block;"></i>Backend offline. Start the server to see info.</div>';
    }
}

async function checkApiHealth() {
    const dot = document.getElementById('apiStatusDot');
    const text = document.getElementById('apiStatusText');
    if (!dot || !text) return;

    try {
        const res = await fetch('http://127.0.0.1:8000/health');
        if (res.ok) {
            dot.className = 'status-dot online';
            text.textContent = 'Backend online · JudiQ v12.5.0';
            text.style.color = '#10b981';
        } else {
            throw new Error('Non-200');
        }
    } catch {
        dot.className = 'status-dot offline';
        text.textContent = 'Backend offline — start uvicorn on port 8000';
        text.style.color = '#ef4444';
    }
}

function initProfileForm() {
    const form = document.getElementById('profileForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = form.querySelector('button[type="submit"]');
        const msgEl = document.getElementById('profileMsg');
        const name = document.getElementById('profileName').value.trim();
        const currentPwd = document.getElementById('profileCurrentPwd').value;
        const newPwd = document.getElementById('profileNewPwd').value;

        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        btn.disabled = true;
        msgEl.style.display = 'none';

        try {
            const res = await apiFetch('/settings/update-profile', {
                method: 'POST',
                body: JSON.stringify({ name, current_password: currentPwd || null, new_password: newPwd || null })
            });
            const data = await res.json();
            if (data.success) {
                msgEl.style.display = 'none';
                showToast('Profile updated successfully!', 'success');
                if (name && currentUser) {
                    currentUser.name = name;
                    localStorage.setItem('judiq_user', JSON.stringify(currentUser));
                    updateUserProfile();
                }
            } else {
                msgEl.textContent = data.detail || 'Update failed.';
                msgEl.style.color = '#ef4444';
                msgEl.style.display = 'block';
            }
        } catch (e) {
            msgEl.textContent = 'Server error. Please try again.';
            msgEl.style.color = '#ef4444';
            msgEl.style.display = 'block';
        } finally {
            btn.innerHTML = '<i class="fas fa-save"></i> Update Profile';
            btn.disabled = false;
        }
    });
}

function savePreferences() {
    const prefs = {
        emailNotif: document.getElementById('prefEmailNotif').checked,
        autoRefresh: document.getElementById('prefAutoRefresh').checked,
        aiCopilot: document.getElementById('prefAiCopilot').checked
    };
    localStorage.setItem('judiq_prefs', JSON.stringify(prefs));
    showToast('Preferences saved successfully!', 'success');

    // Apply auto-refresh if enabled
    if (prefs.autoRefresh) {
        window._autoRefreshInterval = setInterval(() => fetchDashboardData(), 300000);
    } else {
        clearInterval(window._autoRefreshInterval);
    }
}

// ══════════════════════════════════════
// Modal Helpers
// ══════════════════════════════════════

function showModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.display = 'flex';
    setTimeout(() => el.style.opacity = '1', 10);
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.opacity = '0';
    setTimeout(() => el.style.display = 'none', 300);
}

// Close modals on overlay click
document.addEventListener('click', (e) => {
    ['draftModal', 'caseDetailModal', 'assignModal', 'statusModal', 'exportModal', 'hearingModal'].forEach(id => {
        const modal = document.getElementById(id);
        if (modal && e.target === modal) closeModal(id);
    });
    // Close notif panel
    const panel = document.getElementById('notifPanel');
    const bell = document.getElementById('notifBellBtn');
    if (panel && !panel.contains(e.target) && bell && !bell.contains(e.target)) {
        panel.classList.add('hidden');
    }
});

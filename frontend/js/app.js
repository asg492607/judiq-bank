// JudiQ Bank Edition - Core Application Logic

let authToken = localStorage.getItem('judiq_token');

document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    if (authToken) {
        showDashboard();
    }
});

// Authentication Logic
function initAuth() {
    const loginForm = document.getElementById('loginForm');
    const authScreen = document.getElementById('authScreen');
    const errorMsg = document.getElementById('loginError');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('http://127.0.0.1:8000/api/v1/bank/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.success && data.access_token) {
                    authToken = data.access_token;
                    localStorage.setItem('judiq_token', authToken);
                    authScreen.style.opacity = '0';
                    setTimeout(() => {
                        authScreen.style.display = 'none';
                        showDashboard();
                    }, 500);
                } else {
                    errorMsg.style.display = 'block';
                    errorMsg.textContent = data.message || "Invalid credentials";
                }
            } catch (error) {
                console.error("Login failed:", error);
                errorMsg.style.display = 'block';
                errorMsg.textContent = "Server connection failed. Make sure backend is running on port 8000.";
            }
        });
    }

    const regForm = document.getElementById('registerForm');
    const regError = document.getElementById('regError');
    if (regForm) {
        regForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('regName').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            
            try {
                const response = await fetch('http://127.0.0.1:8000/api/v1/bank/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });
                
                const data = await response.json();
                if (data.success) {
                    alert("Registration successful! Please login.");
                    toggleAuth('login');
                } else {
                    regError.style.display = 'block';
                    regError.textContent = data.message || "Registration failed";
                }
            } catch (error) {
                console.error("Reg failed:", error);
                regError.style.display = 'block';
                regError.textContent = "Server connection failed.";
            }
        });
    }
}

function toggleAuth(mode) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const subtitle = document.getElementById('authSubtitle');
    
    if (mode === 'register') {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        subtitle.textContent = "Create Officer Account";
    } else {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        subtitle.textContent = "Secure Officer Login";
    }
}

function showDashboard() {
    const authScreen = document.getElementById('authScreen');
    const appContainer = document.getElementById('appContainer');
    
    if (authScreen) authScreen.style.display = 'none';
    if (appContainer) appContainer.style.display = 'flex';
    
    initNavigation();
    initCharts();
    fetchDashboardData();
    initCaseIntake();
    fetchRecoveryCases();
    fetchRiskData();
    fetchNotices();
    initNoticeGenerator();
}

// Handle Sidebar Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const viewPanes = document.querySelectorAll('.view-pane');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            const targetViewId = 'view-' + item.getAttribute('data-view');
            
            viewPanes.forEach(pane => {
                pane.classList.remove('active');
                pane.classList.add('hidden');
            });
            
            const targetView = document.getElementById(targetViewId);
            if (targetView) {
                targetView.classList.remove('hidden');
                targetView.classList.add('active');
            }
        });
    });
}

let recoveryChartInstance = null;
let riskChartInstance = null;

// Initialize Empty Charts
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

// Fetch Real Data from Backend (API Integration)
async function fetchDashboardData() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/bank/dashboard', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (!response.ok) throw new Error("API call failed");
        
        const data = await response.json();
        
        // Update KPIs
        if (data.kpis) {
            document.getElementById('kpi-exposure').textContent = '₹' + data.kpis.total_exposure_cr.toLocaleString() + ' Cr';
            document.getElementById('kpi-cases').textContent = data.kpis.active_litigation_cases.toLocaleString();
            document.getElementById('kpi-score').textContent = data.kpis.compliance_score_percent + '%';
            document.getElementById('kpi-predicted').textContent = '₹' + data.kpis.predicted_recovery_cr.toLocaleString() + ' Cr';
        }
        
        // Update Recovery Chart
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
        
        // Update Risk Chart
        if (riskChartInstance && data.risk_heatmap) {
            riskChartInstance.data.labels = data.risk_heatmap.categories;
            riskChartInstance.data.datasets = [{
                label: 'Number of Cases',
                data: data.risk_heatmap.case_counts,
                backgroundColor: [
                    '#ef4444', '#f59e0b', 
                    'rgba(239, 68, 68, 0.8)', 'rgba(245, 158, 11, 0.6)', 
                    '#10b981'
                ],
                borderWidth: 0, borderRadius: 4
            }];
            riskChartInstance.update();
        }
        
        console.log("Dashboard updated with live data.");
    } catch (error) {
        console.error("Error fetching dashboard data:", error);
        if (error.message.includes('401')) {
            localStorage.removeItem('judiq_token');
            location.reload();
        }
    }
}

// Case Intake Module Logic
function initCaseIntake() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    
    if (!uploadZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('dragover'), false);
    });

    uploadZone.addEventListener('drop', (e) => {
        handleFiles(e.dataTransfer.files);
    });
    
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    fetchRecentCases();
}

function handleFiles(files) {
    if (files.length > 0) {
        simulateUploadAndOCR(files[0]);
    }
}

function simulateUploadAndOCR(file) {
    const progressDiv = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const percentText = document.getElementById('uploadPercent');
    const filenameText = document.getElementById('uploadFilename');
    
    filenameText.textContent = `Processing ${file.name}...`;
    progressDiv.classList.remove('hidden');
    progressFill.style.width = '0%';
    percentText.textContent = '0%';
    
    let progress = 0;
    const interval = setInterval(async () => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('http://127.0.0.1:8000/api/v1/bank/cases/upload', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${authToken}` },
                    body: formData
                });
                
                if(response.ok) {
                    setTimeout(() => {
                        progressDiv.classList.add('hidden');
                        alert("Case processed successfully by JudiQ OCR Engine!");
                        fetchRecentCases();
                    }, 500);
                }
            } catch(e) {
                console.error("Upload error", e);
                progressDiv.classList.add('hidden');
            }
        }
        progressFill.style.width = progress + '%';
        percentText.textContent = Math.round(progress) + '%';
    }, 300);
}

async function fetchRecentCases() {
    const tbody = document.getElementById('recentCasesBody');
    if (!tbody) return;
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/bank/cases/recent', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (!response.ok) throw new Error("Failed to fetch cases");
        const data = await response.json();
        
        tbody.innerHTML = '';
        data.cases.forEach(c => {
            let statusClass = 'status-info';
            if (c.status.includes('Completed')) statusClass = 'status-success';
            if (c.status.includes('Duplicate')) statusClass = 'status-warning';
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${c.case_id}</strong></td>
                <td>${c.borrower}</td>
                <td>${c.exposure}</td>
                <td><span class="status-badge ${statusClass}">${c.status}</span></td>
                <td><button class="btn btn-sm btn-outline">View Details</button></td>
            `;
            tbody.appendChild(tr);
        });
} catch(e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#ef4444;">Failed to load cases.</td></tr>`;
    }
}

// Module 4: Recovery Case Management Logic
async function fetchRecoveryCases() {
    const tbody = document.getElementById('recoveryCasesBody');
    if (!tbody) return;
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/bank/recovery/cases', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (!response.ok) throw new Error("Failed to fetch recovery cases");
        const data = await response.json();
        
        tbody.innerHTML = '';
        data.cases.forEach(c => {
            let statusClass = 'status-info';
            if (c.status.includes('Completed') || c.status.includes('Scheduled')) statusClass = 'status-success';
            if (c.status.includes('Pending') || c.status.includes('Unassigned')) statusClass = 'status-warning';
            
            const actionBtn = c.advocate === 'Unassigned' 
                ? `<button class="btn btn-sm btn-primary" onclick="assignAdvocate('${c.case_id}')">Assign Advocate</button>`
                : `<button class="btn btn-sm btn-outline">Update Status</button>`;
                
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${c.case_id}</strong></td>
                <td>${c.borrower}</td>
                <td>${c.exposure}</td>
                <td>${c.strategy}</td>
                <td><span class="status-badge ${statusClass}">${c.status}</span></td>
                <td>${c.advocate}</td>
                <td>${actionBtn}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch(e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#ef4444;">Failed to load recovery cases.</td></tr>`;
    }
}

async function assignAdvocate(caseId) {
    const advocateName = prompt("Enter Advocate Name to assign:");
    if (!advocateName) return;
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/bank/recovery/assign', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ case_id: caseId, advocate_name: advocateName })
        });
        const data = await response.json();
        if (data.success) {
            alert(data.message);
            fetchRecoveryCases(); // Refresh table
        }
    } catch (e) {
        console.error(e);
        alert("Failed to assign advocate.");
    }
}

// Module 12: AI Risk Scoring Engine Logic
let detailedRiskChartInstance = null;

async function fetchRiskData() {
    const tbody = document.getElementById('highRiskCasesBody');
    if (!tbody) return;
    
    try {
        // Fetch Portfolio KPIs & Matrix
        const portRes = await fetch('http://127.0.0.1:8000/api/v1/bank/risk/portfolio', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (portRes.ok) {
            const portData = await portRes.json();
            document.getElementById('kpi-high-risk').textContent = portData.kpis.high_risk_accounts;
            document.getElementById('kpi-ews').textContent = portData.kpis.ews_alerts;
            document.getElementById('kpi-avg-risk').textContent = portData.kpis.avg_portfolio_risk;
            
            // Render Detailed Risk Matrix Chart
            const ctxMatrix = document.getElementById('detailedRiskChart');
            if (ctxMatrix) {
                if (detailedRiskChartInstance) detailedRiskChartInstance.destroy();
                detailedRiskChartInstance = new Chart(ctxMatrix, {
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
        
        // Fetch High Risk Cases
        const casesRes = await fetch('http://127.0.0.1:8000/api/v1/bank/risk/high-risk', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (casesRes.ok) {
            const casesData = await casesRes.json();
            tbody.innerHTML = '';
            casesData.cases.forEach(c => {
                let badgeClass = c.risk_score > 90 ? 'status-warning' : 'status-info'; // using warning for red/orange in this context
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${c.borrower}</strong></td>
                    <td>${c.exposure}</td>
                    <td><span class="status-badge ${badgeClass}">${c.risk_score}/100</span></td>
                    <td>${c.factor}</td>
                    <td>${c.recommendation}</td>
                    <td><button class="btn btn-sm btn-outline">Take Action</button></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch(e) {
        console.error("Failed to fetch risk data:", e);
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#ef4444;">Failed to load risk data.</td></tr>`;
    }
}

// Module 3: Legal Notice Intelligence Logic
async function fetchNotices() {
    const tbody = document.getElementById('noticesTrackingBody');
    if (!tbody) return;
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/bank/notices/tracking', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const data = await response.json();
            tbody.innerHTML = '';
            data.notices.forEach(n => {
                let badgeClass = 'status-info';
                if (n.status.includes('Served')) badgeClass = 'status-success';
                if (n.status.includes('Drafting')) badgeClass = 'status-warning';
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${n.notice_id}</strong></td>
                    <td>${n.borrower}</td>
                    <td>${n.type}</td>
                    <td><span class="status-badge ${badgeClass}">${n.status}</span></td>
                    <td>${n.deadline}</td>
                    <td><button class="btn btn-sm btn-outline"><i class="fas fa-eye"></i> View</button></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch(e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#ef4444;">Failed to load notices.</td></tr>`;
    }
}

function initNoticeGenerator() {
    const form = document.getElementById('noticeGeneratorForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const caseId = document.getElementById('noticeCaseId').value;
        const noticeType = document.getElementById('noticeType').value;
        const btn = form.querySelector('button');
        
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        btn.disabled = true;
        
        try {
            const response = await fetch('http://127.0.0.1:8000/api/v1/bank/notices/generate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({ case_id: caseId, notice_type: noticeType })
            });
            const data = await response.json();
            if (data.success) {
                document.getElementById('draftContent').textContent = data.draft_content;
                document.getElementById('draftModal').style.display = 'flex';
                setTimeout(() => document.getElementById('draftModal').style.opacity = '1', 10);
            }
        } catch(err) {
            alert("Failed to generate notice.");
        } finally {
            btn.innerHTML = '<i class="fas fa-magic"></i> Generate Draft';
            btn.disabled = false;
        }
    });
}

function closeDraftModal() {
    document.getElementById('draftModal').style.opacity = '0';
    setTimeout(() => document.getElementById('draftModal').style.display = 'none', 300);
}

import sys

app_js_path = r"c:\Users\Atharva\OneDrive\Desktop\judiq-bank\frontend\js\app.js"

with open(app_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace fetchRecentCases
old_fetch = """async function fetchRecentCases() {
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
}"""

new_fetch = """let currentCasesPage = 0;
const casesPerPage = 50;

async function fetchRecentCases(page = 0) {
    currentCasesPage = page;
    const tbody = document.getElementById('recentCasesBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:16px;"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';

    try {
        const offset = page * casesPerPage;
        const res = await apiFetch(`/cases/recent?limit=${casesPerPage}&offset=${offset}`);
        const data = await res.json();
        tbody.innerHTML = '';

        if (!data.cases || data.cases.length === 0) {
            if (page === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#94a3b8;">No cases yet. Upload a document to begin.</td></tr>';
            } else {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:20px;color:#94a3b8;">No more cases found.</td></tr>';
            }
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
        
        updatePaginationControls('casesPagination', page, data.cases.length === casesPerPage);
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#ef4444;">Failed to load cases. Is the backend running?</td></tr>`;
    }
}

function updatePaginationControls(containerId, page, hasMore) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = `
        <button class="btn btn-sm btn-outline" onclick="fetchRecentCases(${page - 1})" ${page === 0 ? 'disabled' : ''}>Previous</button>
        <span style="padding: 0 10px; font-size: 0.9rem;">Page ${page + 1}</span>
        <button class="btn btn-sm btn-outline" onclick="fetchRecentCases(${page + 1})" ${!hasMore ? 'disabled' : ''}>Next</button>
    `;
}"""

content = content.replace(old_fetch, new_fetch)

feedback_code = """
// ══════════════════════════════════════
// Feedback
// ══════════════════════════════════════
function initFeedbackForm() {
    const form = document.getElementById('feedbackForm');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('feedbackSubmitBtn');
        const type = document.getElementById('feedbackType').value;
        const message = document.getElementById('feedbackMessage').value;

        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        btn.disabled = true;

        try {
            const res = await apiFetch('/feedback', {
                method: 'POST',
                body: JSON.stringify({ type, message })
            });
            const data = await res.json();
            if (data.success) {
                showToast(data.message, 'success');
                document.getElementById('feedbackModal').style.display = 'none';
                form.reset();
            } else {
                showToast(data.detail || 'Failed to submit feedback', 'error');
            }
        } catch (err) {
            showToast('Server error during feedback submission.', 'error');
        } finally {
            btn.innerHTML = 'Submit';
            btn.disabled = false;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initFeedbackForm();
});
"""

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(content + "\n" + feedback_code)

print("Patched app.js successfully!")

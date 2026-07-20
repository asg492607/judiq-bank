import { wizardSteps } from './config.js?v=8';
import { ui, switchScreen } from './ui.js?v=8';
import { api } from './api.js?v=8';
import { renderResults } from './renderer.js?v=8';

let isWizardInitialized = false;

function persistAutosave() {
    localStorage.setItem('judiq_wizard_autosave', JSON.stringify({
        step: window.state.currentStep,
        data: window.state.caseData
    }));
}

function loadAutosave() {
    const saved = localStorage.getItem('judiq_wizard_autosave');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            if (parsed.data) window.state.caseData = { ...window.state.caseData, ...parsed.data };
            if (parsed.step) window.state.currentStep = parsed.step;
        } catch(e) {}
    }
}

// Add enter-to-proceed functionality
document.addEventListener('keydown', (e) => {
    const wizardContainer = document.getElementById('wizardStepsContainer');
    // Only trigger if wizard is visible
    if (wizardContainer && wizardContainer.offsetParent !== null) {
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'BUTTON') {
            e.preventDefault();
            if (window.state.currentStep < window.wizardStepsLength) {
                window.nextStep();
            } else {
                window.submitCase();
            }
        }
    }
});

export function renderWizardStep() {
    const stepIdx = window.state.currentStep - 1;
    const step = wizardSteps[stepIdx];
    
    ui.setText('wizardTitle', step.title);
    ui.setText('wizardSubtitle', step.subtitle);
    ui.setText('stepBadgeNumber', window.state.currentStep);
    ui.setText('totalBadgeNumber', wizardSteps.length);
    ui.setText('currentStepDisplay', window.state.currentStep);
    ui.setText('totalStepsDisplay', wizardSteps.length);
    
    const container = document.getElementById('wizardStepsContainer');
    if (!container) return;
    
    if (!isWizardInitialized) {
        loadAutosave();
        // Update step index based on loaded autosave
        const loadedStepIdx = window.state.currentStep - 1;
        window.wizardStepsLength = wizardSteps.length;
        container.innerHTML = wizardSteps.map((s, idx) => `
            <form id="stepForm_${idx}" class="step-form fade-in ${idx === 0 ? '' : 'hidden'}" onsubmit="event.preventDefault(); nextStep();">
                ${s.fields.map(field => renderField(field)).join('')}
            </form>
        `).join('');
        isWizardInitialized = true;
    } else {
        wizardSteps.forEach((s, idx) => {
            const form = document.getElementById(`stepForm_${idx}`);
            if (form) {
                if (idx === window.state.currentStep - 1) {
                    form.classList.remove('hidden');
                } else {
                    form.classList.add('hidden');
                }
            }
            s.fields.forEach(field => {
                const el = document.getElementById(field.name);
                if (el) {
                    el.value = window.state.caseData[field.name] || '';
                }
            });
        });
    }
    
    updateProgress();
    updateNavigationButtons();
    updateConditionalFields();
}

function updateConditionalFields() {
    // Helper to toggle visibility and required attribute
    const toggleField = (fieldId, isVisible) => {
        const el = document.getElementById(fieldId);
        if (!el) return;
        const group = el.closest('.form-group');
        if (group) {
            group.style.display = isVisible ? 'block' : 'none';
        }
        if (isVisible) {
            el.setAttribute('required', 'required');
            el.required = true;
            el.disabled = false;
        } else {
            el.removeAttribute('required');
            el.required = false;
            el.disabled = true;
        }
    };

    // Complainant Type -> Authorized Representative
    const compTypeEl = document.getElementById('complainant_type');
    if (compTypeEl) {
        const isEntity = compTypeEl.value !== 'Individual' && compTypeEl.value !== '';
        toggleField('complainant_authorized', isEntity);
    }

    // Accused Type -> Directors Named
    const accTypeEl = document.getElementById('accused_type');
    if (accTypeEl) {
        const isEntity = accTypeEl.value !== 'Individual' && accTypeEl.value !== '';
        toggleField('directors_named', isEntity);
    }
}

function renderField(field) {
    const value = window.state.caseData[field.name] || '';
    let inputHtml = '';
    
    if (field.type === 'select') {
        inputHtml = `
            <select id="${field.name}" name="${field.name}" ${field.required ? 'required' : ''} onchange="if(typeof updateConditionalFields === 'function') updateConditionalFields()">
                <option value="">Select Option</option>
                ${field.options.map(opt => `<option value="${opt}" ${value === opt ? 'selected' : ''}>${opt}</option>`).join('')}
            </select>
        `;
    } else if (field.type === 'textarea') {
        inputHtml = `<textarea id="${field.name}" name="${field.name}" ${field.required ? 'required' : ''} placeholder="${field.placeholder || ''}" onchange="if(typeof updateConditionalFields === 'function') updateConditionalFields()">${value}</textarea>`;
    } else {
        inputHtml = `<input type="${field.type}" id="${field.name}" name="${field.name}" value="${value}" ${field.required ? 'required' : ''} placeholder="${field.placeholder || ''}" onchange="if(typeof updateConditionalFields === 'function') updateConditionalFields()">`;
    }
    
    return `
        <div class="form-group">
            <label for="${field.name}">${field.label} ${field.required ? '<span class="required">*</span>' : ''}</label>
            ${inputHtml}
        </div>
    `;
}

function updateProgress() {
    const progress = (window.state.currentStep / wizardSteps.length) * 100;
    const fill = document.getElementById('progressFill');
    if (fill) fill.style.width = `${progress}%`;
    ui.setText('progressPercentage', `${Math.round(progress)}%`);
}

// Update wizard navigation buttons state
function updateNavigationButtons() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    if (prevBtn) prevBtn.disabled = window.state.currentStep === 1;
    
    if (window.state.currentStep === wizardSteps.length) {
        if (nextBtn) nextBtn.classList.add('hidden');
        if (submitBtn) submitBtn.classList.remove('hidden');
    } else {
        if (nextBtn) nextBtn.classList.remove('hidden');
        if (submitBtn) submitBtn.classList.add('hidden');
    }
}

window.nextStep = () => {
    const stepIdx = window.state.currentStep - 1;
    const form = document.getElementById(`stepForm_${stepIdx}`);
    if (form && !form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Save data
    const step = wizardSteps[stepIdx];
    step.fields.forEach(field => {
        const el = document.getElementById(field.name);
        if (el) window.state.caseData[field.name] = el.value;
    });

    // Auto-selection logic: if Agreement Type is "Invoice/Bill", select "receipts_invoices"
    if (step.id === 'transaction') {
        if (window.state.caseData['agreement_type'] === 'Invoice/Bill') {
            window.state.caseData['receipts_invoices'] = 'Yes';
        }
    }
    
    if (window.state.currentStep < wizardSteps.length) {
        window.state.currentStep++;
        persistAutosave();
        renderWizardStep();
    }
};

window.previousStep = () => {
    if (window.state.currentStep > 1) {
        window.state.currentStep--;
        persistAutosave();
        renderWizardStep();
    }
};

/**
 * Sanitizes wizard payload before sending to API.
 * Converts string Yes/No fields to actual booleans for boolean-typed fields
 * so the backend normalizer receives clean data.
 */
function sanitizePayload(rawData) {
    const BOOLEAN_FIELDS = [
        'notice_sent', 'cheque_present', 'dishonour_memo', 'debt_proven',
        'directors_named', 'complainant_authorized', 'itr_available',
        'bank_memo_received', 'second_presentation', 'post_dated',
        'signature_dispute', 'debt_denial', 'cheque_security_claim',
        'within_30_days', 'reply_received', 'memo_signed', 'court_attendance'
    ];
    const TRUTHY_VALUES = ['yes', 'true', '1', 'yes - all', 'yes - partial',
        'yes - original', 'yes - copy', 'yes - written', 'yes - verbal',
        'yes - acknowledged', 'yes - denied', 'yes - full payment',
        'yes - denial', 'yes - partial response', 'yes - being sent', 'in progress', 'yes - signed', 'yes - regular'];

    const cleaned = { ...rawData };
    for (const field of BOOLEAN_FIELDS) {
        if (field in cleaned) {
            const val = String(cleaned[field] || '').trim().toLowerCase();
            cleaned[field] = TRUTHY_VALUES.some(t => val.startsWith(t) || val === t);
        }
    }
    return cleaned;
}

function saveCurrentStepValues() {
    const stepIdx = window.state.currentStep - 1;
    const step = wizardSteps[stepIdx];
    if (!step) return;
    step.fields.forEach(field => {
        const el = document.getElementById(field.name);
        if (el) window.state.caseData[field.name] = el.value;
    });
}

window.submitCase = async () => {
    const stepIdx = window.state.currentStep - 1;
    const form = document.getElementById(`stepForm_${stepIdx}`);
    if (form && !form.checkValidity()) {
        form.reportValidity();
        return;
    }
    saveCurrentStepValues();
    ui.show('analysisLoading');
    try {
        const userId = window.state.currentUser ? window.state.currentUser.uid : 'ANONYMOUS';
        const rawPayload = { ...window.state.caseData, user_id: userId };
        const payload = sanitizePayload(rawPayload);
        const result = await api.analyze(payload);
        window.state.analysisResult = result;
        if (window.saveCaseToHistory) {
            window.saveCaseToHistory(payload, result);
        }
        // Clear autosave after successful submission
        localStorage.removeItem('judiq_wizard_autosave');
        ui.hide('analysisLoading');
        switchScreen('resultsScreen');
        renderResults(result);
    } catch (err) {
        ui.hide('analysisLoading');
        ui.toast(err.message, 'error');
    }
};



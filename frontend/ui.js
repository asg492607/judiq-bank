/**
 * UI Utility Module
 */
export const ui = {
    show(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove('hidden');
    },
    
    hide(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    },
    
    toggle(id, condition) {
        if (condition) this.show(id);
        else this.hide(id);
    },
    
    setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    },
    
    setHTML(id, html) {
        const el = document.getElementById(id);
        if (el) el.innerHTML = html;
    },
    
    toast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';
        
        toast.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <div class="toast-content">${message}</div>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }
};

/**
 * Screen switching logic
 */
export function switchScreen(targetScreenId) {
    const screens = [
        'landingScreen', 'loginScreen', 'registerScreen', 
        'roleScreen', 'dashboardScreen', 'caseWizardScreen', 
        'resultsScreen', 'termsScreen', 'privacyScreen', 'refundScreen',
        'draftGeneratorScreen'
    ];
    
    screens.forEach(id => ui.hide(id));
    ui.show(targetScreenId);
    
    // Reset scroll
    window.scrollTo(0, 0);

    // First-time visit guided tour check
    if (targetScreenId === 'dashboardScreen') {
        const tourCompleted = localStorage.getItem('judiq_tour_completed') === 'true';
        if (!tourCompleted && typeof window.startGuidedTour === 'function') {
            setTimeout(() => {
                window.startGuidedTour();
            }, 800);
        }
    }
}

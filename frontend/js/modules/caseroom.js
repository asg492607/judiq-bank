import { escapeHtml } from './utils.js?v=8';
import { JudiQState } from './state.js?v=8';
import { ui } from '../../ui.js?v=8';
import { API_BASE_URL } from '../../config.js?v=8';

// =============================================================================
// JUDIQ — COLLABORATIVE CASEROOM ENGINE
// =============================================================================
// Reads all runtime state from JudiQState and JudiQConfig.
// No raw globals; no ES6 imports/exports.
// =============================================================================

    // -------------------------------------------------------------------------
    // CONFIG HELPERS — safe reads from JudiQConfig / JudiQState
    // -------------------------------------------------------------------------
    function cfg(key, fallback) {
        if (key === 'API_BASE_URL') return API_BASE_URL;
        return fallback;
    }

    function state(key, fallback) {
        return (JudiQState && JudiQState[key] !== undefined)
            ? JudiQState[key]
            : fallback;
    }

    function getApiBase() {
        return cfg('API_BASE_URL', 'http://127.0.0.1:8000');
    }

    function getWsBase() {
        return cfg('WS_BASE_URL',
            (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
                ? 'ws://127.0.0.1:8000'
                : 'wss://cheque-bounce-ragbased.onrender.com'
        );
    }

    function getMaxRetries() {
        return cfg('MAX_WS_RETRIES', 5);
    }

    function getMaxQueueSize() {
        return cfg('MAX_QUEUE_SIZE', 50);
    }

    function getCurrentUserId() {
        return state('currentUser', null)?.uid
            || (window.currentUser && window.currentUser.uid)
            || 'LEAD_ADVOCATE';
    }

    function getCaseData() {
        return state('caseData', null) || window.caseData || null;
    }

    // -------------------------------------------------------------------------
    // TOAST / LOADING HELPERS — delegate to UI layer if available
    // -------------------------------------------------------------------------
    function toast(msg, type) {
        if (ui && ui.toast) ui.toast(msg, type);
        else console[type === 'error' ? 'error' : 'log']('[JudiQ Caseroom]', msg);
    }

    function showLoading(msg) {
        if (window.showAnalysisLoading) window.showAnalysisLoading(msg);
    }

    function hideLoading() {
        if (window.hideAnalysisLoading) window.hideAnalysisLoading();
    }

    // -------------------------------------------------------------------------
    // SAFE HTML HELPER — always sanitize before touching the DOM
    // -------------------------------------------------------------------------
    function safeHtml(html) {
        if (JudiQ_UI && typeof JudiQ_UI.setHTML === 'function') {
            // Return a document fragment via JudiQ_UI.sanitize if provided
            if (typeof JudiQ_UI.sanitize === 'function') {
                return JudiQ_UI.sanitize(html);
            }
        }
        if (window.DOMPurify) return window.DOMPurify.sanitize(html);
        // Last-resort: strip tags entirely
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }

    function setHTML(element, html) {
        if (!element) return;
        if (JudiQ_UI && typeof JudiQ_UI.setHTML === 'function') {
            JudiQ_UI.setHTML(element, html);
        } else {
            element.innerHTML = safeHtml(html);
        }
    }

    function escHtml(str) {
        if (typeof str !== 'string') str = String(str || '');
        if (escapeHtml) return escapeHtml(str);
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // -------------------------------------------------------------------------
    // MODULE STATE
    // -------------------------------------------------------------------------
    var currentCaseroomId = null;
    var caseroomWs = null;
    var wsReconnectAttempts = 0;
    var wsKeepAliveInterval = null;
    var CASE_ROOM_QUEUE_PREFIX = 'judiq_caseroom_queue_';

    // -------------------------------------------------------------------------
    // OFFLINE QUEUE
    // -------------------------------------------------------------------------
    function getQueueKey() {
        return CASE_ROOM_QUEUE_PREFIX + (currentCaseroomId || 'unknown');
    }

    function readQueue() {
        try {
            return JSON.parse(localStorage.getItem(getQueueKey()) || '[]');
        } catch (_) {
            return [];
        }
    }

    function writeQueue(items) {
        try {
            var maxSize = getMaxQueueSize();
            if (items.length > maxSize) {
                items = items.slice(-maxSize);
                toast('Local queue full — older offline tasks were discarded.', 'warning');
            }
            localStorage.setItem(getQueueKey(), JSON.stringify(items));
        } catch (_) {}
    }

    function queueAction(type, payload) {
        var queue = readQueue();
        queue.push({ type: type, payload: payload, ts: Date.now() });
        writeQueue(queue);
    }

    async function flushQueue() {
        var queue = readQueue();
        if (!queue.length || !currentCaseroomId) return;

        var remaining = [];
        for (var i = 0; i < queue.length; i++) {
            var item = queue[i];
            try {
                var url = '';
                if (item.type === 'message') {
                    url = getApiBase() + '/api/v1/caseroom/' + currentCaseroomId + '/message';
                } else if (item.type === 'task') {
                    url = getApiBase() + '/api/v1/caseroom/' + currentCaseroomId + '/task';
                } else {
                    continue; // Unknown type — drop it
                }

                var response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(item.payload)
                });
                var result = await response.json();
                if (!result.success) {
                    remaining.push(item);
                }
            } catch (_) {
                remaining.push(item);
            }
        }
        writeQueue(remaining);

        if (remaining.length === 0 && queue.length > 0) {
            toast('Offline queue flushed — all queued actions synced.', 'success');
        }
    }

    // -------------------------------------------------------------------------
    // KEEP-ALIVE PING
    // -------------------------------------------------------------------------
    function startKeepAlive() {
        stopKeepAlive();
        wsKeepAliveInterval = setInterval(function () {
            if (caseroomWs && caseroomWs.readyState === WebSocket.OPEN) {
                try {
                    caseroomWs.send(JSON.stringify({ type: 'PING', ts: Date.now() }));
                } catch (_) {}
            }
        }, 25000);
    }

    function stopKeepAlive() {
        if (wsKeepAliveInterval) {
            clearInterval(wsKeepAliveInterval);
            wsKeepAliveInterval = null;
        }
    }

    // -------------------------------------------------------------------------
    // OFFLINE BANNER
    // -------------------------------------------------------------------------
    function showOfflineBanner() {
        var caseroomContainer = document.querySelector('.caseroom-chat-area');
        if (!caseroomContainer) {
            toast('Live chat connection lost. Switched to HTTP mode.', 'error');
            return;
        }
        var offlineBanner = document.getElementById('caseroomOfflineBanner');
        if (!offlineBanner) {
            offlineBanner = document.createElement('div');
            offlineBanner.id = 'caseroomOfflineBanner';
            offlineBanner.style.cssText = [
                'background-color:#fef2f2',
                'color:#991b1b',
                'padding:10px',
                'text-align:center',
                'font-size:0.9rem',
                'font-weight:500',
                'border-bottom:1px solid #fecaca'
            ].join(';');
            setHTML(offlineBanner, '<i class="fas fa-wifi" style="text-decoration:line-through;"></i> OFFLINE MODE: Live sync disconnected. Messages will be sent via standard HTTP.');
            caseroomContainer.insertBefore(offlineBanner, caseroomContainer.firstChild);
        }
    }

    function removeOfflineBanner() {
        var banner = document.getElementById('caseroomOfflineBanner');
        if (banner && banner.parentNode) banner.parentNode.removeChild(banner);
    }

    // -------------------------------------------------------------------------
    // WEBSOCKET RECONNECTION
    // -------------------------------------------------------------------------
    function scheduleReconnect() {
        var maxRetries = getMaxRetries();
        if (wsReconnectAttempts < maxRetries) {
            var delay = Math.min(1000 * Math.pow(2, wsReconnectAttempts), 30000);
            console.warn(
                '[JudiQ Caseroom] WS disconnected. Reconnecting in ' +
                (delay / 1000) + 's… (Attempt ' + (wsReconnectAttempts + 1) + '/' + maxRetries + ')'
            );
            wsReconnectAttempts++;
            setTimeout(startCaseroomSync, delay);
        } else {
            console.error('[JudiQ Caseroom] WS failed to reconnect after maximum attempts.');
            showOfflineBanner();
        }
    }

    // -------------------------------------------------------------------------
    // INIT CASEROOM
    // -------------------------------------------------------------------------
    async function initCaseroom() {
        var caseData = getCaseData();
        if (!caseData || !caseData.case_id) {
            toast('Please analyze a case first.', 'warning');
            return;
        }

        var caseId = caseData.case_id;
        var userId = getCurrentUserId();

        try {
            showLoading('Initializing Secure Caseroom…');
            var response = await fetch(getApiBase() + '/api/v1/caseroom/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ case_id: caseId, user_id: userId })
            });
            var result = await response.json();
            if (result.success) {
                currentCaseroomId = result.caseroom_id;
                toast('Caseroom Created Successfully!', 'success');
                startCaseroomSync();
            } else {
                toast(result.message || 'Failed to create caseroom.', 'error');
            }
        } catch (error) {
            console.error('[JudiQ Caseroom] Init Error:', error);
            toast('Network error while creating caseroom.', 'error');
        } finally {
            hideLoading();
        }
    }

    // -------------------------------------------------------------------------
    // START CASEROOM SYNC (WebSocket + initial data fetch)
    // -------------------------------------------------------------------------
    function startCaseroomSync() {
        if (!currentCaseroomId) {
            console.warn('[JudiQ Caseroom] startCaseroomSync called without a caseroom ID.');
            return;
        }

        // Close any existing socket cleanly
        if (caseroomWs) {
            try { caseroomWs.close(); } catch (_) {}
            caseroomWs = null;
        }

        refreshCaseroom();

        var wsUrl = getWsBase() + '/api/v1/caseroom/ws/' + currentCaseroomId;

        try {
            caseroomWs = new WebSocket(wsUrl);
        } catch (e) {
            console.error('[JudiQ Caseroom] Could not create WebSocket:', e);
            scheduleReconnect();
            return;
        }

        caseroomWs.onopen = function () {
            
            wsReconnectAttempts = 0;
            removeOfflineBanner();
            startKeepAlive();
            flushQueue()
                .then(function () { return refreshCaseroom(); })
                .catch(function (err) { console.error(err); });
        };

        caseroomWs.onmessage = function (event) {
            try {
                var data = JSON.parse(event.data);
                if (data.type === 'PONG') return;
                if (data.type === 'NEW_MESSAGE' || data.type === 'REFRESH') {
                    refreshCaseroom();
                }
            } catch (_) {}
        };

        caseroomWs.onerror = function (error) {
            console.error('[JudiQ Caseroom] WS Error:', error);
        };

        caseroomWs.onclose = function () {
            stopKeepAlive();
            scheduleReconnect();
        };
    }

    // -------------------------------------------------------------------------
    // REFRESH CASEROOM DATA (HTTP poll / manual refresh)
    // -------------------------------------------------------------------------
    async function refreshCaseroom() {
        if (!currentCaseroomId) return;
        try {
            var response = await fetch(getApiBase() + '/api/v1/caseroom/' + currentCaseroomId);
            var result = await response.json();
            if (result.success) {
                renderCaseroom(result.data);
            } else {
                console.warn('[JudiQ Caseroom] Refresh returned failure:', result);
            }
        } catch (error) {
            console.error('[JudiQ Caseroom] Sync Error:', error);
        }
    }

    // -------------------------------------------------------------------------
    // RENDER CASEROOM DATA INTO THE DOM
    // -------------------------------------------------------------------------
    function renderCaseroom(data) {
        if (!data) return;

        var chatBox = document.getElementById('caseroomChat');
        var chatControls = document.getElementById('chatControls');
        var participantsEl = document.getElementById('crParticipants');
        var caseIdEl = document.getElementById('crCaseId');
        var timelineEl = document.getElementById('caseroomTimeline');

        // --- Case ID label ---
        if (caseIdEl && data.room_info) {
            caseIdEl.textContent = data.room_info[2] || '';
        }

        // --- Show chat controls ---
        if (chatControls) chatControls.classList.remove('hidden');

        // --- Participants ---
        if (participantsEl && Array.isArray(data.participants)) {
            var participantHtml = data.participants.map(function (p) {
                var safeId = escHtml(p.user_id || '');
                var safeRole = escHtml(p.role || '');
                var initial = safeId.charAt(0).toUpperCase() || '?';
                return '<div class="participant-avatar" title="' + safeId + ' (' + safeRole + ')">' + initial + '</div>';
            }).join('');
            setHTML(participantsEl, participantHtml);
        }

        // --- Messages (incremental append) ---
        if (chatBox && Array.isArray(data.messages) && data.messages.length > 0) {
            var prevCount = parseInt(chatBox.dataset.msgCount || '0', 10);
            var newCount = data.messages.length;

            if (newCount > prevCount) {
                var userId = getCurrentUserId();
                var newMessages = data.messages.slice(prevCount);
                var newChatHtml = newMessages.map(function (m) {
                    var isMe = m.user_id === userId;
                    var type = m.user_id === 'SYSTEM' ? 'system' : (isMe ? 'user' : 'other');
                    var safeUser = escHtml(m.user_id || '');
                    var safeContent = escHtml(m.content || '');
                    var timeStr = m.timestamp ? new Date(m.timestamp).toLocaleTimeString() : '';
                    return (
                        '<div class="chat-bubble ' + type + '">' +
                            '<strong>' + safeUser + ':</strong> ' + safeContent +
                            '<div style="font-size:8px;opacity:0.6;text-align:right;">' + timeStr + '</div>' +
                        '</div>'
                    );
                }).join('');

                var fragment = document.createElement('div');
                fragment.innerHTML = safeHtml(newChatHtml);
                while (fragment.firstChild) {
                    chatBox.appendChild(fragment.firstChild);
                }
                chatBox.scrollTop = chatBox.scrollHeight;
                chatBox.dataset.msgCount = String(newCount);
            }
        }

        // --- Tasks / Milestones ---
        if (timelineEl) {
            if (Array.isArray(data.tasks) && data.tasks.length > 0) {
                var prevTaskCount = parseInt(timelineEl.dataset.taskCount || '-1', 10);
                if (prevTaskCount !== data.tasks.length) {
                    var timelineHtml = data.tasks.map(function (t) {
                        var safeTitle = escHtml(t.title || '');
                        var safeStatus = escHtml(t.status || '');
                        var safeDate = escHtml(t.due_date || '');
                        return (
                            '<div class="timeline-milestone">' +
                                '<div style="font-weight:600;font-size:13px;">' + safeTitle + '</div>' +
                                '<div style="font-size:11px;color:var(--gray-500);">' + safeDate + ' | ' + safeStatus + '</div>' +
                            '</div>'
                        );
                    }).join('');
                    setHTML(timelineEl, timelineHtml);
                    timelineEl.dataset.taskCount = String(data.tasks.length);
                }
            } else {
                var emptyHtml = '<div class="evidence-empty">No milestones added.</div>';
                if (timelineEl.dataset.taskCount !== '0') {
                    setHTML(timelineEl, emptyHtml);
                    timelineEl.dataset.taskCount = '0';
                }
            }
        }
    }

    // -------------------------------------------------------------------------
    // SEND MESSAGE
    // -------------------------------------------------------------------------
    async function sendMessage() {
        var input = document.getElementById('chatInput');
        if (!input) return;

        var btn = input.nextElementSibling;
        var text = input.value.trim();
        if (!text || !currentCaseroomId) return;

        var payload = { user_id: getCurrentUserId(), content: text };

        try {
            input.disabled = true;
            if (btn) btn.disabled = true;

            if (!navigator.onLine) {
                queueAction('message', payload);
                input.value = '';
                toast('Offline: message queued and will sync automatically.', 'warning');
                return;
            }

            var response = await fetch(
                getApiBase() + '/api/v1/caseroom/' + currentCaseroomId + '/message',
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }
            );
            var result = await response.json();
            if (result.success) {
                input.value = '';
                refreshCaseroom();
            } else {
                toast(result.message || 'Failed to send message.', 'error');
            }
        } catch (error) {
            console.error('[JudiQ Caseroom] Message Send Error:', error);
            queueAction('message', payload);
            input.value = '';
            toast('Connection lost: message queued for sync.', 'warning');
        } finally {
            input.disabled = false;
            if (btn) btn.disabled = false;
            input.focus();
        }
    }

    // -------------------------------------------------------------------------
    // ADD TASK / MILESTONE
    // -------------------------------------------------------------------------
    async function addTask() {
        var title = prompt('Enter Milestone Title:');
        if (!title || !title.trim() || !currentCaseroomId) return;

        var date = new Date().toISOString().split('T')[0];
        var payload = { title: title.trim(), due_date: date, description: 'Added from Caseroom' };

        if (!navigator.onLine) {
            queueAction('task', payload);
            toast('Offline: milestone queued and will sync automatically.', 'warning');
            return;
        }

        try {
            showLoading('Adding Milestone…');
            var response = await fetch(
                getApiBase() + '/api/v1/caseroom/' + currentCaseroomId + '/task',
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }
            );
            var result = await response.json();
            if (result.success) {
                toast('Milestone Added', 'success');
                refreshCaseroom();
            } else {
                toast(result.message || 'Failed to add milestone.', 'error');
            }
        } catch (error) {
            console.error('[JudiQ Caseroom] Task Add Error:', error);
            queueAction('task', payload);
            toast('Network error: milestone queued for sync.', 'warning');
        } finally {
            hideLoading();
        }
    }

    // -------------------------------------------------------------------------
    // ONLINE EVENT — flush queue on reconnect
    // -------------------------------------------------------------------------
    window.addEventListener('online', function () {
        if (currentCaseroomId) {
            flushQueue()
                .then(function () { return refreshCaseroom(); })
                .catch(function (err) { console.error(err); });
        }
    });

    // -------------------------------------------------------------------------
    // PUBLIC API — attach to window
    // -------------------------------------------------------------------------
    export { initCaseroom };
    export { startCaseroomSync };
    export { refreshCaseroom };
    export { renderCaseroom };
    export { sendMessage };
    export { addTask };

    // Also expose queue helpers for debugging / external use
    export const JudiQCaseroom = {
        initCaseroom: initCaseroom,
        startCaseroomSync: startCaseroomSync,
        refreshCaseroom: refreshCaseroom,
        renderCaseroom: renderCaseroom,
        sendMessage: sendMessage,
        addTask: addTask,
        readQueue: readQueue,
        writeQueue: writeQueue,
        queueAction: queueAction,
        flushQueue: flushQueue,
        startKeepAlive: startKeepAlive,
        stopKeepAlive: stopKeepAlive,
        getState: function () {
            return {
                currentCaseroomId: currentCaseroomId,
                wsReconnectAttempts: wsReconnectAttempts,
                wsState: caseroomWs ? caseroomWs.readyState : null
            };
        }
    };

    






// ==============================================================================
// SINCRONIZZAZIONE REAL-TIME BIDIREZIONALE (WEBSOCKET / SERVER LOCALE)
// ==============================================================================

const CLIENT_ID = 'client_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now().toString(36);
let syncSocket = null;
let syncReconnectTimer = null;
let isApplyingRemoteState = false;

function getServerBaseUrl() {
    // 1. Priorità a eventuale injection da Android WebView
    if (window.ANDROID_SERVER_URL) {
        return window.ANDROID_SERVER_URL;
    }
    if (window.Android && typeof window.Android.getServerUrl === 'function') {
        const url = window.Android.getServerUrl();
        if (url) return url;
    }

    // 2. Se siamo già serviti via HTTP/HTTPS da server locale
    if (window.location.protocol.startsWith('http')) {
        return window.location.origin;
    }

    // 3. Fallback salvato in localStorage per modalità file:///
    const savedUrl = localStorage.getItem('FANTA_SYNC_SERVER_URL');
    if (savedUrl) return savedUrl;

    return null;
}

function getWebSocketUrl(baseUrl) {
    if (!baseUrl) return null;
    const url = new URL(baseUrl.startsWith('http') ? baseUrl : 'http://' + baseUrl);
    const wsProto = url.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProto}//${url.host}/ws`;
}

function updateSyncBadge(status, details) {
    const badge = document.getElementById('liveSyncStatus');
    const text = document.getElementById('syncText');
    if (!badge || !text) return;

    badge.className = 'sync-badge ' + status;
    if (status === 'connected') {
        const count = details || 1;
        text.textContent = count > 1 ? `Live (${count} conn.)` : `Live (1 conn.)`;
        badge.title = `Connesso al server Live. Dispositivi sincronizzati: ${count}. Clicca per impostazioni.`;
    } else if (status === 'connecting') {
        text.textContent = 'Connessione...';
        badge.title = 'Tentativo di connessione al server...';
    } else {
        text.textContent = 'Offline';
        badge.title = 'Modalità Offline autonoma. Clicca per connettere al PC su Wi-Fi.';
    }
}

function initLiveSync() {
    if (syncReconnectTimer) {
        clearTimeout(syncReconnectTimer);
        syncReconnectTimer = null;
    }

    const baseUrl = getServerBaseUrl();
    if (!baseUrl) {
        updateSyncBadge('offline');
        return;
    }

    const wsUrl = getWebSocketUrl(baseUrl);
    if (!wsUrl) {
        updateSyncBadge('offline');
        return;
    }

    updateSyncBadge('connecting');

    try {
        syncSocket = new WebSocket(wsUrl);

        syncSocket.onopen = () => {
            console.log("-> [LiveSync] Connessione WebSocket stabilita con successo.");
            updateSyncBadge('connected', 1);
            // Richiedi lo stato attuale salvato sul server
            syncSocket.send(JSON.stringify({ type: 'GET_STATE', client_id: CLIENT_ID }));
        };

        syncSocket.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);
                handleSyncMessage(payload);
            } catch (err) {
                console.warn("[LiveSync] Errore parsing messaggio:", err);
            }
        };

        syncSocket.onclose = () => {
            updateSyncBadge('offline');
            // Tentativo automatico di riconnessione ogni 4 secondi
            syncReconnectTimer = setTimeout(initLiveSync, 4000);
        };

        syncSocket.onerror = () => {
            updateSyncBadge('offline');
        };

    } catch (e) {
        console.warn("[LiveSync] Impossibile aprire WebSocket:", e);
        updateSyncBadge('offline');
        syncReconnectTimer = setTimeout(initLiveSync, 4000);
    }
}

function handleSyncMessage(payload) {
    if (!payload || !payload.type) return;

    if (payload.type === 'PEERS_COUNT') {
        updateSyncBadge('connected', payload.count);
    } else if (payload.type === 'INIT_STATE' || payload.type === 'STATE_UPDATE') {
        if (payload.source === CLIENT_ID) return; // Ignora eco locale

        const remote = payload.state;
        if (!remote || Object.keys(remote).length === 0) return;

        console.log("-> [LiveSync] Ricevuto aggiornamento di stato remoto. Applicazione in corso...");
        isApplyingRemoteState = true;

        try {
            const currentActiveId = (typeof LeaguesManager !== 'undefined' && typeof LeaguesManager.getActiveId === 'function') 
                ? LeaguesManager.getActiveId() 
                : (State.activeLeagueId || 'league_default');
            
            const remoteLeagueId = remote.leagueId || currentActiveId;

            // Se il payload appartiene a una lega DIVERSA da quella attualmente attiva:
            if (remote.leagueId && remote.leagueId !== currentActiveId) {
                if (typeof LeaguesManager !== 'undefined' && typeof LeaguesManager.getAll === 'function') {
                    const leagues = LeaguesManager.getAll();
                    const targetIdx = leagues.findIndex(l => l.id === remote.leagueId);
                    if (targetIdx !== -1) {
                        if (remote.leagueName) leagues[targetIdx].name = remote.leagueName;
                        if (remote.teamName) leagues[targetIdx].myTeamName = remote.teamName;
                        if (remote.systemMode) leagues[targetIdx].systemMode = remote.systemMode;
                        if (remote.budgetTotal !== undefined) leagues[targetIdx].budgetTotal = Number(remote.budgetTotal);
                        if (remote.budgetSpent !== undefined) leagues[targetIdx].budgetSpent = Number(remote.budgetSpent);
                        if (remote.slots) leagues[targetIdx].slots = JSON.parse(JSON.stringify(remote.slots));
                        if (remote.rules) leagues[targetIdx].rules = JSON.parse(JSON.stringify(remote.rules));
                        if (remote.favorites) leagues[targetIdx].favorites = JSON.parse(JSON.stringify(remote.favorites));
                        if (remote.takenByOthers) leagues[targetIdx].takenByOthers = JSON.parse(JSON.stringify(remote.takenByOthers));
                        if (remote.rivalAssignments) leagues[targetIdx].rivalAssignments = JSON.parse(JSON.stringify(remote.rivalAssignments));
                        if (remote.rivals) leagues[targetIdx].rivals = JSON.parse(JSON.stringify(remote.rivals));
                        if (remote.playerOverrides) leagues[targetIdx].playerOverrides = JSON.parse(JSON.stringify(remote.playerOverrides));
                        leagues[targetIdx].updatedAt = new Date().toISOString();
                        LeaguesManager.saveAll(leagues);
                        if (State.activeTab === 'home' && typeof renderHomeHubView === 'function') {
                            renderHomeHubView();
                        }
                    }
                }
                return; // Non sovrascrivere lo State della lega attualmente attiva!
            }

            // Se il payload appartiene alla lega attiva:
            if (remote.budgetTotal !== undefined) State.budgetTotal = Number(remote.budgetTotal);
            if (remote.budgetSpent !== undefined) State.budgetSpent = Number(remote.budgetSpent);
            if (remote.slots) State.slots = JSON.parse(JSON.stringify(remote.slots));
            if (remote.rules) State.rules = JSON.parse(JSON.stringify(remote.rules));
            if (remote.favorites) State.favorites = JSON.parse(JSON.stringify(remote.favorites));
            if (remote.takenByOthers) State.takenByOthers = JSON.parse(JSON.stringify(remote.takenByOthers));
            if (remote.rivalAssignments) State.rivalAssignments = JSON.parse(JSON.stringify(remote.rivalAssignments));
            if (remote.rivals) State.rivals = JSON.parse(JSON.stringify(remote.rivals));
            if (remote.playerOverrides) State.playerOverrides = JSON.parse(JSON.stringify(remote.playerOverrides));
            if (remote.systemMode && remote.systemMode !== State.systemMode && typeof setSystemMode === 'function') {
                setSystemMode(remote.systemMode, false);
            }

            // Salva nella collezione leghe
            if (typeof LeaguesManager !== 'undefined' && typeof LeaguesManager.saveCurrentStateToActiveLeague === 'function') {
                LeaguesManager.saveCurrentStateToActiveLeague();
            }

            // Salva su localStorage legacy per compatibilità
            const toSave = {
                leagueId: State.activeLeagueId,
                leagueName: State.leagueName,
                teamName: State.teamName,
                systemMode: State.systemMode,
                budgetTotal: State.budgetTotal,
                budgetSpent: State.budgetSpent,
                slots: State.slots,
                rules: State.rules,
                favorites: State.favorites,
                takenByOthers: State.takenByOthers,
                rivalAssignments: State.rivalAssignments,
                rivals: State.rivals,
                playerOverrides: State.playerOverrides
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));

            if (typeof applyPlayerOverrides === 'function') {
                applyPlayerOverrides();
            }
            if (typeof updateAllViews === 'function') {
                updateAllViews();
            }

            // Notifica visiva discreta
            showSyncToast("⚡ Dati sincronizzati in tempo reale");
        } finally {
            isApplyingRemoteState = false;
        }
    }
}

function broadcastStateUpdate(toSave) {
    if (isApplyingRemoteState) return; // Evita loop infiniti
    if (!syncSocket || syncSocket.readyState !== WebSocket.OPEN) return;

    try {
        const payloadToSend = {
            ...toSave,
            leagueId: toSave.leagueId || (typeof State !== 'undefined' ? State.activeLeagueId : 'league_default')
        };
        syncSocket.send(JSON.stringify({
            type: 'STATE_UPDATE',
            state: payloadToSend,
            source: CLIENT_ID
        }));
    } catch (e) {
        console.warn("[LiveSync] Errore invio aggiornamento stato:", e);
    }
}

function promptServerConnection() {
    const current = getServerBaseUrl() || 'http://192.168.1.xxx:8000';
    const input = prompt("Inserisci l'indirizzo IP del PC su cui è attivo il Server Live (es. http://192.168.1.15:8000):", current);
    if (input !== null) {
        let cleaned = input.trim();
        if (cleaned && !cleaned.startsWith('http')) {
            cleaned = 'http://' + cleaned;
        }
        if (cleaned) {
            localStorage.setItem('FANTA_SYNC_SERVER_URL', cleaned);
            if (window.Android && typeof window.Android.setServerUrl === 'function') {
                window.Android.setServerUrl(cleaned);
            }
            alert("Indirizzo impostato: " + cleaned + "\nRiconnessione in corso...");
            initLiveSync();
        } else {
            localStorage.removeItem('FANTA_SYNC_SERVER_URL');
            if (syncSocket) syncSocket.close();
            updateSyncBadge('offline');
        }
    }
}

function showSyncToast(msg) {
    let toast = document.getElementById('syncToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'syncToast';
        toast.className = 'sync-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('visible');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
        toast.classList.remove('visible');
    }, 2200);
}

// Avvio automatico al caricamento della pagina
window.addEventListener('DOMContentLoaded', () => {
    initLiveSync();
});

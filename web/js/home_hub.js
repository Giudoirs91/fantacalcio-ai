// ==============================================================================
// HOME AI HUB — INTERACTION & QUICK SEARCH LOGIC
// ==============================================================================

function filterHubPlayers(query) {
    const resEl = document.getElementById('hubSearchResults');
    if (!resEl) return;
    
    if (!query || query.trim().length < 2) {
        resEl.style.display = 'none';
        resEl.innerHTML = '';
        return;
    }
    const q = query.toLowerCase().trim();
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS)) return;
    
    const matches = PLAYERS.filter(p => {
        const n = (p.name || '').toLowerCase();
        const t = (p.team || '').toLowerCase();
        return n.includes(q) || t.includes(q);
    }).slice(0, 6);

    if (matches.length === 0) {
        resEl.innerHTML = `<div style="padding:16px;color:var(--text-muted);text-align:center;font-size:12.5px;">Nessun calciatore trovato per "<b>${query}</b>"</div>`;
        resEl.style.display = 'block';
        return;
    }

    resEl.innerHTML = matches.map(p => `
        <div class="hub-search-result-item" onclick="selectHubPlayer(${p.id})">
            <div style="display:flex;align-items:center;gap:10px;">
                <span class="role-badge ${p.role}">${p.role}</span>
                <div>
                    <div style="font-weight:800;color:#fff;font-size:13.5px;">${p.name}</div>
                    <div style="font-size:11.5px;color:var(--text-secondary);">${p.team} • ${p.role_desc || p.role}</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;">
                <span class="ovr-pill ${typeof getOvrClass === 'function' ? getOvrClass(p.ovr) : ''}">OVR ${p.ovr || '-'}</span>
                <span style="font-size:12.5px;font-weight:900;color:#fbbf24;font-family:'Outfit',sans-serif;">${p.fvm || p.price_prop || '-'} CR</span>
                <span style="color:var(--accent-cyan);font-size:11.5px;font-weight:800;background:rgba(56,189,248,0.1);padding:3px 8px;border-radius:6px;border:1px solid rgba(56,189,248,0.25);">Scheda &rarr;</span>
            </div>
        </div>
    `).join('');
    resEl.style.display = 'block';
}

function selectHubPlayer(playerId) {
    const resEl = document.getElementById('hubSearchResults');
    const inputEl = document.getElementById('hubQuickSearch');
    if (resEl) resEl.style.display = 'none';
    if (inputEl) inputEl.value = '';
    if (typeof openPlayerProfileModal === 'function') {
        openPlayerProfileModal(playerId);
    }
}

function openPlayerByName(name) {
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS)) return;
    const nClean = name.toLowerCase().trim();
    const p = PLAYERS.find(pl => (pl.name || '').toLowerCase().includes(nClean));
    if (p && typeof openPlayerProfileModal === 'function') {
        openPlayerProfileModal(p.id);
    } else {
        // Fallback: switch to auction and search
        if (typeof switchTab === 'function') {
            switchTab('auction');
            const searchInput = document.getElementById('searchBar');
            if (searchInput) {
                searchInput.value = name;
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    }
}

// Chiudi dropdown al click esterno
document.addEventListener('click', (e) => {
    const searchContainer = document.querySelector('.ai-hub-search-wrap');
    const resEl = document.getElementById('hubSearchResults');
    if (searchContainer && resEl && !searchContainer.contains(e.target)) {
        resEl.style.display = 'none';
    }
});

// ==============================================================================
// FANTA MASTER AI — MODERN SPA APPLICATION CONTROLLER
// ==============================================================================

// Stato globale dell'applicazione
const state = {
  activeTab: 'lineup',
  lineupMode: 'squad', // 'squad' o 'clubs'
  activeClub: 'Inter',
  tacticalTeamsList: [],
  mySquad: [], // Lista di ID o oggetti giocatore
  supportedModules: ['3-4-3', '4-3-3', '3-5-2', '4-4-2', '4-2-3-1', '5-3-2'],
  selectedModule: 'auto',
  playersPage: 1,
  playersPageSize: 25,
  playersSortBy: 'fvm',
  playersOrder: 'desc',
  playersRoleFilter: '',
  playersSearchQuery: '',
  gkPairs: [],
  selectedPlayer: null
};

// Inizializzazione al caricamento del DOM
document.addEventListener('DOMContentLoaded', async () => {
  setupNavigation();
  setupEventListeners();
  setupModeSwitcher();
  registerServiceWorker();
  
  // Carica i moduli supportati
  try {
    const modRes = await window.api.getSupportedModules();
    if (modRes && modRes.modules) {
      state.supportedModules = modRes.modules;
      populateModuleSelect(modRes.modules);
    }
  } catch(e) {
    console.warn("Uso moduli di default", e);
  }

  // Carica i 20 club di Serie A
  await loadTacticalTeamsList();

  // Carica prima pagina giocatori e rosa iniziale
  await loadInitialSquad();
  await loadPlayersTable();
  await loadGkMatrix();
});

// Setup Navigazione a Schede
function setupNavigation() {
  const tabs = document.querySelectorAll('.nav-tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
}

function switchTab(tabId) {
  state.activeTab = tabId;
  
  document.querySelectorAll('.nav-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });

  document.querySelectorAll('.view-section').forEach(sec => {
    sec.classList.toggle('active', sec.id === `view-${tabId}`);
  });
}

// Switcher tra "La Mia Rosa" e "20 Club Serie A"
function setupModeSwitcher() {
  const btnSquad = document.getElementById('btn-mode-squad');
  const btnClubs = document.getElementById('btn-mode-clubs');

  btnSquad?.addEventListener('click', () => {
    state.lineupMode = 'squad';
    btnSquad.classList.add('active');
    btnClubs?.classList.remove('active');

    document.getElementById('squad-controls-bar').style.display = 'flex';
    document.getElementById('club-quick-bar-container').style.display = 'none';
    document.getElementById('club-active-badge-container').style.display = 'none';
    document.getElementById('bench-section-container').style.display = 'block';
    document.getElementById('panel-squad-details').style.display = 'flex';
    document.getElementById('panel-club-details').style.display = 'none';
    document.getElementById('pitch-title-label').innerText = 'Campo Titolari (11)';

    optimizeLineup();
  });

  btnClubs?.addEventListener('click', () => {
    state.lineupMode = 'clubs';
    btnClubs.classList.add('active');
    btnSquad?.classList.remove('active');

    document.getElementById('squad-controls-bar').style.display = 'none';
    document.getElementById('club-quick-bar-container').style.display = 'block';
    document.getElementById('club-active-badge-container').style.display = 'flex';
    document.getElementById('bench-section-container').style.display = 'none';
    document.getElementById('panel-squad-details').style.display = 'none';
    document.getElementById('panel-club-details').style.display = 'flex';

    selectTacticalClub(state.activeClub || 'Inter');
  });
}

async function loadTacticalTeamsList() {
  try {
    const res = await window.api.getTacticalTeams();
    if (res && res.teams) {
      state.tacticalTeamsList = res.teams;
      const bar = document.getElementById('club-quick-bar');
      if (bar) {
        bar.innerHTML = res.teams.map(t => `
          <button class="club-quick-btn ${t.team === state.activeClub ? 'active' : ''}" data-team="${t.team}">
            ⚽ ${t.team}
          </button>
        `).join('');

        bar.querySelectorAll('.club-quick-btn').forEach(btn => {
          btn.addEventListener('click', () => {
            const tm = btn.getAttribute('data-team');
            selectTacticalClub(tm);
          });
        });
      }
    }
  } catch (err) {
    console.error('Errore caricamento lista 20 club:', err);
  }
}

async function selectTacticalClub(teamName) {
  state.activeClub = teamName;

  document.querySelectorAll('.club-quick-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-team') === teamName);
  });

  try {
    const clubData = await window.api.getTacticalTeam(teamName);
    renderClubTacticalView(clubData);
  } catch (err) {
    console.error(`Errore caricamento tattica per ${teamName}:`, err);
  }
}

function renderClubTacticalView(club) {
  // Update header badges
  const coachBadge = document.getElementById('club-active-coach');
  const formBadge = document.getElementById('club-active-formation');
  const scoreBadge = document.getElementById('expected-score-badge');
  const titleLabel = document.getElementById('pitch-title-label');

  if (coachBadge) coachBadge.innerText = `All: ${club.allenatore || 'N/D'}`;
  if (formBadge) formBadge.innerText = `Modulo: ${club.modulo || '4-3-3'}`;
  if (scoreBadge) scoreBadge.innerText = `⭐ Att: ${club.att_stars || 3}/5 | 🛡️ Dif: ${club.dif_stars || 3}/5`;
  if (titleLabel) titleLabel.innerText = `Probabile Formazione: ${club.team} (${club.modulo})`;

  // Render Lineup on Pitch
  renderClubLineupOnPitch(club.lineup, club.modulo);

  // Render Calci Piazzati
  renderClubSetPieces(club);

  // Render Ballottaggi
  renderClubBallottaggi(club.ballottaggi);

  // Render OOP & Consigliati
  renderClubOOP(club);

  // Render Club Roster
  renderClubRosterTable(club.roster);
}

function renderClubLineupOnPitch(lineup, modulo) {
  const rowPor = document.getElementById('pitch-row-por');
  const rowDef = document.getElementById('pitch-row-def');
  const rowMed = document.getElementById('pitch-row-med');
  const rowAtt = document.getElementById('pitch-row-att');

  if (!rowPor || !rowDef || !rowMed || !rowAtt) return;

  rowPor.innerHTML = '';
  rowDef.innerHTML = '';
  rowMed.innerHTML = '';
  rowAtt.innerHTML = '';

  lineup.forEach(slot => {
    const pos = (slot.pos || '').toUpperCase();
    const role = (slot.role || 'C').toUpperCase();
    const cardHtml = createClubPitchCardHtml(slot);

    if (pos === 'POR' || role === 'P') {
      rowPor.innerHTML += cardHtml;
    } else if (['TD', 'TS', 'DC', 'DC_D', 'DC_S', 'DC_C', 'BRAC_D', 'BRAC_S'].includes(pos) || role === 'D') {
      rowDef.innerHTML += cardHtml;
    } else if (['AD', 'AS', 'PC', 'PC_D', 'PC_S', 'PUN', 'ATT', 'SP', 'SS'].includes(pos) || role === 'A') {
      rowAtt.innerHTML += cardHtml;
    } else {
      rowMed.innerHTML += cardHtml;
    }
  });

  document.querySelectorAll('.pitch-card').forEach(card => {
    card.addEventListener('click', () => {
      const pid = parseInt(card.getAttribute('data-player-id'), 10);
      if (pid) openPlayerModal(pid);
    });
  });
}

function createClubPitchCardHtml(slot) {
  const role = (slot.role || 'C').toLowerCase();
  const subInfo = slot.sub_name ? `<div class="sub-indicator">vs ${slot.sub_name} (${100 - (slot.pct || 60)}%)</div>` : '';
  const oopBadge = slot.oop ? '<span class="oop-badge" style="font-size:0.6rem; padding:0.05rem 0.2rem;" title="Fuori Ruolo Positivo (FRP): schierato sul campo in una posizione più offensiva rispetto alla quotazione del listone">FRP</span>' : '';

  return `
    <div class="pitch-card" data-player-id="${slot.id || ''}">
      <span class="tactical-pos-badge">${slot.pos_label || slot.pos}</span>
      <span class="card-role-badge role-${role}">${slot.role || 'C'}</span>
      <div class="card-name" title="${slot.name}">${slot.name} ${oopBadge}</div>
      <div class="card-score" style="color:var(--accent-cyan); font-size:0.7rem;">${slot.pct || 80}% Tit.</div>
      ${subInfo}
    </div>
  `;
}

function renderClubSetPieces(club) {
  const container = document.getElementById('club-set-pieces-container');
  if (!container) return;

  const rigHtml = (club.rigoristi && club.rigoristi.length > 0)
    ? club.rigoristi.map((r, i) => `<li>${i+1}º ${r}</li>`).join('')
    : '<li>Nessun rigorista designato</li>';

  const punHtml = (club.punizioni && club.punizioni.length > 0)
    ? club.punizioni.map((r, i) => `<li>${i+1}º ${r}</li>`).join('')
    : '<li>Nessuno designato</li>';

  const corHtml = (club.corner && club.corner.length > 0)
    ? club.corner.map((r, i) => `<li>${i+1}º ${r}</li>`).join('')
    : '<li>Nessuno designato</li>';

  container.innerHTML = `
    <div class="set-piece-card">
      <div class="set-piece-title">🎯 Rigoristi</div>
      <ul class="set-piece-list">${rigHtml}</ul>
    </div>
    <div class="set-piece-card">
      <div class="set-piece-title">👟 Punizioni</div>
      <ul class="set-piece-list">${punHtml}</ul>
    </div>
    <div class="set-piece-card">
      <div class="set-piece-title">🚩 Calci d'Angolo</div>
      <ul class="set-piece-list">${corHtml}</ul>
    </div>
  `;
}

function renderClubBallottaggi(ballottaggi) {
  const container = document.getElementById('club-ballottaggi-container');
  if (!container) return;

  if (!ballottaggi || ballottaggi.length === 0) {
    container.innerHTML = '<p class="text-secondary" style="font-size:0.85rem;">Nessun ballottaggio serrato segnalato.</p>';
    return;
  }

  container.innerHTML = ballottaggi.map(b => `
    <div class="ballot-card">
      <div class="ballot-header">
        <span>${b.player} <strong style="color:var(--accent-neon);">${b.pct}%</strong></span>
        <span class="text-secondary">vs ${b.vs}</span>
      </div>
      <div class="ballot-bar">
        <div class="ballot-fill" style="width: ${b.pct}%;"></div>
      </div>
    </div>
  `).join('');
}

function renderClubOOP(club) {
  const container = document.getElementById('club-oop-container');
  if (!container) return;

  const oopList = club.oop_players || [];
  const topList = club.top || [];
  const sleeperList = club.sleeper || [];

  let html = '';

  if (topList.length > 0) {
    html += `<div style="margin-bottom:0.5rem;"><strong style="color:var(--accent-gold); font-size:0.85rem;">⭐ Top Consigliati:</strong> <span style="font-size:0.85rem;">${topList.join(', ')}</span></div>`;
  }
  if (sleeperList.length > 0) {
    html += `<div style="margin-bottom:0.5rem;"><strong style="color:var(--accent-cyan); font-size:0.85rem;" title="Calciatori dal costo contenuto con statistiche avanzate (xG/xA) ad alto potenziale">🔥 Scommesse ad Alto Potenziale:</strong> <span style="font-size:0.85rem;">${sleeperList.join(', ')}</span></div>`;
  }

  if (oopList.length > 0) {
    html += '<div style="margin-top:0.75rem;"><strong style="color:var(--accent-purple); font-size:0.85rem;" title="Fuori Ruolo Positivo (FRP): Calciatori listati più arretrati rispetto alla loro posizione reale sul campo">💎 Giocatori Fuori Ruolo Positivo (FRP):</strong></div>';
    html += oopList.map(o => `
      <div class="oop-badge" style="display:block; margin-top:0.4rem;">
        <strong>${o.name}</strong> (${o.role}) ➜ ${o.pos_label}
        <div style="font-size:0.75rem; color:var(--text-secondary);">${o.oop_desc}</div>
      </div>
    `).join('');
  }

  if (!html) {
    html = '<p class="text-secondary" style="font-size:0.85rem;">Nessuna segnalazione speciale per questo club.</p>';
  }

  container.innerHTML = html;
}

function renderClubRosterTable(roster) {
  const tbody = document.getElementById('club-roster-tbody');
  if (!tbody) return;

  if (!roster || roster.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">Nessun calciatore trovato.</td></tr>';
    return;
  }

  tbody.innerHTML = roster.map(p => {
    const isSquad = state.mySquad.some(sp => sp.id === p.id);
    return `
      <tr onclick="openPlayerModal(${p.id})">
        <td><span class="card-role-badge role-${p.role.toLowerCase()}">${p.role}</span></td>
        <td><strong>${p.name}</strong></td>
        <td>${p.fvm || '-'}</td>
        <td>${p.qta || '-'}</td>
        <td>
          <button class="btn-secondary" style="padding: 0.2rem 0.5rem; font-size:0.7rem;" onclick="event.stopPropagation(); toggleSquadPlayer(${p.id})">
            ${isSquad ? '❌' : '➕ Rosa'}
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function setupEventListeners() {
  // Lineup controls
  document.getElementById('btn-optimize-lineup')?.addEventListener('click', optimizeLineup);
  document.getElementById('select-formation')?.addEventListener('change', (e) => {
    state.selectedModule = e.target.value;
    optimizeLineup();
  });
  document.getElementById('check-defense-mod')?.addEventListener('change', optimizeLineup);
  document.getElementById('select-risk')?.addEventListener('change', optimizeLineup);

  // Player search & filter
  const searchInput = document.getElementById('input-player-search');
  let debounceTimeout = null;
  searchInput?.addEventListener('input', (e) => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
      state.playersSearchQuery = e.target.value;
      state.playersPage = 1;
      loadPlayersTable();
    }, 250);
  });

  document.getElementById('select-role-filter')?.addEventListener('change', (e) => {
    state.playersRoleFilter = e.target.value;
    state.playersPage = 1;
    loadPlayersTable();
  });

  document.getElementById('select-sort-by')?.addEventListener('change', (e) => {
    state.playersSortBy = e.target.value;
    loadPlayersTable();
  });

  // Modal close
  document.getElementById('modal-close-btn')?.addEventListener('click', closeModal);
  document.getElementById('player-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'player-modal') closeModal();
  });

  // Auction advice
  document.getElementById('btn-calc-bid')?.addEventListener('click', calculateAuctionBid);
}

function populateModuleSelect(modules) {
  const select = document.getElementById('select-formation');
  if (!select) return;
  select.innerHTML = '<option value="auto">✨ Modulo Ottimale (Auto AI)</option>' +
    modules.map(m => `<option value="${m}">${m}</option>`).join('');
}

// Caricamento Rosa Iniziale
async function loadInitialSquad() {
  try {
    const saved = localStorage.getItem('FANTA_MY_SQUAD');
    if (saved) {
      state.mySquad = JSON.parse(saved);
    } else {
      const topP = await window.api.getPlayers({ role: 'P', page_size: 2, sort_by: 'fvm' });
      const topD = await window.api.getPlayers({ role: 'D', page_size: 7, sort_by: 'fvm' });
      const topC = await window.api.getPlayers({ role: 'C', page_size: 7, sort_by: 'fvm' });
      const topA = await window.api.getPlayers({ role: 'A', page_size: 5, sort_by: 'fvm' });

      state.mySquad = [
        ...topP.players,
        ...topD.players,
        ...topC.players,
        ...topA.players
      ];
      localStorage.setItem('FANTA_MY_SQUAD', JSON.stringify(state.mySquad));
    }
    await optimizeLineup();
  } catch (err) {
    console.error('Errore caricamento rosa iniziale:', err);
  }
}

// Ottimizzatore Formazione via API
async function optimizeLineup() {
  if (state.lineupMode === 'clubs') return;

  const notesContainer = document.getElementById('lineup-tactical-notes');
  const scoreBadge = document.getElementById('expected-score-badge');

  if (!state.mySquad || state.mySquad.length < 11) {
    if (notesContainer) notesContainer.innerHTML = '<p class="text-secondary">Seleziona almeno 11 giocatori nella tua rosa per calcolare la formazione.</p>';
    return;
  }

  const playerIds = state.mySquad.map(p => p.id);
  const useDefMod = document.getElementById('check-defense-mod')?.checked ?? true;
  const risk = document.getElementById('select-risk')?.value || 'balanced';

  try {
    const result = await window.api.recommendLineup({
      player_ids: playerIds,
      formation: state.selectedModule,
      use_defense_modifier: useDefMod,
      risk_tolerance: risk
    });

    if (scoreBadge) {
      scoreBadge.innerText = `${result.expected_team_score} pt attesi`;
    }

    renderStartersOnPitch(result.starters, result.formation);
    renderBench(result.bench);

    if (notesContainer && result.tactical_notes) {
      notesContainer.innerHTML = result.tactical_notes.map(n => `<div class="note-pill">💡 ${n}</div>`).join('');
    }
  } catch (err) {
    console.error('Errore ottimizzazione formazione:', err);
    if (notesContainer) {
      notesContainer.innerHTML = `<div class="error-pill">⚠️ ${err.message}</div>`;
    }
  }
}

// Render Titolari sul Campo 2D
function renderStartersOnPitch(starters, formation) {
  const rowPor = document.getElementById('pitch-row-por');
  const rowDef = document.getElementById('pitch-row-def');
  const rowMed = document.getElementById('pitch-row-med');
  const rowAtt = document.getElementById('pitch-row-att');

  if (!rowPor || !rowDef || !rowMed || !rowAtt) return;

  rowPor.innerHTML = '';
  rowDef.innerHTML = '';
  rowMed.innerHTML = '';
  rowAtt.innerHTML = '';

  starters.forEach(p => {
    const cardHtml = createPitchCardHtml(p);
    const role = p.role.toUpperCase();

    if (role === 'P') {
      rowPor.innerHTML += cardHtml;
    } else if (role === 'D') {
      rowDef.innerHTML += cardHtml;
    } else if (role === 'C') {
      rowMed.innerHTML += cardHtml;
    } else if (role === 'A') {
      rowAtt.innerHTML += cardHtml;
    }
  });

  document.querySelectorAll('.pitch-card').forEach(card => {
    card.addEventListener('click', () => {
      const pid = parseInt(card.getAttribute('data-player-id'), 10);
      if (pid) openPlayerModal(pid);
    });
  });
}

function renderBench(benchPlayers) {
  const container = document.getElementById('bench-players-grid');
  if (!container) return;

  if (!benchPlayers || benchPlayers.length === 0) {
    container.innerHTML = '<span class="text-secondary">Nessun panchinaro</span>';
    return;
  }

  container.innerHTML = benchPlayers.map(p => `
    <div class="pitch-card" data-player-id="${p.id}">
      <span class="card-role-badge role-${p.role.toLowerCase()}">${p.role}</span>
      <div class="card-name">${p.name}</div>
      <div class="card-meta">${p.team}</div>
      <div class="card-score">${p.expected_score} pt</div>
    </div>
  `).join('');

  container.querySelectorAll('.pitch-card').forEach(card => {
    card.addEventListener('click', () => {
      const pid = parseInt(card.getAttribute('data-player-id'), 10);
      if (pid) openPlayerModal(pid);
    });
  });
}

function createPitchCardHtml(p) {
  return `
    <div class="pitch-card" data-player-id="${p.id}">
      <span class="card-role-badge role-${p.role.toLowerCase()}">${p.role}</span>
      <div class="card-name" title="${p.name}">${p.name}</div>
      <div class="card-meta">${p.team}</div>
      <div class="card-score">⚡ ${p.expected_score}</div>
    </div>
  `;
}

// Tabella Esplora Giocatori
async function loadPlayersTable() {
  const tbody = document.getElementById('players-table-body');
  const countSpan = document.getElementById('players-total-count');
  const pageLabel = document.getElementById('current-page-label');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 2rem;">Caricamento in corso...</td></tr>';

  try {
    const data = await window.api.getPlayers({
      query: state.playersSearchQuery,
      role: state.playersRoleFilter,
      sort_by: state.playersSortBy,
      order: state.playersOrder,
      page: state.playersPage,
      page_size: state.playersPageSize
    });

    if (countSpan) countSpan.innerText = `${data.total} giocatori`;
    if (pageLabel) pageLabel.innerText = `Pagina ${data.page} di ${Math.ceil(data.total / state.playersPageSize)}`;

    if (data.players.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 2rem;">Nessun giocatore trovato con questi filtri.</td></tr>';
      return;
    }

    tbody.innerHTML = data.players.map(p => {
      const fmVal = p.fm_2627 || p.fm || '-';
      const isSquad = state.mySquad.some(sp => sp.id === p.id);

      return `
        <tr onclick="openPlayerModal(${p.id})">
          <td><span class="card-role-badge role-${p.role.toLowerCase()}">${p.role}</span></td>
          <td><strong>${p.name}</strong></td>
          <td>${p.team}</td>
          <td><strong>${p.fvm || '-'}</strong></td>
          <td>${p.qta || '-'}</td>
          <td><span style="color: var(--accent-neon); font-weight:700;">${fmVal}</span></td>
          <td>
            <button class="btn-secondary" style="padding: 0.3rem 0.6rem; font-size:0.75rem;" onclick="event.stopPropagation(); toggleSquadPlayer(${p.id})">
              ${isSquad ? '❌ Rimuovi' : '➕ Rosa'}
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Errore caricamento tabella giocatori:', err);
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--accent-danger);">Errore: ${err.message}</td></tr>`;
  }
}

// Aggiungi / Rimuovi dalla Rosa
async function toggleSquadPlayer(playerId) {
  const idx = state.mySquad.findIndex(p => p.id === playerId);
  if (idx >= 0) {
    state.mySquad.splice(idx, 1);
  } else {
    const player = await window.api.getPlayerById(playerId);
    if (player) state.mySquad.push(player);
  }
  localStorage.setItem('FANTA_MY_SQUAD', JSON.stringify(state.mySquad));
  loadPlayersTable();
  if (state.activeTab === 'lineup' && state.lineupMode === 'squad') {
    optimizeLineup();
  }
}

// Modal Dettaglio Giocatore
async function openPlayerModal(playerId) {
  const modal = document.getElementById('player-modal');
  const modalBody = document.getElementById('player-modal-content');
  if (!modal || !modalBody) return;

  modal.classList.add('active');
  modalBody.innerHTML = '<p style="text-align:center; padding: 2rem;">Caricamento dettagli...</p>';

  try {
    const p = await window.api.getPlayerById(playerId);
    state.selectedPlayer = p;

    const voti = p.voti_dettaglio_2627 || [];
    const votiHtml = voti.length > 0
      ? `<table class="custom-table" style="font-size:0.8rem; margin-top:1rem;">
          <thead>
            <tr><th>G</th><th>Partita</th><th>Voto</th><th>FV</th><th>Bonus/Malus</th></tr>
          </thead>
          <tbody>
            ${voti.map(v => `
              <tr>
                <td><strong>G${v.giornata}</strong></td>
                <td>${v.match || v.opponent || '-'}</td>
                <td>${v.voto || '-'}</td>
                <td><strong style="color:var(--accent-neon);">${v.fantavoto || '-'}</strong></td>
                <td>${v.bonus_malus_str || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
         </table>`
      : '<p class="text-secondary" style="margin-top:1rem;">Nessun voto registrato nella stagione corrente.</p>';

    modalBody.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <div>
          <span class="card-role-badge role-${p.role.toLowerCase()}">${p.role}</span>
          <h2 style="font-size:1.5rem; margin-top:0.3rem;">${p.name}</h2>
          <span class="text-secondary">${p.team} ${p.mantra ? `(${p.mantra})` : ''}</span>
        </div>
        <div style="text-align:right;">
          <div style="font-size:1.5rem; font-weight:800; color:var(--accent-neon);">FVM ${p.fvm || '-'}</div>
          <div class="text-secondary" style="font-size:0.8rem;">Quotazione: ${p.qta || '-'}</div>
        </div>
      </div>

      <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.75rem; margin: 1rem 0;">
        <div class="stat-widget">
          <div class="stat-value">${p.fm_2627 || p.fm || '-'}</div>
          <div class="stat-label">FantaMedia</div>
        </div>
        <div class="stat-widget">
          <div class="stat-value">${p.gol_2627 !== undefined ? p.gol_2627 : (p.gf || 0)}</div>
          <div class="stat-label">Gol Totali</div>
        </div>
        <div class="stat-widget">
          <div class="stat-value">${p.titolarita || 85}%</div>
          <div class="stat-label">Titolarità</div>
        </div>
      </div>

      <h3 style="font-size:1rem; margin-top:1.5rem; border-bottom:1px solid var(--border-glass); padding-bottom:0.5rem;">Storico Partite & Voti 2026/27</h3>
      ${votiHtml}
    `;
  } catch (err) {
    modalBody.innerHTML = `<p style="color:var(--accent-danger);">Errore nel caricamento del giocatore: ${err.message}</p>`;
  }
}

function closeModal() {
  document.getElementById('player-modal')?.classList.remove('active');
}

// Griglia Incroci Portieri
async function loadGkMatrix() {
  const container = document.getElementById('gk-pairs-list');
  if (!container) return;

  try {
    const data = await window.api.getGkMatrix();
    if (!data.best_pairs || data.best_pairs.length === 0) {
      container.innerHTML = '<p class="text-secondary">Nessun dato sulla griglia portieri disponibile.</p>';
      return;
    }

    container.innerHTML = data.best_pairs.slice(0, 15).map(pair => `
      <div class="glass-panel" style="padding: 1rem; display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
        <div>
          <strong style="font-size:1rem;">🧤 ${pair.team_a} + ${pair.team_b}</strong>
          <div class="text-secondary" style="font-size:0.8rem;">${pair.consiglio}</div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:1.1rem; font-weight:800; color:var(--accent-neon);">${pair.malus_sovrapposizione} malus</div>
          <div class="text-secondary" style="font-size:0.75rem;">Indice: ${pair.indice_alternanza}/38</div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Errore caricamento matrice portieri:', err);
    container.innerHTML = `<p style="color:var(--accent-danger);">Errore: ${err.message}</p>`;
  }
}

// Calcolatore Offerta Asta
async function calculateAuctionBid() {
  const select = document.getElementById('auction-player-select');
  const budgetInput = document.getElementById('auction-budget-input');
  const resultContainer = document.getElementById('auction-advice-result');

  const pid = parseInt(select?.value, 10);
  const budget = parseInt(budgetInput?.value, 10) || 500;

  if (!pid) {
    resultContainer.innerHTML = '<p class="text-secondary">Seleziona un giocatore dal database.</p>';
    return;
  }

  try {
    const advice = await window.api.getBidAdvice({
      player_id: pid,
      current_budget: budget,
      total_budget: 500
    });

    resultContainer.innerHTML = `
      <div class="glass-panel" style="border-left: 4px solid var(--accent-neon); margin-top:1rem;">
        <h3 style="font-size:1.2rem; color:var(--accent-neon);">${advice.tier}</h3>
        <p style="font-size:1.1rem; margin: 0.5rem 0;"><strong>${advice.advice}</strong></p>
        <div style="display:flex; gap:1.5rem; margin-top:0.75rem;">
          <div>Prezzo Target: <strong style="color:var(--accent-gold);">${advice.target_price} crediti</strong></div>
          <div>Offerta Massima: <strong style="color:var(--accent-danger);">${advice.max_bid} crediti</strong></div>
        </div>
        <div class="text-secondary" style="font-size:0.85rem; margin-top:0.5rem;">${advice.risk_assessment}</div>
      </div>
    `;
  } catch (err) {
    resultContainer.innerHTML = `<p style="color:var(--accent-danger);">Errore: ${err.message}</p>`;
  }
}

// Registrazione Service Worker PWA
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js')
      .then(() => console.log('[PWA] Service Worker registrato con successo.'))
      .catch(err => console.warn('[PWA] Errore registrazione Service Worker:', err));
  }
}

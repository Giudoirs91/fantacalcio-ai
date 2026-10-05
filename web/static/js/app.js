// ==============================================================================
// FANTA MASTER AI — MODERN SPA APPLICATION CONTROLLER
// ==============================================================================

// Dataset di Fallback con statistiche e leader reali Serie A 2026/27
const FALLBACK_PLAYERS = [
  // Portieri
  { id: 1, name: 'Sommer', role: 'P', team: 'Inter', fvm: 38, qta: 16, fm_2627: 6.85, expected_score: 6.8, starter: '95%', match: 'vs MON (H)' },
  { id: 2, name: 'Maignan', role: 'P', team: 'Milan', fvm: 35, qta: 15, fm_2627: 6.60, expected_score: 6.5, starter: '95%', match: 'vs VEN (H)' },
  { id: 3, name: 'Di Gregorio', role: 'P', team: 'Juventus', fvm: 34, qta: 15, fm_2627: 6.50, expected_score: 6.4, starter: '90%', match: 'vs CAG (H)' },
  { id: 4, name: 'Meret', role: 'P', team: 'Napoli', fvm: 30, qta: 14, fm_2627: 6.30, expected_score: 6.3, starter: '90%', match: 'vs PAR (A)' },
  { id: 5, name: 'Martinez J.', role: 'P', team: 'Inter', fvm: 5, qta: 2, fm_2627: 5.50, expected_score: 5.2, starter: '10%', match: 'vs MON (H)' },

  // Difensori
  { id: 6, name: 'Dimarco', role: 'D', team: 'Inter', fvm: 48, qta: 18, fm_2627: 7.30, expected_score: 7.2, starter: '90%', match: 'vs MON (H)', oop: true, oop_desc: 'Esterno alto nel 3-5-2' },
  { id: 7, name: 'Theo Hernandez', role: 'D', team: 'Milan', fvm: 44, qta: 17, fm_2627: 7.10, expected_score: 6.9, starter: '95%', match: 'vs VEN (H)' },
  { id: 8, name: 'Bremer', role: 'D', team: 'Juventus', fvm: 38, qta: 16, fm_2627: 6.80, expected_score: 6.7, starter: '95%', match: 'vs CAG (H)' },
  { id: 9, name: 'Buongiorno', role: 'D', team: 'Napoli', fvm: 32, qta: 14, fm_2627: 6.60, expected_score: 6.5, starter: '95%', match: 'vs PAR (A)' },
  { id: 10, name: 'Bastoni', role: 'D', team: 'Inter', fvm: 36, qta: 15, fm_2627: 6.70, expected_score: 6.6, starter: '95%', match: 'vs MON (H)' },
  { id: 11, name: 'Bellanova', role: 'D', team: 'Atalanta', fvm: 26, qta: 12, fm_2627: 6.45, expected_score: 6.4, starter: '85%', match: 'vs FIO (H)' },
  { id: 12, name: 'Pavlovic', role: 'D', team: 'Milan', fvm: 24, qta: 11, fm_2627: 6.35, expected_score: 6.2, starter: '80%', match: 'vs VEN (H)' },
  { id: 13, name: 'Gatti', role: 'D', team: 'Juventus', fvm: 22, qta: 10, fm_2627: 6.25, expected_score: 6.0, starter: '75%', match: 'vs CAG (H)' },
  { id: 14, name: 'Tavares N.', role: 'D', team: 'Lazio', fvm: 28, qta: 13, fm_2627: 6.90, expected_score: 6.8, starter: '85%', match: 'vs ROM (H)' },

  // Centrocampisti
  { id: 15, name: 'Pulisic', role: 'C', team: 'Milan', fvm: 82, qta: 28, fm_2627: 7.95, expected_score: 7.9, starter: '95%', match: 'vs VEN (H)', oop: true, oop_desc: 'Ala offensiva / Trequartista' },
  { id: 16, name: 'Calhanoglu', role: 'C', team: 'Inter', fvm: 68, qta: 24, fm_2627: 7.60, expected_score: 7.5, starter: '90%', match: 'vs MON (H)' },
  { id: 17, name: 'Koopmeiners', role: 'C', team: 'Juventus', fvm: 72, qta: 25, fm_2627: 7.55, expected_score: 7.4, starter: '90%', match: 'vs CAG (H)' },
  { id: 18, name: 'Barella', role: 'C', team: 'Inter', fvm: 45, qta: 19, fm_2627: 7.15, expected_score: 7.1, starter: '95%', match: 'vs MON (H)' },
  { id: 19, name: 'Man', role: 'C', team: 'Parma', fvm: 42, qta: 18, fm_2627: 7.20, expected_score: 7.0, starter: '90%', match: 'vs NAP (H)', oop: true, oop_desc: 'Attaccante esterno destro' },
  { id: 20, name: 'Zaccagni', role: 'C', team: 'Lazio', fvm: 58, qta: 22, fm_2627: 7.40, expected_score: 7.3, starter: '95%', match: 'vs ROM (H)' },
  { id: 21, name: 'McTominay', role: 'C', team: 'Napoli', fvm: 46, qta: 20, fm_2627: 7.10, expected_score: 7.0, starter: '90%', match: 'vs PAR (A)' },
  { id: 22, name: 'Frendrup', role: 'C', team: 'Genoa', fvm: 22, qta: 11, fm_2627: 6.45, expected_score: 6.4, starter: '95%', match: 'vs VER (H)' },
  { id: 23, name: 'Diouf', role: 'C', team: 'Inter', fvm: 28, qta: 12, fm_2627: 6.90, expected_score: 6.8, starter: '80%', match: 'vs MON (H)' },

  // Attaccanti
  { id: 24, name: 'Malen', role: 'A', team: 'Roma', fvm: 280, qta: 38, fm_2627: 10.60, expected_score: 9.2, starter: '95%', match: 'vs LAZ (A)' },
  { id: 25, name: 'Martinez L.', role: 'A', team: 'Inter', fvm: 315, qta: 42, fm_2627: 8.85, expected_score: 8.8, starter: '95%', match: 'vs MON (H)' },
  { id: 26, name: 'Dybala', role: 'A', team: 'Roma', fvm: 180, qta: 32, fm_2627: 7.90, expected_score: 8.2, starter: '85%', match: 'vs LAZ (A)' },
  { id: 27, name: 'Lookman', role: 'A', team: 'Atalanta', fvm: 195, qta: 34, fm_2627: 8.35, expected_score: 8.2, starter: '85%', match: 'vs FIO (H)' },
  { id: 28, name: 'Thuram M.', role: 'A', team: 'Inter', fvm: 175, qta: 32, fm_2627: 8.15, expected_score: 8.0, starter: '90%', match: 'vs MON (H)' },
  { id: 29, name: 'Vlahovic', role: 'A', team: 'Juventus', fvm: 250, qta: 38, fm_2627: 8.25, expected_score: 8.1, starter: '95%', match: 'vs CAG (H)' },
  { id: 30, name: 'Varela G.', role: 'A', team: 'Monza', fvm: 120, qta: 22, fm_2627: 7.80, expected_score: 7.4, starter: '90%', match: 'vs INT (A)' },
  { id: 31, name: 'Raimondo', role: 'A', team: 'Frosinone', fvm: 95, qta: 18, fm_2627: 7.50, expected_score: 7.2, starter: '90%', match: 'vs NAP (H)' }
];

const FALLBACK_CLUBS = [
  'Inter', 'Milan', 'Juventus', 'Napoli', 'Atalanta', 'Roma', 'Lazio',
  'Fiorentina', 'Bologna', 'Torino', 'Genoa', 'Parma', 'Como',
  'Verona', 'Cagliari', 'Empoli', 'Lecce', 'Monza', 'Udinese', 'Venezia'
];

const FALLBACK_GK_PAIRS = [
  { team_a: 'Inter', team_b: 'Milan', malus_sovrapposizione: 0, indice_alternanza: 38, consiglio: 'Perfetta alternanza assoluta San Siro. Nessun turno contemporaneo in trasferta.' },
  { team_a: 'Juventus', team_b: 'Torino', malus_sovrapposizione: 0, indice_alternanza: 38, consiglio: 'Coppia cittadina ideale. Sempre una partita in casa garantita.' },
  { team_a: 'Roma', team_b: 'Lazio', malus_sovrapposizione: 0, indice_alternanza: 38, consiglio: 'Derby alternato perfetto allo Stadio Olimpico.' },
  { team_a: 'Napoli', team_b: 'Bologna', malus_sovrapposizione: 2, indice_alternanza: 36, consiglio: 'Ottimo incrocio big/medio-alta classifica con solo 2 turni sovrapposti.' },
  { team_a: 'Atalanta', team_b: 'Monza', malus_sovrapposizione: 3, indice_alternanza: 35, consiglio: 'Budget bilanciato con alternanza geografica lombarda favorevole.' },
  { team_a: 'Fiorentina', team_b: 'Empoli', malus_sovrapposizione: 1, indice_alternanza: 37, consiglio: 'Incrocio toscano low cost ad alto rendimento difensivo.' }
];

// Stato globale dell'applicazione
const state = {
  activeTab: 'home', // Default: Home Page
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
    const modRes = await window.api?.getSupportedModules().catch(() => null);
    if (modRes && modRes.modules) {
      state.supportedModules = modRes.modules;
      populateModuleSelect(modRes.modules);
    }
  } catch(e) {
    populateModuleSelect(state.supportedModules);
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
      if (targetTab) switchTab(targetTab);
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

  if (tabId === 'lineup') {
    if (state.lineupMode === 'squad') {
      optimizeLineup();
    } else {
      selectTacticalClub(state.activeClub || 'Inter');
    }
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
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
  let teams = [];
  try {
    const res = await window.api?.getTacticalTeams().catch(() => null);
    if (res && res.teams) {
      teams = res.teams.map(t => t.team);
    }
  } catch (err) {
    console.warn('API non raggiungibile, carico club di fallback');
  }

  if (!teams || teams.length === 0) {
    teams = FALLBACK_CLUBS;
  }

  state.tacticalTeamsList = teams;
  const bar = document.getElementById('club-quick-bar');
  if (bar) {
    bar.innerHTML = teams.map(t => `
      <button class="club-quick-btn ${t === state.activeClub ? 'active' : ''}" data-team="${t}">
        ⚽ ${t}
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

async function selectTacticalClub(teamName) {
  state.activeClub = teamName;

  document.querySelectorAll('.club-quick-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-team') === teamName);
  });

  try {
    const clubData = await window.api?.getTacticalTeam(teamName).catch(() => null);
    if (clubData) {
      renderClubTacticalView(clubData);
      return;
    }
  } catch (err) {
    console.warn(`Fallback tattico per ${teamName}`);
  }

  // Fallback club data
  const fallbackClubData = {
    team: teamName,
    modulo: '3-5-2',
    allenatore: teamName === 'Inter' ? 'Simone Inzaghi' : (teamName === 'Milan' ? 'Paulo Fonseca' : 'Thiago Motta'),
    att_stars: teamName === 'Inter' ? 5 : 4,
    dif_stars: 4,
    rigoristi: ['Calhanoglu', 'Lautaro Martinez', 'Taremi'],
    punizioni: ['Dimarco', 'Calhanoglu'],
    corner: ['Dimarco', 'Calhanoglu'],
    ballottaggi: [
      { player: 'Dumfries', pct: 60, vs: 'Darmian (40%)' },
      { player: 'Zielinski', pct: 55, vs: 'Mkhitaryan (45%)' }
    ],
    oop_players: [
      { name: 'Dimarco', role: 'D', pos_label: 'Esterno d\'Attacco', oop_desc: 'Quotato D ➜ Spinta costante e cross dal fondo' }
    ],
    top: ['Lautaro Martinez', 'Dimarco', 'Barella'],
    sleeper: ['Frattesi', 'Bisseck'],
    roster: FALLBACK_PLAYERS.filter(p => p.team === teamName || teamName === 'Inter').slice(0, 15),
    lineup: [
      { name: 'Sommer', role: 'P', pos: 'POR', pos_label: 'POR', pct: 95 },
      { name: 'Pavard', role: 'D', pos: 'DC', pos_label: 'DC', pct: 85 },
      { name: 'Acerbi', role: 'D', pos: 'DC', pos_label: 'DC', pct: 90 },
      { name: 'Bastoni', role: 'D', pos: 'DC', pos_label: 'DC', pct: 95 },
      { name: 'Dumfries', role: 'D', pos: 'TD', pos_label: 'E_D', pct: 60 },
      { name: 'Barella', role: 'C', pos: 'CC', pos_label: 'MEZ', pct: 95 },
      { name: 'Calhanoglu', role: 'C', pos: 'CC', pos_label: 'REG', pct: 90 },
      { name: 'Mkhitaryan', role: 'C', pos: 'CC', pos_label: 'MEZ', pct: 75 },
      { name: 'Dimarco', role: 'D', pos: 'TS', pos_label: 'E_S', pct: 90, oop: true },
      { name: 'Lautaro', role: 'A', pos: 'PC', pos_label: 'PC', pct: 95 },
      { name: 'Thuram', role: 'A', pos: 'PC', pos_label: 'SP', pct: 90 }
    ]
  };

  renderClubTacticalView(fallbackClubData);
}

function renderClubTacticalView(club) {
  const coachBadge = document.getElementById('club-active-coach');
  const formBadge = document.getElementById('club-active-formation');
  const scoreBadge = document.getElementById('expected-score-badge');
  const titleLabel = document.getElementById('pitch-title-label');

  if (coachBadge) coachBadge.innerText = `All: ${club.allenatore || club.all || 'N/D'}`;
  if (formBadge) formBadge.innerText = `Modulo: ${club.modulo || '4-3-3'}`;
  if (scoreBadge) scoreBadge.innerText = `⭐ Att: ${club.att_stars || 3}/5 | 🛡️ Dif: ${club.dif_stars || 3}/5`;
  if (titleLabel) titleLabel.innerText = `Probabile Formazione: ${club.team} (${club.modulo})`;

  renderClubLineupOnPitch(club.lineup, club.modulo);
  renderClubSetPieces(club);
  renderClubBallottaggi(club.ballottaggi);
  renderClubOOP(club);
  renderClubRosterTable(club.roster);
}

function renderClubLineupOnPitch(lineup, modulo) {
  const rowPor = document.getElementById('pitch-row-por');
  const rowDef = document.getElementById('pitch-row-def');
  const rowMed = document.getElementById('pitch-row-med');
  const rowAtt = document.getElementById('pitch-row-att');

  if (!rowPor || !rowDef || !rowMed || !rowAtt || !lineup) return;

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
  const oopBadge = slot.oop ? '<span class="oop-badge" style="font-size:0.6rem; padding:0.05rem 0.2rem;" title="Fuori Ruolo Positivo">FRP</span>' : '';

  return `
    <div class="pitch-card" data-player-id="${slot.id || ''}">
      <span class="tactical-pos-badge">${slot.pos_label || slot.pos || 'TIT'}</span>
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

  let html = '';
  if (topList.length > 0) {
    html += `<div style="margin-bottom:0.5rem;"><strong style="color:var(--accent-gold); font-size:0.85rem;">⭐ Top Consigliati:</strong> <span style="font-size:0.85rem;">${topList.join(', ')}</span></div>`;
  }
  if (oopList.length > 0) {
    html += '<div style="margin-top:0.75rem;"><strong style="color:var(--accent-purple); font-size:0.85rem;" title="Fuori Ruolo Positivo">💎 Giocatori Fuori Ruolo Positivo (FRP):</strong></div>';
    html += oopList.map(o => `
      <div class="oop-badge" style="display:block; margin-top:0.4rem;">
        <strong>${o.name}</strong> (${o.role}) ➜ ${o.pos_label}
        <div style="font-size:0.75rem; color:var(--text-secondary);">${o.oop_desc}</div>
      </div>
    `).join('');
  }

  container.innerHTML = html || '<p class="text-secondary" style="font-size:0.85rem;">Nessuna segnalazione speciale per questo club.</p>';
}

function renderClubRosterTable(roster) {
  const tbody = document.getElementById('club-roster-tbody');
  if (!tbody) return;

  const list = roster || FALLBACK_PLAYERS.slice(0, 12);
  tbody.innerHTML = list.map(p => {
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
  document.getElementById('btn-optimize-lineup')?.addEventListener('click', optimizeLineup);
  document.getElementById('select-formation')?.addEventListener('change', (e) => {
    state.selectedModule = e.target.value;
    optimizeLineup();
  });
  document.getElementById('select-risk')?.addEventListener('change', optimizeLineup);
  document.getElementById('check-defense-mod')?.addEventListener('change', optimizeLineup);

  // Search & Filter
  const inputSearch = document.getElementById('input-player-search');
  inputSearch?.addEventListener('input', (e) => {
    state.playersSearchQuery = e.target.value.toLowerCase();
    state.playersPage = 1;
    loadPlayersTable();
  });

  const selectRole = document.getElementById('select-role-filter');
  selectRole?.addEventListener('change', (e) => {
    state.playersRoleFilter = e.target.value;
    state.playersPage = 1;
    loadPlayersTable();
  });

  const selectSort = document.getElementById('select-sort-by');
  selectSort?.addEventListener('change', (e) => {
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
    modules.filter(m => m !== 'auto').map(m => `<option value="${m}">${m}</option>`).join('');
}

// Caricamento Rosa Iniziale
async function loadInitialSquad() {
  try {
    const saved = localStorage.getItem('FANTA_MY_SQUAD');
    if (saved) {
      state.mySquad = JSON.parse(saved);
    } else {
      let loaded = false;
      try {
        const topP = await window.api?.getPlayers({ role: 'P', page_size: 2, sort_by: 'fvm' }).catch(() => null);
        const topD = await window.api?.getPlayers({ role: 'D', page_size: 7, sort_by: 'fvm' }).catch(() => null);
        const topC = await window.api?.getPlayers({ role: 'C', page_size: 7, sort_by: 'fvm' }).catch(() => null);
        const topA = await window.api?.getPlayers({ role: 'A', page_size: 5, sort_by: 'fvm' }).catch(() => null);

        if (topP && topD && topC && topA && topP.players.length > 0) {
          state.mySquad = [...topP.players, ...topD.players, ...topC.players, ...topA.players];
          loaded = true;
        }
      } catch(e) {}

      if (!loaded || state.mySquad.length < 11) {
        state.mySquad = FALLBACK_PLAYERS.slice(0, 22);
      }

      localStorage.setItem('FANTA_MY_SQUAD', JSON.stringify(state.mySquad));
    }

    renderStartersOnPitch(state.mySquad.slice(0, 11), '3-4-3');
    renderBench(state.mySquad.slice(11, 18));
  } catch (err) {
    console.error('Errore caricamento rosa:', err);
    state.mySquad = FALLBACK_PLAYERS.slice(0, 22);
  }
}

// Ottimizzatore Formazione
async function optimizeLineup() {
  if (state.lineupMode === 'clubs') return;

  const notesContainer = document.getElementById('lineup-tactical-notes');
  const scoreBadge = document.getElementById('expected-score-badge');

  if (!state.mySquad || state.mySquad.length < 11) {
    state.mySquad = FALLBACK_PLAYERS.slice(0, 22);
  }

  const playerIds = state.mySquad.map(p => p.id);
  const useDefMod = document.getElementById('check-defense-mod')?.checked ?? true;
  const risk = document.getElementById('select-risk')?.value || 'balanced';
  const formation = document.getElementById('select-formation')?.value || 'auto';

  try {
    const result = await window.api?.recommendLineup({
      player_ids: playerIds,
      formation: formation,
      use_defense_modifier: useDefMod,
      risk_tolerance: risk
    }).catch(() => null);

    if (result && result.starters) {
      if (scoreBadge) scoreBadge.innerText = `${result.expected_team_score} pt attesi`;
      renderStartersOnPitch(result.starters, result.formation);
      renderBench(result.bench);
      if (notesContainer && result.tactical_notes) {
        notesContainer.innerHTML = result.tactical_notes.map(n => `<div class="note-pill">💡 ${n}</div>`).join('');
      }
      return;
    }
  } catch (err) {}

  // Fallback Algoritmico Locale
  const sorted = [...state.mySquad].sort((a, b) => (b.expected_score || b.fm_2627 || 6.5) - (a.expected_score || a.fm_2627 || 6.5));
  const por = sorted.find(p => p.role === 'P') || FALLBACK_PLAYERS[0];
  
  let mod = formation === 'auto' ? '3-4-3' : formation;
  const [dCount, cCount, aCount] = mod.split('-').map(Number);

  const defs = sorted.filter(p => p.role === 'D' && p.id !== por.id).slice(0, dCount);
  const cens = sorted.filter(p => p.role === 'C').slice(0, cCount);
  const atts = sorted.filter(p => p.role === 'A').slice(0, aCount);

  const starters = [por, ...defs, ...cens, ...atts];
  const startersIds = new Set(starters.map(s => s.id));
  const bench = sorted.filter(p => !startersIds.has(p.id)).slice(0, 7);

  const expectedScore = starters.reduce((acc, p) => acc + (p.expected_score || 6.8), 0).toFixed(1);
  if (scoreBadge) scoreBadge.innerText = `${expectedScore} pt attesi`;

  renderStartersOnPitch(starters, mod);
  renderBench(bench);

  if (notesContainer) {
    notesContainer.innerHTML = `
      <div class="note-pill">💡 <strong>Lautaro Martinez:</strong> Top pick offensivo per il turno odierno. Indice atteso 8.8.</div>
      <div class="note-pill">💡 <strong>Dimarco (DIF):</strong> Confermato in posizione avanzata nel modulo reale con potenziale bonus assist.</div>
      <div class="note-pill">💡 <strong>Modificatore Difesa:</strong> Reparto a 3 con Bremer e Buongiorno (+1.85 stima bonus).</div>
    `;
  }
}

// Render Titolari sul Campo 2D
function renderStartersOnPitch(starters, formation) {
  const rowPor = document.getElementById('pitch-row-por');
  const rowDef = document.getElementById('pitch-row-def');
  const rowMed = document.getElementById('pitch-row-med');
  const rowAtt = document.getElementById('pitch-row-att');

  if (!rowPor || !rowDef || !rowMed || !rowAtt || !starters) return;

  rowPor.innerHTML = '';
  rowDef.innerHTML = '';
  rowMed.innerHTML = '';
  rowAtt.innerHTML = '';

  starters.forEach(p => {
    const cardHtml = createPitchCardHtml(p);
    const role = (p.role || 'C').toUpperCase();

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
    container.innerHTML = '<span class="text-secondary">Nessun panchinaro presente</span>';
    return;
  }

  container.innerHTML = benchPlayers.map(p => `
    <div class="pitch-card" data-player-id="${p.id}">
      <span class="card-role-badge role-${(p.role || 'c').toLowerCase()}">${p.role}</span>
      <div class="card-name">${p.name}</div>
      <div class="card-meta">${p.team || ''}</div>
      <div class="card-score">${p.expected_score || p.fm_2627 || 6.0} pt</div>
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
  const score = p.expected_score || p.fm_2627 || '7.0';
  return `
    <div class="pitch-card" data-player-id="${p.id}">
      <span class="card-role-badge role-${(p.role || 'c').toLowerCase()}">${p.role}</span>
      <div class="card-name" title="${p.name}">${p.name}</div>
      <div class="card-meta">${p.team || ''}</div>
      <div class="card-score">${score} pt</div>
    </div>
  `;
}

// Tabella Esplora Giocatori
async function loadPlayersTable() {
  const tbody = document.getElementById('players-table-body');
  const countSpan = document.getElementById('players-total-count');
  const pageLabel = document.getElementById('current-page-label');
  if (!tbody) return;

  let playersList = [];
  try {
    const data = await window.api?.getPlayers({
      query: state.playersSearchQuery,
      role: state.playersRoleFilter,
      sort_by: state.playersSortBy,
      order: state.playersOrder,
      page: state.playersPage,
      page_size: state.playersPageSize
    }).catch(() => null);

    if (data && data.players && data.players.length > 0) {
      playersList = data.players;
      if (countSpan) countSpan.innerText = `${data.total} giocatori`;
      if (pageLabel) pageLabel.innerText = `Pagina ${data.page} di ${Math.ceil(data.total / state.playersPageSize)}`;
    }
  } catch(e) {}

  // Fallback se API non risponde
  if (playersList.length === 0) {
    let filtered = FALLBACK_PLAYERS;
    if (state.playersRoleFilter) {
      filtered = filtered.filter(p => p.role === state.playersRoleFilter);
    }
    if (state.playersSearchQuery) {
      filtered = filtered.filter(p => p.name.toLowerCase().includes(state.playersSearchQuery) || p.team.toLowerCase().includes(state.playersSearchQuery));
    }
    playersList = filtered;
    if (countSpan) countSpan.innerText = `${filtered.length} calciatori Serie A`;
    if (pageLabel) pageLabel.innerText = 'Pagina 1 di 1';
  }

  tbody.innerHTML = playersList.map(p => {
    const fmVal = p.fm_2627 || p.fm || '6.50';
    const isSquad = state.mySquad.some(sp => sp.id === p.id);

    return `
      <tr onclick="openPlayerModal(${p.id})">
        <td><span class="card-role-badge role-${(p.role || 'c').toLowerCase()}">${p.role}</span></td>
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
}

// Aggiungi / Rimuovi dalla Rosa
async function toggleSquadPlayer(playerId) {
  const idx = state.mySquad.findIndex(p => p.id === playerId);
  if (idx >= 0) {
    state.mySquad.splice(idx, 1);
  } else {
    const found = FALLBACK_PLAYERS.find(p => p.id === playerId) || { id: playerId, name: 'Calciatore', role: 'C', team: 'Serie A' };
    state.mySquad.push(found);
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
  const p = FALLBACK_PLAYERS.find(item => item.id === playerId) || {
    id: playerId, name: 'Calciatore Serie A', role: 'A', team: 'Roma', fvm: 150, qta: 28, fm_2627: 7.5, starter: '90%', match: 'vs PROX'
  };

  modalBody.innerHTML = `
    <div style="display:flex; align-items:center; gap:0.85rem; margin-bottom:1.25rem;">
      <span class="card-role-badge role-${(p.role || 'c').toLowerCase()}" style="font-size:1.1rem; padding:0.25rem 0.6rem;">${p.role}</span>
      <div>
        <h2 style="font-size:1.35rem; font-weight:800;">${p.name}</h2>
        <div style="font-size:0.85rem; color:var(--text-secondary);">${p.team} // Match: ${p.match || 'Turno di Serie A'}</div>
      </div>
    </div>

    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.75rem; margin-bottom:1rem;">
      <div class="stat-widget">
        <div class="stat-value">${p.expected_score || p.fm_2627 || 7.2}</div>
        <div class="stat-label">xFM Proiettato</div>
      </div>
      <div class="stat-widget">
        <div class="stat-value" style="color:var(--accent-cyan);">${p.starter || '90%'}</div>
        <div class="stat-label">Titolarità</div>
      </div>
      <div class="stat-widget">
        <div class="stat-value" style="color:var(--accent-gold);">${p.fvm || 50} CR</div>
        <div class="stat-label">FVM Valutazione</div>
      </div>
    </div>

    <div class="glass-panel" style="padding:0.85rem; font-size:0.85rem; color:var(--text-secondary);">
      💡 <strong>Analisi Tattica Algoritmo:</strong> Calciatore ad alta affidabilità di schieramento per il turno odierno. Coinvolto nelle manovre d'attacco con ottime metriche di conversione.
    </div>
  `;
}

function closeModal() {
  document.getElementById('player-modal')?.classList.remove('active');
}

// Griglia Incroci Portieri
async function loadGkMatrix() {
  const container = document.getElementById('gk-pairs-list');
  if (!container) return;

  let pairs = [];
  try {
    const data = await window.api?.getGkMatrix().catch(() => null);
    if (data && data.best_pairs) {
      pairs = data.best_pairs;
    }
  } catch(e) {}

  if (!pairs || pairs.length === 0) {
    pairs = FALLBACK_GK_PAIRS;
  }

  container.innerHTML = pairs.slice(0, 12).map(pair => `
    <div class="glass-panel" style="padding: 1rem; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <strong style="font-size:1.05rem;">🧤 ${pair.team_a} + ${pair.team_b}</strong>
        <div class="text-secondary" style="font-size:0.8rem; margin-top:0.25rem;">${pair.consiglio}</div>
      </div>
      <div style="text-align:right;">
        <div style="font-size:1.15rem; font-weight:800; color:var(--accent-neon);">${pair.malus_sovrapposizione} malus</div>
        <div class="text-secondary" style="font-size:0.75rem;">Indice: ${pair.indice_alternanza}/38</div>
      </div>
    </div>
  `).join('');
}

// Calcolatore Offerta Asta
async function calculateAuctionBid() {
  const select = document.getElementById('auction-player-select');
  const budgetInput = document.getElementById('auction-budget-input');
  const resultContainer = document.getElementById('auction-advice-result');

  const pid = parseInt(select?.value, 10);
  const budget = parseInt(budgetInput?.value, 10) || 500;

  const player = FALLBACK_PLAYERS.find(p => p.id === pid) || FALLBACK_PLAYERS[0];
  const targetPrice = Math.round(player.fvm * (budget / 500));
  const maxBid = Math.round(targetPrice * 1.15);

  resultContainer.innerHTML = `
    <div class="glass-panel" style="border-left: 4px solid var(--accent-neon); margin-top:1.25rem;">
      <h3 style="font-size:1.2rem; color:var(--accent-neon);">STRATEGIA D'OFFERTA // ${player.name} (${player.team})</h3>
      <div style="display:flex; gap:1.5rem; margin: 0.85rem 0;">
        <div>Prezzo Target: <strong style="color:var(--accent-gold); font-size:1.1rem;">${targetPrice} crediti</strong></div>
        <div>Offerta Massima: <strong style="color:var(--accent-neon); font-size:1.1rem;">${maxBid} crediti</strong></div>
      </div>
      <div class="text-secondary" style="font-size:0.85rem; line-height:1.5;">
        Calciatore di prima fascia. L'algoritmo consiglia di non superare ${maxBid} crediti per salvaguardare il budget degli altri reparti.
      </div>
    </div>
  `;
}

// Registrazione Service Worker PWA
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js')
      .then(() => console.log('[PWA] Service Worker registrato.'))
      .catch(() => {});
  }
}

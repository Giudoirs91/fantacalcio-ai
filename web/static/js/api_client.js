// ==============================================================================
// FANTA MASTER AI — API CLIENT (REST & Async)
// ==============================================================================

class ApiClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Errore HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  }

  // Giocatori
  async getPlayers({ query, role, team, min_qta, max_qta, min_fm, sort_by = 'fvm', order = 'desc', page = 1, page_size = 50 } = {}) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (role) params.append('role', role);
    if (team) params.append('team', team);
    if (min_qta !== undefined && min_qta !== null) params.append('min_qta', min_qta);
    if (max_qta !== undefined && max_qta !== null) params.append('max_qta', max_qta);
    if (min_fm !== undefined && min_fm !== null) params.append('min_fm', min_fm);
    params.append('sort_by', sort_by);
    params.append('order', order);
    params.append('page', page);
    params.append('page_size', page_size);

    return this.request(`/api/players?${params.toString()}`);
  }

  async getPlayerById(id) {
    return this.request(`/api/players/${id}`);
  }

  async getRolesSummary() {
    return this.request('/api/players/roles-summary');
  }

  async getTopFlop(roundNum) {
    const url = roundNum ? `/api/players/top-flop?round_num=${roundNum}` : '/api/players/top-flop';
    return this.request(url);
  }

  // Tattica & 20 Club Serie A
  async getTacticalTeams() {
    return this.request('/api/tactics/teams');
  }

  async getTacticalTeam(teamName) {
    return this.request(`/api/tactics/team/${encodeURIComponent(teamName)}`);
  }

  // Formazione & Lineup Optimizer
  async getSupportedModules() {
    return this.request('/api/lineup/supported-modules');
  }

  async recommendLineup({ player_ids, formation = 'auto', use_defense_modifier = true, risk_tolerance = 'balanced' }) {
    return this.request('/api/lineup/recommend', {
      method: 'POST',
      body: JSON.stringify({
        player_ids,
        formation,
        use_defense_modifier,
        risk_tolerance
      })
    });
  }

  // Statistiche & Incroci Portieri
  async getGkMatrix() {
    return this.request('/api/stats/gk-matrix');
  }

  async getTeamsStats() {
    return this.request('/api/stats/teams');
  }

  async getDatabaseOverview() {
    return this.request('/api/stats/database-overview');
  }

  // Asta Live
  async getAuctionState() {
    return this.request('/api/auction/state');
  }

  async updateAuctionState(state) {
    return this.request('/api/auction/state', {
      method: 'POST',
      body: JSON.stringify(state)
    });
  }

  async getBidAdvice({ player_id, current_budget, total_budget = 500, league_size = 8 }) {
    return this.request('/api/auction/bid-advice', {
      method: 'POST',
      body: JSON.stringify({
        player_id,
        current_budget,
        total_budget,
        league_size
      })
    });
  }

  // Health
  async getHealth() {
    return this.request('/api/health');
  }
}

// Istanza globale
window.api = new ApiClient();

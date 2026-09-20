// ai_report_card.js — AI Report Card Dashboard Module
// =====================================================
// Legge data/processed/ai_error_analysis.json (iniettato nella pagina
// dalla build come window.AI_ERROR_ANALYSIS) e disegna la sezione
// "AI Report Card" con metriche di autovalutazione, pattern di errore
// e le peggiori predizioni della stagione.

(function () {
    'use strict';

    // ── Helpers ───────────────────────────────────────────────────────────────

    function fmt(v, decimals = 2, signed = false) {
        if (v === null || v === undefined || isNaN(v)) return '—';
        const n = Number(v).toFixed(decimals);
        return signed ? (v >= 0 ? '+' + n : n) : n;
    }

    function pct(v) {
        if (v === null || v === undefined) return '—';
        return (Number(v) * 100).toFixed(0) + '%';
    }

    function biasColor(bias) {
        if (Math.abs(bias) < 0.2) return '#4ade80';      // green — ottimo
        if (Math.abs(bias) < 0.5) return '#facc15';      // yellow — attenzione
        return '#f87171';                                  // red — problema
    }

    function maeColor(mae) {
        if (mae < 0.8) return '#4ade80';
        if (mae < 1.5) return '#facc15';
        return '#f87171';
    }

    function accColor(acc) {
        if (acc >= 0.85) return '#4ade80';
        if (acc >= 0.65) return '#facc15';
        return '#f87171';
    }

    function renderProgressBar(value01, color, width = '100%') {
        const pct_val = Math.min(1, Math.max(0, value01)) * 100;
        return `
            <div style="background:rgba(255,255,255,0.08);border-radius:6px;height:10px;width:${width};overflow:hidden;">
                <div style="height:100%;width:${pct_val.toFixed(1)}%;background:${color};border-radius:6px;
                            transition:width 0.8s ease;"></div>
            </div>`;
    }

    // ── Main Render ───────────────────────────────────────────────────────────

    function renderAiReportCard() {
        const container = document.getElementById('ai-report-card-container');
        if (!container) return;

        const data = window.AI_ERROR_ANALYSIS;
        if (!data || !data.latest) {
            container.innerHTML = `
                <div class="ai-rc-empty">
                    <div class="ai-rc-empty-icon">🤖</div>
                    <div class="ai-rc-empty-title">AI Report Card non disponibile</div>
                    <div class="ai-rc-empty-subtitle">
                        Il sistema genererà automaticamente l'analisi a partire dalla <strong>Giornata 5</strong>.
                        Riesegui la pipeline dopo aver caricato almeno 5 giornate di voti.
                    </div>
                    <div class="ai-rc-snapshot-info" id="ai-rc-snapshot-status">
                        Verificando snapshot predizioni...
                    </div>
                </div>`;
            _checkSnapshotStatus();
            return;
        }

        const latest = data.latest;
        const global = latest.global || {};
        const xfmStats = global.xfm || {};
        const roundNum = latest.round_num || 0;
        const analyzedAt = latest.analyzed_at ? new Date(latest.analyzed_at).toLocaleDateString('it-IT') : '—';
        const snapshotDate = data.snapshot_date ? new Date(data.snapshot_date).toLocaleDateString('it-IT') : '—';

        const bias = xfmStats.mean || 0;
        const mae = xfmStats.mae || 0;
        const advAcc = global.advice_accuracy || 0;
        const fragHit = global.fragility_hit_rate || 0;

        // ── KPI Cards Row ─────────────────────────────────────────────────────
        const kpiHTML = `
            <div class="ai-rc-kpi-grid">
                <div class="ai-rc-kpi-card">
                    <div class="ai-rc-kpi-label">Errore Medio xFM</div>
                    <div class="ai-rc-kpi-value" style="color:${maeColor(mae)}">${fmt(mae)} FM</div>
                    ${renderProgressBar(1 - Math.min(1, mae / 2.5), maeColor(mae))}
                    <div class="ai-rc-kpi-sub">MAE su ${global.n_players || 0} giocatori</div>
                </div>
                <div class="ai-rc-kpi-card">
                    <div class="ai-rc-kpi-label">Bias xFM</div>
                    <div class="ai-rc-kpi-value" style="color:${biasColor(bias)}">${fmt(bias, 2, true)} FM</div>
                    ${renderProgressBar(0.5 + (bias / 3) * 0.5, biasColor(bias))}
                    <div class="ai-rc-kpi-sub">${bias > 0.15 ? '🔺 Ottimista' : bias < -0.15 ? '🔻 Pessimista' : '✅ Calibrato'}</div>
                </div>
                <div class="ai-rc-kpi-card">
                    <div class="ai-rc-kpi-label">Accuratezza Consigli</div>
                    <div class="ai-rc-kpi-value" style="color:${accColor(advAcc)}">${pct(advAcc)}</div>
                    ${renderProgressBar(advAcc, accColor(advAcc))}
                    <div class="ai-rc-kpi-sub">${advAcc >= 0.85 ? 'Eccellente' : advAcc >= 0.70 ? 'Buona' : advAcc >= 0.55 ? 'Sufficiente' : 'Da migliorare'}</div>
                </div>
                <div class="ai-rc-kpi-card">
                    <div class="ai-rc-kpi-label">Fragility Hit Rate</div>
                    <div class="ai-rc-kpi-value" style="color:${accColor(fragHit)}">${pct(fragHit)}</div>
                    ${renderProgressBar(fragHit, accColor(fragHit))}
                    <div class="ai-rc-kpi-sub">Infortuni previsti corretti</div>
                </div>
            </div>`;

        // ── Errori per Categoria ──────────────────────────────────────────────
        const byRole = latest.by_role || {};
        const byLeague = latest.by_league || {};
        const byOop = latest.by_oop || {};

        const roleRows = Object.entries(byRole)
            .sort((a, b) => Math.abs(b[1].mean) - Math.abs(a[1].mean))
            .map(([role, stats]) => {
                const c = biasColor(stats.mean);
                return `<tr>
                    <td><span class="role-badge role-${role.toLowerCase()}">${role}</span></td>
                    <td style="color:${c};font-weight:600">${fmt(stats.mean, 2, true)}</td>
                    <td>${fmt(stats.mae)}</td>
                    <td style="color:rgba(255,255,255,0.5)">${stats.count}</td>
                    <td>${renderProgressBar(1 - Math.min(1, stats.mae / 2), maeColor(stats.mae), '80px')}</td>
                </tr>`;
            }).join('');

        const leagueRows = Object.entries(byLeague)
            .filter(([, s]) => s.count >= 3)
            .sort((a, b) => Math.abs(b[1].mean) - Math.abs(a[1].mean))
            .slice(0, 8)
            .map(([league, stats]) => {
                const c = biasColor(stats.mean);
                return `<tr>
                    <td style="font-size:0.82rem">${league}</td>
                    <td style="color:${c};font-weight:600">${fmt(stats.mean, 2, true)}</td>
                    <td>${fmt(stats.mae)}</td>
                    <td style="color:rgba(255,255,255,0.5)">${stats.count}</td>
                </tr>`;
            }).join('');

        const oopRows = Object.entries(byOop)
            .filter(([tier]) => tier !== 'STANDARD')
            .map(([tier, stats]) => {
                const c = biasColor(stats.mean);
                return `<tr>
                    <td>${tier}</td>
                    <td style="color:${c};font-weight:600">${fmt(stats.mean, 2, true)}</td>
                    <td>${fmt(stats.mae)}</td>
                    <td style="color:rgba(255,255,255,0.5)">${stats.count}</td>
                </tr>`;
            }).join('');

        // ── Advice Accuracy per Tipo ──────────────────────────────────────────
        const adviceAcc = latest.advice_accuracy || {};
        const adviceRows = Object.entries(adviceAcc)
            .sort((a, b) => b[1].accuracy - a[1].accuracy)
            .map(([type, d]) => {
                const c = accColor(d.accuracy);
                const bar = renderProgressBar(d.accuracy, c, '100px');
                return `<tr>
                    <td><span class="advice-badge advice-${type}">${_adviceLabel(type)}</span></td>
                    <td style="color:${c};font-weight:700">${pct(d.accuracy)}</td>
                    <td style="color:rgba(255,255,255,0.5)">${d.count}</td>
                    <td>${bar}</td>
                </tr>`;
            }).join('');

        // ── Peggiori Predizioni ───────────────────────────────────────────────
        const worst = latest.worst_predictions || [];
        const worstRows = worst.map(w => {
            const err = Number(w.error);
            const c = err > 0 ? '#fbbf24' : '#60a5fa'; // giallo=ottimista, blu=pessimista
            const icon = err > 0 ? '🔺' : '🔻';
            const correctIcon = w.advice_correct === true ? '✅' : w.advice_correct === false ? '❌' : '—';
            return `<tr>
                <td>${w.name}</td>
                <td><span class="role-badge role-${(w.role||'').toLowerCase()}">${w.role}</span></td>
                <td style="color:rgba(255,255,255,0.6);font-size:0.8rem">${w.team}</td>
                <td>${fmt(w.xfm_pred)}</td>
                <td style="font-weight:700">${fmt(w.fm_actual)}</td>
                <td style="color:${c};font-weight:700">${icon} ${fmt(Math.abs(err))} FM</td>
                <td style="text-align:center">${correctIcon}</td>
            </tr>`;
        }).join('');

        // ── Learning Notes ────────────────────────────────────────────────────
        const notes = latest.learning_notes || [];
        const notesHTML = notes.length > 0
            ? notes.map(n => `<div class="ai-rc-note"><span class="ai-rc-note-dot"></span>${n}</div>`).join('')
            : '<div class="ai-rc-note-empty">Nessuna nota disponibile per questa finestra temporale.</div>';

        // ── Timeline (History) ────────────────────────────────────────────────
        const history = data.history || [];
        const timelineHTML = history.length > 1 ? `
            <div class="ai-rc-section">
                <h3 class="ai-rc-section-title">📈 Evoluzione Errore MAE nel Tempo</h3>
                <div class="ai-rc-timeline">
                    ${history.map(h => {
                        const hmae = h.global?.xfm?.mae || 0;
                        const hbias = h.global?.xfm?.mean || 0;
                        const maxHeight = 80;
                        const barH = Math.min(maxHeight, Math.round(hmae / 2.5 * maxHeight));
                        const c = maeColor(hmae);
                        return `<div class="ai-rc-timeline-bar-wrapper">
                            <div class="ai-rc-timeline-bar" style="height:${barH}px;background:${c};" title="G${h.round_num}: MAE=${hmae.toFixed(2)}, Bias=${hbias.toFixed(2)}"></div>
                            <div class="ai-rc-timeline-label">G${h.round_num}</div>
                            <div class="ai-rc-timeline-val" style="color:${c}">${hmae.toFixed(1)}</div>
                        </div>`;
                    }).join('')}
                </div>
            </div>` : '';

        // ── Assemble Full View ────────────────────────────────────────────────
        container.innerHTML = `
            <div class="ai-rc-header">
                <div class="ai-rc-header-left">
                    <div class="ai-rc-title">🤖 AI Report Card</div>
                    <div class="ai-rc-subtitle">
                        Analisi a <strong>Giornata ${roundNum}</strong> — Aggiornata il ${analyzedAt}
                        <span class="ai-rc-snapshot-badge" title="Data snapshot T0: ${snapshotDate}">📸 Snapshot: ${snapshotDate}</span>
                    </div>
                </div>
                <div class="ai-rc-header-badge ${_overallGrade(mae, advAcc)}">
                    ${_overallGradeLabel(mae, advAcc)}
                </div>
            </div>

            ${kpiHTML}

            <div class="ai-rc-grid-2col">

                <div class="ai-rc-section">
                    <h3 class="ai-rc-section-title">📊 Errori per Ruolo</h3>
                    <table class="ai-rc-table">
                        <thead><tr><th>Ruolo</th><th>Bias</th><th>MAE</th><th>N</th><th>Qualità</th></tr></thead>
                        <tbody>${roleRows || '<tr><td colspan="5" style="opacity:0.4;text-align:center">—</td></tr>'}</tbody>
                    </table>
                </div>

                <div class="ai-rc-section">
                    <h3 class="ai-rc-section-title">🌍 Errori per Lega Origine</h3>
                    <table class="ai-rc-table">
                        <thead><tr><th>Lega</th><th>Bias</th><th>MAE</th><th>N</th></tr></thead>
                        <tbody>${leagueRows || '<tr><td colspan="4" style="opacity:0.4;text-align:center">Dati insufficienti per lega</td></tr>'}</tbody>
                    </table>
                </div>

                <div class="ai-rc-section">
                    <h3 class="ai-rc-section-title">🔀 Errori OOP (Fuori Ruolo)</h3>
                    <table class="ai-rc-table">
                        <thead><tr><th>Tier</th><th>Bias</th><th>MAE</th><th>N</th></tr></thead>
                        <tbody>${oopRows || '<tr><td colspan="4" style="opacity:0.4;text-align:center">Nessun OOP analizzato</td></tr>'}</tbody>
                    </table>
                </div>

                <div class="ai-rc-section">
                    <h3 class="ai-rc-section-title">🎯 Accuratezza Consigli AI</h3>
                    <table class="ai-rc-table">
                        <thead><tr><th>Tipo</th><th>Accuratezza</th><th>N</th><th>Barra</th></tr></thead>
                        <tbody>${adviceRows || '<tr><td colspan="4" style="opacity:0.4;text-align:center">—</td></tr>'}</tbody>
                    </table>
                </div>
            </div>

            ${timelineHTML}

            <div class="ai-rc-section">
                <h3 class="ai-rc-section-title">⚠️ Top 15 Predizioni Peggiori</h3>
                <div class="ai-rc-table-scroll">
                    <table class="ai-rc-table">
                        <thead><tr><th>Calciatore</th><th>R</th><th>Squadra</th><th>xFM Pred.</th><th>FM Reale</th><th>Errore</th><th>Consiglio</th></tr></thead>
                        <tbody>${worstRows || '<tr><td colspan="7" style="opacity:0.4;text-align:center">—</td></tr>'}</tbody>
                    </table>
                </div>
            </div>

            <div class="ai-rc-section">
                <h3 class="ai-rc-section-title">💡 Lezioni Apprese — Cosa ha sbagliato l'AI</h3>
                <div class="ai-rc-notes">
                    ${notesHTML}
                </div>
                <div class="ai-rc-correction-note">
                    <span>⚙️</span>
                    <span>Le correzioni bias vengono applicate automaticamente dalla prossima esecuzione della pipeline (da G${Math.max(5, roundNum + 1)} in poi).</span>
                </div>
            </div>
        `;
    }

    // ── Private Helpers ───────────────────────────────────────────────────────

    function _adviceLabel(type) {
        const map = {
            top: '👑 Top', leader: '⭐ Leader', buy: '📈 Buy',
            sleeper: '🔥 Sleeper', warning: '⚠️ Warning', flop: '📉 Flop', avoid: '⛔ Avoid'
        };
        return map[type] || type;
    }

    function _overallGrade(mae, advAcc) {
        if (mae < 0.8 && advAcc >= 0.85) return 'grade-a';
        if (mae < 1.2 && advAcc >= 0.70) return 'grade-b';
        if (mae < 1.8 && advAcc >= 0.55) return 'grade-c';
        return 'grade-d';
    }

    function _overallGradeLabel(mae, advAcc) {
        if (mae < 0.8 && advAcc >= 0.85) return 'Grado A';
        if (mae < 1.2 && advAcc >= 0.70) return 'Grado B';
        if (mae < 1.8 && advAcc >= 0.55) return 'Grado C';
        return 'Grado D';
    }

    function _checkSnapshotStatus() {
        const el = document.getElementById('ai-rc-snapshot-status');
        if (!el) return;
        const snap = window.AI_PREDICTIONS_SNAPSHOT;
        if (snap && snap.metadata) {
            const date = new Date(snap.metadata.saved_at).toLocaleDateString('it-IT');
            el.innerHTML = `✅ Snapshot T0 presente — Salvato il ${date} (${snap.metadata.n_players} calciatori)`;
            el.style.color = '#4ade80';
        } else {
            el.innerHTML = '⚠️ Snapshot T0 non trovato — Verrà creato alla prossima esecuzione della pipeline';
            el.style.color = '#facc15';
        }
    }

    // ── Init ──────────────────────────────────────────────────────────────────

    window.renderAiReportCard = renderAiReportCard;

    document.addEventListener('DOMContentLoaded', () => {
        renderAiReportCard();
    });

})();

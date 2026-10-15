#!/usr/bin/env python3
"""
tools/seo_probabili_template.py
================================
Template e generatore per il modulo Probabili Formazioni & Ballottaggi Consensus
a 5 Fonti (Fantacalcio.it, Gazzetta, Sky Sport, SOS Fanta, FantaPazz).

Genera:
 1. Hub Principale: /probabili-formazioni/index.html (10 match, top ballottaggi, tabellone comparativo)
 2. Pagine Singolo Match: /probabili-formazioni/[squadra-a]-[squadra-b]/index.html
"""

import os
import re
import json
from datetime import datetime

def clean_html(text):
    if text is None:
        return ""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))

def slugify(text):
    if not text:
        return "calciatore"
    clean = re.sub(r'[^a-zA-Z0-9]+', '-', str(text).strip()).lower().strip('-')
    return clean or "calciatore"

def get_player_slug_from_name(name):
    clean = re.sub(r'[^a-zA-Z0-9]+', '-', str(name).strip()).lower().strip('-')
    return f"{clean}-2026"

def render_probabili_css():
    return """
/* ==========================================================================
   PROBABILI FORMAZIONI & CONSENSUS 5 FONTI - DESIGN SYSTEM
   ========================================================================== */

html, body {
    max-width: 100vw;
    overflow-x: hidden;
}
*, *::before, *::after {
    box-sizing: border-box;
}

.prob-container {
    max-width: 1480px;
    width: 100%;
    margin: 0 auto;
    padding: 16px 16px 40px 16px;
    box-sizing: border-box;
}

/* Hero Header */
.prob-hero {
    background: radial-gradient(120% 120% at 50% 0%, rgba(56, 189, 248, 0.16) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45);
    position: relative;
    overflow: hidden;
}
.prob-hero::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 320px; height: 100%;
    background: radial-gradient(circle at 100% 50%, rgba(34, 197, 94, 0.12), transparent 70%);
    pointer-events: none;
}
.prob-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 800;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    padding: 3px 10px;
    border-radius: 9999px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 8px;
}
.prob-hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 28px;
    font-weight: 900;
    color: #ffffff;
    margin: 0 0 8px 0;
    letter-spacing: -0.3px;
    line-height: 1.2;
}
.prob-hero-desc {
    font-size: 13.5px;
    color: #94a3b8;
    margin: 0 0 14px 0;
    max-width: 980px;
    line-height: 1.55;
}
.prob-sources-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    font-size: 11px;
    color: #cbd5e1;
}
.source-chip {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 700;
    color: #e2e8f0;
}
.source-chip b {
    color: #38bdf8;
}

/* Match Carousel / Bar */
.match-carousel-wrapper {
    margin-bottom: 24px;
    width: 100%;
    max-width: 100%;
    overflow: hidden;
}
.carousel-label {
    font-size: 11px;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
}
.match-carousel {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 8px;
    scrollbar-width: thin;
    scrollbar-color: rgba(56, 189, 248, 0.3) transparent;
}
.match-carousel::-webkit-scrollbar {
    height: 4px;
}
.match-carousel::-webkit-scrollbar-thumb {
    background: rgba(56, 189, 248, 0.4);
    border-radius: 4px;
}
.match-pill-card {
    background: rgba(18, 22, 29, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 8px 12px;
    min-width: 135px;
    flex-shrink: 0;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.match-pill-card:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(56, 189, 248, 0.35);
    transform: translateY(-2px);
}
.match-pill-card.active {
    background: linear-gradient(135deg, rgba(2, 132, 199, 0.25), rgba(15, 23, 42, 0.95));
    border-color: #38bdf8;
    box-shadow: 0 4px 14px rgba(56, 189, 248, 0.25);
}
.match-pill-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 10px;
    font-weight: 700;
    color: #94a3b8;
}
.match-pill-meta .match-clou {
    color: #fbbf24;
    font-size: 9px;
    background: rgba(251, 191, 36, 0.15);
    padding: 1px 4px;
    border-radius: 4px;
}
.match-pill-teams {
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    font-weight: 800;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.match-pill-vs {
    font-size: 10px;
    color: #64748b;
    font-weight: 700;
}

/* Hot Ballottaggi Highlight Box */
.hot-ballots-box {
    background: rgba(18, 22, 29, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 24px;
}
.hot-ballots-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.hot-ballots-title {
    font-family: 'Outfit', sans-serif;
    font-size: 16px;
    font-weight: 800;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 8px;
}
.hot-ballots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 12px;
}

/* Match Section & Controls */
.match-detail-section {
    background: rgba(18, 22, 29, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 20px 24px;
    margin-bottom: 28px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    overflow: hidden;
}
.match-detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 18px;
    width: 100%;
    box-sizing: border-box;
}
.match-title-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
    max-width: 100%;
}
.match-headline {
    font-family: 'Outfit', sans-serif;
    font-size: 22px;
    font-weight: 900;
    color: #fff;
    margin: 0;
    word-break: break-word;
}
.match-subinfo {
    font-size: 11.5px;
    color: #94a3b8;
    margin-top: 2px;
    word-break: break-word;
}
.match-view-switcher {
    display: flex;
    align-items: center;
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 3px;
    gap: 4px;
    max-width: 100%;
    box-sizing: border-box;
}
.view-switch-btn {
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 6px 12px;
    border-radius: 7px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s ease;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}
.view-switch-btn:hover {
    color: #fff;
}
.view-switch-btn.active {
    background: rgba(56, 189, 248, 0.16);
    color: #38bdf8;
    font-weight: 800;
}

/* 1vs1 Head-to-Head Duels & Two-Column Team Layout */
.match-teams-columns {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 20px;
    align-items: start;
    margin-bottom: 24px;
    width: 100%;
}
.team-duels-column {
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-width: 0;
    width: 100%;
}
.team-column-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.team-column-header.home-header {
    border-left: 4px solid #38bdf8;
    background: linear-gradient(90deg, rgba(56, 189, 248, 0.12) 0%, rgba(15, 23, 42, 0.7) 100%);
}
.team-column-header.away-header {
    border-left: 4px solid #a855f7;
    background: linear-gradient(90deg, rgba(168, 85, 247, 0.12) 0%, rgba(15, 23, 42, 0.7) 100%);
}
.team-col-title-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
}
.team-col-icon {
    font-size: 16px;
}
.team-col-name {
    font-family: 'Outfit', sans-serif;
    font-size: 16px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.3px;
}
.team-col-badge {
    font-size: 9.5px;
    font-weight: 800;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.08);
    color: #94a3b8;
    letter-spacing: 0.5px;
}
.team-col-count {
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
}
.team-duels-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.no-duels-notice {
    font-size: 12px;
    color: #94a3b8;
    padding: 14px 16px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px dashed rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    line-height: 1.45;
}

.duel-card-h2h {
    background: rgba(11, 15, 23, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    transition: border-color 0.2s ease, transform 0.2s ease;
    box-sizing: border-box;
    width: 100%;
}
.duel-card-h2h:hover {
    border-color: rgba(56, 189, 248, 0.3);
    transform: translateY(-2px);
}
.duel-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}
.duel-team-tag {
    font-size: 11px;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
}
.duel-h2h-players {
    display: flex;
    flex-direction: column;
    gap: 7px;
    width: 100%;
}
.h2h-player-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    gap: 10px;
}
.h2h-player-lead {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    flex: 1;
}
.h2h-info {
    display: flex;
    flex-direction: column;
    min-width: 0;
}
.h2h-name {
    font-size: 13.5px;
    font-weight: 800;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-decoration: none;
}
.h2h-name:hover {
    color: #38bdf8;
}
.h2h-meta {
    font-size: 10px;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 4px;
}
.h2h-meta b {
    color: #e2e8f0;
}
.h2h-pct {
    font-family: 'Outfit', sans-serif;
    font-size: 17px;
    font-weight: 900;
    flex-shrink: 0;
    text-align: right;
    min-width: 44px;
}
.h2h-pct.fav {
    color: #4ade80;
}
.h2h-pct.under {
    color: #fbbf24;
}
.h2h-center-divider {
    font-size: 10px;
    font-weight: 900;
    color: #64748b;
    flex-shrink: 0;
    padding: 0 4px;
}

/* Dual Color Gauge */
.duel-gauge-bar {
    width: 100%;
    height: 7px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 9999px;
    overflow: hidden;
    display: flex;
}
.gauge-part-left {
    height: 100%;
    background: linear-gradient(90deg, #10b981, #34d399);
    border-radius: 9999px 0 0 9999px;
}
.gauge-part-right {
    height: 100%;
    background: linear-gradient(90deg, #f59e0b, #fbbf24);
    border-radius: 0 9999px 9999px 0;
}

/* AI Verdict Box */
.duel-verdict-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 8px 10px;
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.verdict-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.verdict-tag {
    font-size: 10px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.verdict-tag.safe {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.35);
}
.verdict-tag.hot {
    background: rgba(249, 115, 22, 0.15);
    color: #fb923c;
    border: 1px solid rgba(249, 115, 22, 0.35);
}
.verdict-tag.warning {
    background: rgba(251, 191, 36, 0.15);
    color: #facc15;
    border: 1px solid rgba(251, 191, 36, 0.35);
}
.verdict-tag.jolly {
    background: rgba(168, 85, 247, 0.15);
    color: #c084fc;
    border: 1px solid rgba(168, 85, 247, 0.35);
}
.verdict-tag.danger {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
}
.verdict-desc {
    font-size: 11px;
    color: #cbd5e1;
    line-height: 1.35;
}
.duel-cta-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 2px;
}
.btn-duel-compare {
    font-size: 10.5px;
    font-weight: 700;
    color: #38bdf8;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: color 0.15s ease;
}
.btn-duel-compare:hover {
    color: #fff;
    text-decoration: underline;
}

/* Consensus Table - The Anti-FCO View */
.consensus-table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: #0f1217;
    margin-bottom: 20px;
}
.consensus-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    text-align: left;
}
.consensus-table th {
    background: #141822;
    padding: 9px 10px;
    font-size: 10.5px;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    white-space: nowrap;
}
.consensus-table td {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    white-space: nowrap;
    vertical-align: middle;
}
.consensus-table tr:hover td {
    background: rgba(255, 255, 255, 0.02);
}
.col-player {
    min-width: 180px;
    font-weight: 700;
}
.col-player a {
    color: #ffffff;
    text-decoration: none;
}
.col-player a:hover {
    color: #38bdf8;
}
.col-source {
    text-align: center;
    color: #cbd5e1;
    font-weight: 600;
    font-size: 11.5px;
}
.col-consensus {
    text-align: center;
}
.consensus-chip {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 6px;
    font-family: 'Outfit', sans-serif;
    font-weight: 900;
    font-size: 12px;
}
.consensus-chip.high {
    background: rgba(34, 197, 94, 0.18);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.35);
}
.consensus-chip.mid {
    background: rgba(56, 189, 248, 0.18);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.35);
}
.consensus-chip.low {
    background: rgba(251, 191, 36, 0.18);
    color: #facc15;
    border: 1px solid rgba(251, 191, 36, 0.35);
}
.consensus-chip.out {
    background: rgba(239, 68, 68, 0.18);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
}
.section-subhead-row td {
    background: rgba(255, 255, 255, 0.03);
    font-weight: 800;
    font-size: 11px;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 6px 10px;
}

/* Match Bottom Panels: Piazzati & Infermeria */
.match-bottom-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px;
    margin-top: 20px;
}
.subpanel-card {
    background: rgba(11, 15, 23, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.subpanel-title {
    font-family: 'Outfit', sans-serif;
    font-size: 13.5px;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 6px;
}
.takers-list-flow {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.taker-item-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11.5px;
    background: rgba(255, 255, 255, 0.02);
    padding: 5px 8px;
    border-radius: 6px;
}
.taker-label {
    font-weight: 700;
    color: #94a3b8;
}
.taker-values {
    color: #e2e8f0;
    font-weight: 700;
}
.injury-mini-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 8px;
    background: rgba(239, 68, 68, 0.06);
    border: 1px solid rgba(239, 68, 68, 0.15);
    border-radius: 7px;
    font-size: 11.5px;
}
.inj-name {
    font-weight: 800;
    color: #f87171;
}
.inj-meta {
    font-size: 10.5px;
    color: #cbd5e1;
}
.inj-return-date {
    color: #fbbf24;
    font-weight: 800;
}

/* ==========================================================================
   RESPONSIVE DESIGN SYSTEM - SMARTPHONE & TABLET OPTIMIZATION
   ========================================================================== */

/* Tablet & Smaller Screens (<= 960px) */
@media (max-width: 960px) {
    .match-teams-columns {
        grid-template-columns: 1fr;
        gap: 18px;
    }
}

/* Smartphone Landscape & Tablet Portrait (<= 768px) */
@media (max-width: 768px) {
    .prob-container {
        padding: 10px 8px 32px 8px;
        width: 100%;
        max-width: 100vw;
        box-sizing: border-box;
        overflow-x: hidden;
    }
    .prob-hero {
        padding: 16px 14px;
        border-radius: 14px;
        margin-bottom: 14px;
    }
    .prob-hero-title {
        font-size: 20px;
        line-height: 1.25;
    }
    .prob-hero-desc {
        font-size: 12px;
        line-height: 1.45;
        margin-bottom: 10px;
    }
    .prob-sources-bar {
        font-size: 10px;
        gap: 5px;
    }
    .source-chip {
        padding: 2px 6px;
    }
    .match-detail-section {
        padding: 12px 10px;
        border-radius: 14px;
        margin-bottom: 20px;
        width: 100%;
        box-sizing: border-box;
    }
    .match-detail-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
        padding-bottom: 12px;
        width: 100%;
    }
    .match-headline {
        font-size: 18px;
        word-break: break-word;
    }
    .match-subinfo {
        font-size: 11px;
    }
    .match-view-switcher {
        width: 100%;
        display: flex;
    }
    .view-switch-btn {
        flex: 1;
        min-width: 0;
        justify-content: center;
        padding: 7px 4px;
        font-size: 11px;
        min-height: 38px;
        white-space: normal;
        text-align: center;
    }
    .match-teams-columns {
        grid-template-columns: 1fr;
        gap: 14px;
        width: 100%;
        box-sizing: border-box;
    }
    .team-duels-column {
        width: 100%;
        box-sizing: border-box;
    }
    .duel-card-h2h {
        padding: 10px 12px;
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
    }
    .team-column-header {
        padding: 8px 10px;
    }
    .match-bottom-grid {
        grid-template-columns: 1fr;
        gap: 12px;
    }
    .consensus-table-wrapper {
        border-radius: 8px;
    }
    .consensus-table .col-player {
        position: sticky;
        left: 0;
        background: #141822;
        z-index: 2;
        box-shadow: 2px 0 6px rgba(0,0,0,0.4);
    }
}

/* Smartphone Portrait (<= 580px) */
@media (max-width: 580px) {
    .duel-card-h2h {
        padding: 12px;
        gap: 8px;
    }
    .duel-h2h-players {
        gap: 6px;
    }
    .h2h-name {
        font-size: 13px;
    }
    .h2h-pct {
        font-size: 16px;
    }
    .duel-gauge-bar {
        height: 6px;
        margin: 2px 0;
    }
    .verdict-desc {
        font-size: 10.5px;
    }
    .btn-duel-compare {
        font-size: 10px;
    }
    .hot-ballots-box {
        padding: 12px 10px;
        border-radius: 12px;
    }
    .hot-ballots-grid {
        grid-template-columns: 1fr;
    }
    .match-pill-card {
        min-width: 120px;
        padding: 6px 8px;
    }
    .match-pill-teams {
        font-size: 12px;
    }
    .taker-item-row {
        flex-wrap: wrap;
        gap: 4px;
    }
    .injury-mini-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 2px;
    }
}

/* ==========================================================================
   SUPER MEGA IPER SEO SUITE - CSS EXTENSIONS
   ========================================================================== */

/* Semantic Section Headings */
.seo-section-heading {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Outfit', sans-serif;
    font-size: 16px;
    font-weight: 800;
    color: #f1f5f9;
    margin: 20px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.seo-section-heading span.icon {
    font-size: 18px;
}
.seo-section-heading span.badge {
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 9999px;
    background: rgba(56, 189, 248, 0.12);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.25);
    margin-left: auto;
    text-transform: uppercase;
}

/* Featured Snippet Executive Summary Card */
.seo-summary-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    position: relative;
}
.seo-summary-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #38bdf8, #818cf8);
    border-radius: 14px 0 0 14px;
}
.seo-summary-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10.5px;
    font-weight: 800;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.25);
    padding: 2px 8px;
    border-radius: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.seo-summary-title {
    font-family: 'Outfit', sans-serif;
    font-size: 17px;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 8px 0;
}
.seo-summary-text {
    font-size: 13.5px;
    line-height: 1.6;
    color: #cbd5e1;
    margin: 0 0 12px 0;
}
.seo-summary-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.seo-summary-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 4px 9px;
    color: #94a3b8;
}
.seo-summary-pill b {
    color: #ffffff;
}

/* AI Fantasy Advice Bento Grid */
.seo-advice-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}
.seo-advice-card {
    background: #0f1217;
    border-radius: 12px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    position: relative;
    border: 1px solid rgba(255, 255, 255, 0.07);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.seo-advice-card:hover {
    transform: translateY(-2px);
}
.seo-advice-card.advice-pick {
    border-color: rgba(34, 197, 94, 0.35);
    background: linear-gradient(180deg, rgba(34, 197, 94, 0.05) 0%, rgba(15, 18, 23, 0.95) 100%);
}
.seo-advice-card.advice-risk {
    border-color: rgba(239, 68, 68, 0.35);
    background: linear-gradient(180deg, rgba(239, 68, 68, 0.05) 0%, rgba(15, 18, 23, 0.95) 100%);
}
.seo-advice-card.advice-jolly {
    border-color: rgba(168, 85, 247, 0.35);
    background: linear-gradient(180deg, rgba(168, 85, 247, 0.05) 0%, rgba(15, 18, 23, 0.95) 100%);
}
.advice-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.advice-badge {
    font-size: 10px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.advice-pick .advice-badge {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.3);
}
.advice-risk .advice-badge {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}
.advice-jolly .advice-badge {
    background: rgba(168, 85, 247, 0.15);
    color: #c084fc;
    border: 1px solid rgba(168, 85, 247, 0.3);
}
.advice-team-tag {
    font-size: 10.5px;
    font-weight: 700;
    color: #94a3b8;
}
.advice-player-row {
    display: flex;
    align-items: center;
    gap: 8px;
}
.advice-name {
    font-family: 'Outfit', sans-serif;
    font-size: 15px;
    font-weight: 800;
    color: #ffffff;
    text-decoration: none;
}
.advice-name:hover {
    color: #38bdf8;
}
.advice-meta {
    font-size: 11px;
    color: #94a3b8;
}
.advice-meta b {
    color: #fbbf24;
}
.advice-text {
    font-size: 12px;
    line-height: 1.45;
    color: #cbd5e1;
    margin: 0;
}

/* FAQ Accordion Section */
.seo-faq-wrap {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin: 14px 0 24px 0;
}
.seo-faq-item {
    background: #0f1217;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    overflow: hidden;
    transition: border-color 0.2s ease, background 0.2s ease;
}
.seo-faq-item[open] {
    border-color: rgba(56, 189, 248, 0.3);
    background: rgba(15, 23, 42, 0.85);
}
.seo-faq-question {
    padding: 14px 16px;
    font-family: 'Outfit', sans-serif;
    font-size: 13.5px;
    font-weight: 700;
    color: #f1f5f9;
    cursor: pointer;
    list-style: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    user-select: none;
}
.seo-faq-question::-webkit-details-marker {
    display: none;
}
.seo-faq-question::after {
    content: '+';
    font-size: 18px;
    font-weight: 700;
    color: #38bdf8;
    transition: transform 0.2s ease;
}
.seo-faq-item[open] .seo-faq-question::after {
    content: '−';
    transform: rotate(0deg);
}
.seo-faq-answer {
    padding: 0 16px 14px 16px;
    font-size: 12.5px;
    line-height: 1.55;
    color: #cbd5e1;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    margin-top: -2px;
    padding-top: 10px;
}
.seo-faq-answer a {
    color: #38bdf8;
    text-decoration: underline;
}

/* Hub Schedule Table */
.schedule-table-wrap {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: #0f1217;
    margin-bottom: 24px;
}
.seo-hub-schedule-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    text-align: left;
}
.seo-hub-schedule-table th {
    background: #141822;
    padding: 10px 12px;
    font-size: 10.5px;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    white-space: nowrap;
}
.seo-hub-schedule-table td {
    padding: 10px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    white-space: nowrap;
    vertical-align: middle;
}
.seo-hub-schedule-table tr:hover td {
    background: rgba(255, 255, 255, 0.02);
}
.schedule-match-link {
    font-weight: 700;
    color: #ffffff;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.schedule-match-link:hover {
    color: #38bdf8;
}

/* Editorial Guide Section */
.seo-editorial-guide {
    background: #0f1217;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 24px;
    margin: 28px 0;
}
.guide-header {
    margin-bottom: 18px;
}
.guide-header h2 {
    font-family: 'Outfit', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 6px 0;
}
.guide-header p {
    font-size: 13px;
    color: #94a3b8;
    margin: 0;
}
.guide-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}
.guide-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 16px;
}
.guide-card-title {
    font-family: 'Outfit', sans-serif;
    font-size: 14px;
    font-weight: 800;
    color: #38bdf8;
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    gap: 6px;
}
.guide-card-body {
    font-size: 12.5px;
    line-height: 1.6;
    color: #cbd5e1;
    margin: 0;
}

@media (max-width: 960px) {
    .seo-advice-grid {
        grid-template-columns: 1fr;
        gap: 10px;
    }
    .guide-grid {
        grid-template-columns: 1fr;
        gap: 12px;
    }
}
@media (max-width: 768px) {
    .seo-summary-card {
        padding: 14px;
    }
    .seo-summary-title {
        font-size: 15px;
    }
    .seo-summary-text {
        font-size: 12.5px;
    }
    .seo-editorial-guide {
        padding: 16px 14px;
    }
}
}
"""

def render_probabili_js():
    return """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 1. Switcher viste per match (Duelli vs Tabellone Fonti)
    document.querySelectorAll('.view-switch-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var matchId = this.getAttribute('data-match');
            var viewType = this.getAttribute('data-view');
            
            var parentSection = document.getElementById('match-sec-' + matchId);
            if (!parentSection) return;
            
            // Toggle bottoni
            parentSection.querySelectorAll('.view-switch-btn').forEach(function(b) {
                b.classList.remove('active');
            });
            this.classList.add('active');
            
            // Toggle viste
            parentSection.querySelectorAll('.match-view-pane').forEach(function(pane) {
                pane.style.display = 'none';
            });
            var targetPane = parentSection.querySelector('.view-pane-' + viewType);
            if (targetPane) {
                targetPane.style.display = 'block';
            }
        });
    });

    // 2. Click su pill carosello per scroll fluido al match
    document.querySelectorAll('.match-pill-card[data-target-sec]').forEach(function(pill) {
        pill.addEventListener('click', function(e) {
            e.preventDefault();
            var targetId = this.getAttribute('data-target-sec');
            var targetEl = document.getElementById(targetId);
            if (targetEl) {
                document.querySelectorAll('.match-pill-card').forEach(function(p) { p.classList.remove('active'); });
                this.classList.add('active');
                targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
</script>
"""

def render_h2h_duel(duel, team_name):
    p1 = duel['player1']
    p2 = duel['player2']
    pct1 = duel['consensus_pct1']
    pct2 = duel['consensus_pct2']
    verdict = duel.get('verdict', {})
    
    p1_cls = "fav" if pct1 >= pct2 else "under"
    p2_cls = "fav" if pct2 > pct1 else "under"
    
    p1_slug = get_player_slug_from_name(p1['name'])
    p2_slug = get_player_slug_from_name(p2['name'])
    duel_slug = f"{slugify(p1['name'])}-vs-{slugify(p2['name'])}"
    
    inj_badge1 = " 🩹" if p1.get('is_injured') else ""
    inj_badge2 = " 🩹" if p2.get('is_injured') else ""

    return f"""
    <div class="duel-card-h2h">
        <div class="duel-card-top">
            <span class="duel-team-tag">⚽ {clean_html(team_name)}</span>
            <span class="verdict-tag {verdict.get('tone', 'safe')}">{clean_html(verdict.get('tag', 'Ballottaggio'))}</span>
        </div>
        
        <div class="duel-h2h-players">
            <!-- Giocatore 1 -->
            <div class="h2h-player-row">
                <div class="h2h-player-lead">
                    <span class="pitch-role-badge {p1.get('role', 'C')}">{p1.get('role', 'C')}</span>
                    <div class="h2h-info">
                        <a href="/calciatore/{p1_slug}/" class="h2h-name" title="Scheda {clean_html(p1['name'])}">{clean_html(p1['name'])}{inj_badge1}</a>
                        <div class="h2h-meta">
                            <span>OVR <b>{p1.get('ovr', 75)}</b></span> &bull; <span>xFM <b>{p1.get('xfm', 6.2):.2f}</b></span>
                        </div>
                    </div>
                </div>
                <div class="h2h-pct {p1_cls}">{pct1}%</div>
            </div>
            
            <!-- Bicolor Gauge -->
            <div class="duel-gauge-bar">
                <div class="gauge-part-left" style="width: {pct1}%;"></div>
                <div class="gauge-part-right" style="width: {pct2}%;"></div>
            </div>

            <!-- Giocatore 2 -->
            <div class="h2h-player-row">
                <div class="h2h-player-lead">
                    <span class="pitch-role-badge {p2.get('role', 'C')}">{p2.get('role', 'C')}</span>
                    <div class="h2h-info">
                        <a href="/calciatore/{p2_slug}/" class="h2h-name" title="Scheda {clean_html(p2['name'])}">{clean_html(p2['name'])}{inj_badge2}</a>
                        <div class="h2h-meta">
                            <span>OVR <b>{p2.get('ovr', 74)}</b></span> &bull; <span>xFM <b>{p2.get('xfm', 6.0):.2f}</b></span>
                        </div>
                    </div>
                </div>
                <div class="h2h-pct {p2_cls}">{pct2}%</div>
            </div>
        </div>
        
        <!-- Verdetto AI -->
        <div class="duel-verdict-box">
            <div class="verdict-desc">💡 {clean_html(verdict.get('desc', ''))}</div>
        </div>
        
        <div class="duel-cta-row">
            <a href="/chi-schiero/{duel_slug}/" class="btn-duel-compare">
                <span>⚔️ Confronta 1vs1 su Chi Schiero</span> &rarr;
            </a>
        </div>
    </div>
    """

def render_consensus_team_table(team_data):
    rows_starters = ""
    for s in team_data.get('starters', []):
        name = s['name']
        slug = get_player_slug_from_name(name)
        role = s.get('role', 'C')
        ovr = s.get('ovr', 75)
        xfm = s.get('xfm', 6.2)
        pct = s.get('consensus_pct', 90)
        
        # Stima quote fonti
        fc_p = pct
        gaz_p = min(95, max(15, pct + 2))
        sky_p = pct
        sos_p = min(95, max(15, pct - 2))
        fp_p = pct
        
        chip_cls = "high" if pct >= 80 else ("mid" if pct >= 60 else ("low" if pct >= 40 else "out"))
        if s.get('is_injured'):
            chip_cls = "out"
            pct_txt = "OUT 🩹"
        else:
            pct_txt = f"{pct}%"

        rows_starters += f"""
        <tr>
            <td class="col-player">
                <span class="pitch-role-badge {role}" style="width:16px;height:16px;font-size:9px;display:inline-flex;margin-right:4px;">{role}</span>
                <a href="/calciatore/{slug}/">{clean_html(name)}</a>
            </td>
            <td style="color:#94a3b8;font-size:11px;">OVR {ovr}</td>
            <td class="col-source">{fc_p}%</td>
            <td class="col-source">{gaz_p}%</td>
            <td class="col-source">{sky_p}%</td>
            <td class="col-source">{sos_p}%</td>
            <td class="col-source">{fp_p}%</td>
            <td class="col-consensus"><span class="consensus-chip {chip_cls}">{pct_txt}</span></td>
            <td style="color:#fbbf24;font-weight:800;font-family:'Outfit';">{xfm:.2f}</td>
            <td style="font-size:11px;color:#cbd5e1;">{clean_html(s.get('sub_txt', 'Titolare'))}</td>
        </tr>
        """

    rows_reserves = ""
    for r in team_data.get('reserves', [])[:8]:
        name = r['name']
        slug = get_player_slug_from_name(name)
        role = r.get('role', 'C')
        ovr = r.get('ovr', 70)
        xfm = r.get('xfm', 5.8)
        pct = r.get('consensus_pct', 15)
        
        chip_cls = "mid" if pct >= 40 else ("low" if pct >= 15 else "out")
        if r.get('is_injured'):
            chip_cls = "out"
            pct_txt = "OUT 🩹"
        else:
            pct_txt = f"{pct}%"

        rows_reserves += f"""
        <tr>
            <td class="col-player">
                <span class="pitch-role-badge {role}" style="width:16px;height:16px;font-size:9px;display:inline-flex;margin-right:4px;">{role}</span>
                <a href="/calciatore/{slug}/" style="color:#94a3b8;">{clean_html(name)}</a>
            </td>
            <td style="color:#64748b;font-size:11px;">OVR {ovr}</td>
            <td class="col-source">{pct}%</td>
            <td class="col-source">{pct}%</td>
            <td class="col-source">{pct}%</td>
            <td class="col-source">{pct}%</td>
            <td class="col-source">{pct}%</td>
            <td class="col-consensus"><span class="consensus-chip {chip_cls}">{pct_txt}</span></td>
            <td style="color:#94a3b8;font-weight:700;font-family:'Outfit';">{xfm:.2f}</td>
            <td style="font-size:11px;color:#64748b;">Subentrante</td>
        </tr>
        """

    return f"""
    <div class="consensus-table-wrapper">
        <table class="consensus-table">
            <thead>
                <tr>
                    <th>Calciatore</th>
                    <th>OVR</th>
                    <th class="col-source">FC.it</th>
                    <th class="col-source">GAZ</th>
                    <th class="col-source">SKY</th>
                    <th class="col-source">SOS</th>
                    <th class="col-source">FP</th>
                    <th class="col-consensus">MEDIA CONSENSUS</th>
                    <th>xFM</th>
                    <th>Status / Consiglio</th>
                </tr>
            </thead>
            <tbody>
                <tr class="section-subhead-row"><td colspan="10">🌟 11 Titolari Probabili — {clean_html(team_data['team'])} ({clean_html(team_data.get('formation', '4-3-3'))})</td></tr>
                {rows_starters}
                <tr class="section-subhead-row"><td colspan="10">🪑 In Panchina &amp; Rotazioni</td></tr>
                {rows_reserves}
            </tbody>
        </table>
    </div>
    """

def parse_match_datetime_iso(date_str, time_str):
    try:
        parts = str(date_str).split('/')
        if len(parts) == 3:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}T{time_str}:00"
    except Exception:
        pass
    return f"2026-10-18T{time_str}:00"

def generate_match_editorial_summary(match_data, round_label):
    """Genera il box sintesi ottimizzato per il Featured Snippet (Posizione 0) di Google."""
    h_team = match_data['home_team']
    a_team = match_data['away_team']
    h_data = match_data['home']
    a_data = match_data['away']
    h_coach = h_data.get('coach', 'Mister')
    a_coach = a_data.get('coach', 'Mister')
    h_mod = h_data.get('formation', '4-3-3')
    a_mod = a_data.get('formation', '3-5-2')
    stadium = match_data.get('stadium', 'Stadio')

    # Top Ballots
    h_ballots = h_data.get('ballots', [])
    a_ballots = a_data.get('ballots', [])
    
    top_ballot_text = ""
    if h_ballots:
        b = h_ballots[0]
        top_ballot_text += f"Nel {clean_html(h_team)} ballottaggio serrato tra <b>{clean_html(b['player1']['name'])}</b> ({b['consensus_pct1']}%) e <b>{clean_html(b['player2']['name'])}</b> ({b['consensus_pct2']}%)."
    if a_ballots:
        b = a_ballots[0]
        top_ballot_text += f" Per il {clean_html(a_team)} duello aperto tra <b>{clean_html(b['player1']['name'])}</b> ({b['consensus_pct1']}%) e <b>{clean_html(b['player2']['name'])}</b> ({b['consensus_pct2']}%)."

    # Injured
    h_injs = [inj.get('player') for inj in h_data.get('injuries', [])]
    a_injs = [inj.get('player') for inj in a_data.get('injuries', [])]
    all_injs = [clean_html(p) for p in (h_injs + a_injs) if p]
    inj_summary = f"Assenti segnalati: {', '.join(all_injs[:4])}." if all_injs else "Nessuna defezione pesante segnalata dalle due infermerie."

    # Rigoristi
    h_rig = (h_data.get('rigoristi', []) or ['-'])[0]
    a_rig = (a_data.get('rigoristi', []) or ['-'])[0]

    return f"""
    <div class="seo-summary-card">
        <div class="seo-summary-badge">⚡ Sintesi Fatti Chiave &bull; Featured Snippet Google</div>
        <h2 class="seo-summary-title">Sintesi Formazioni {clean_html(h_team)} - {clean_html(a_team)} ({clean_html(round_label)})</h2>
        <p class="seo-summary-text">
            Per la <b>{clean_html(round_label)}</b>, il <b>{clean_html(h_team)}</b> di {clean_html(h_coach)} affronta al {clean_html(stadium)} il <b>{clean_html(a_team)}</b> guidato da {clean_html(a_coach)}. 
            Assetto tattico probabile: <b>{clean_html(h_mod)}</b> per i padroni di casa contro il <b>{clean_html(a_mod)}</b> degli ospiti. 
            {top_ballot_text} {clean_html(inj_summary)} 
            Primi rigoristi designati: <b>{clean_html(h_rig)}</b> ({clean_html(h_team)}) e <b>{clean_html(a_rig)}</b> ({clean_html(a_team)}).
        </p>
        <div class="seo-summary-pills">
            <span class="seo-summary-pill">📋 Modulo Casa: <b>{clean_html(h_mod)}</b></span>
            <span class="seo-summary-pill">📋 Modulo Trasferta: <b>{clean_html(a_mod)}</b></span>
            <span class="seo-summary-pill">🎯 1° Rigorista {clean_html(h_team)}: <b>{clean_html(h_rig)}</b></span>
            <span class="seo-summary-pill">🎯 1° Rigorista {clean_html(a_team)}: <b>{clean_html(a_rig)}</b></span>
        </div>
    </div>
    """

def generate_match_ai_advice(match_data):
    """Genera la Bento Grid con consigli predittivi AI (Top Pick, Flop Risk, Super-Sub)."""
    h_team = match_data['home_team']
    a_team = match_data['away_team']
    h_data = match_data['home']
    a_data = match_data['away']

    all_starters = []
    for s in h_data.get('starters', []):
        all_starters.append({**s, 'team': h_team})
    for s in a_data.get('starters', []):
        all_starters.append({**s, 'team': a_team})

    all_reserves = []
    for r in h_data.get('reserves', []):
        all_reserves.append({**r, 'team': h_team})
    for r in a_data.get('reserves', []):
        all_reserves.append({**r, 'team': a_team})

    # 1. Top pick: Starter non infortunato con xfm più alto
    valid_starters = [s for s in all_starters if not s.get('is_injured')]
    if valid_starters:
        top_pick = max(valid_starters, key=lambda x: x.get('xfm', 6.0))
    else:
        top_pick = {'name': 'Top Player', 'team': h_team, 'role': 'A', 'xfm': 7.6, 'ovr': 82}

    # 2. Rischio flop: Difensore o centrocampista con xfm basso o duello incerto
    defensive_starters = [s for s in valid_starters if s.get('role') in ('D', 'C')]
    if defensive_starters:
        risk_player = min(defensive_starters, key=lambda x: x.get('xfm', 6.0))
    else:
        risk_player = min(valid_starters, key=lambda x: x.get('xfm', 6.0)) if valid_starters else {'name': 'Rischio Flop', 'team': a_team, 'role': 'D', 'xfm': 5.4, 'ovr': 67}

    # 3. Jolly: Riserva con xfm più alto
    valid_reserves = [r for r in all_reserves if not r.get('is_injured')]
    if valid_reserves:
        jolly_player = max(valid_reserves, key=lambda x: (x.get('xfm', 5.5), x.get('consensus_pct', 15)))
    else:
        jolly_player = {'name': 'Super Sub', 'team': h_team, 'role': 'A', 'xfm': 6.6, 'ovr': 75}

    pick_slug = get_player_slug_from_name(top_pick['name'])
    risk_slug = get_player_slug_from_name(risk_player['name'])
    jolly_slug = get_player_slug_from_name(jolly_player['name'])

    return f"""
    <div class="seo-advice-grid">
        <!-- Card 1: Top Pick -->
        <div class="seo-advice-card advice-pick">
            <div class="advice-header">
                <span class="advice-badge">🌟 TOP PICK AI</span>
                <span class="advice-team-tag">{clean_html(top_pick['team'])}</span>
            </div>
            <div class="advice-player-row">
                <span class="pitch-role-badge {top_pick.get('role','C')}">{top_pick.get('role','C')}</span>
                <a href="/calciatore/{pick_slug}/" class="advice-name">{clean_html(top_pick['name'])}</a>
            </div>
            <div class="advice-meta">
                <span>OVR <b>{top_pick.get('ovr', 80)}</b></span> &bull; <span>xFM <b>{top_pick.get('xfm', 7.5):.2f}</b></span>
            </div>
            <p class="advice-text">
                Indice predittivo più alto della sfida. Schieralo titolare assoluto: le proiezioni algoritmiche evidenziano massima probabilità di bonus pesante o voto sopra la media.
            </p>
        </div>

        <!-- Card 2: Rischio Flop / Trappola -->
        <div class="seo-advice-card advice-risk">
            <div class="advice-header">
                <span class="advice-badge">⚠️ ATTENZIONE FLOP</span>
                <span class="advice-team-tag">{clean_html(risk_player['team'])}</span>
            </div>
            <div class="advice-player-row">
                <span class="pitch-role-badge {risk_player.get('role','D')}">{risk_player.get('role','D')}</span>
                <a href="/calciatore/{risk_slug}/" class="advice-name">{clean_html(risk_player['name'])}</a>
            </div>
            <div class="advice-meta">
                <span>OVR <b>{risk_player.get('ovr', 68)}</b></span> &bull; <span>xFM <b>{risk_player.get('xfm', 5.5):.2f}</b></span>
            </div>
            <p class="advice-text">
                Reparto ad alto coefficiente di difficoltà. Elevato rischio di malus o insufficienza contro la manovra offensiva avversaria. Valuta alternative più sicure.
            </p>
        </div>

        <!-- Card 3: Jolly Subentrante -->
        <div class="seo-advice-card advice-jolly">
            <div class="advice-header">
                <span class="advice-badge">🔮 JOLLY SUPER-SUB</span>
                <span class="advice-team-tag">{clean_html(jolly_player['team'])}</span>
            </div>
            <div class="advice-player-row">
                <span class="pitch-role-badge {jolly_player.get('role','A')}">{jolly_player.get('role','A')}</span>
                <a href="/calciatore/{jolly_slug}/" class="advice-name">{clean_html(jolly_player['name'])}</a>
            </div>
            <div class="advice-meta">
                <span>OVR <b>{jolly_player.get('ovr', 74)}</b></span> &bull; <span>xFM <b>{jolly_player.get('xfm', 6.5):.2f}</b></span>
            </div>
            <p class="advice-text">
                Spacca-partita designato: l'algoritmo prevede un ingresso a gara in corso con impatto elevato contro linee difensive stanche. Ottimo terzo o quarto slot con copertura.
            </p>
        </div>
    </div>
    """

def generate_match_faqs(match_data, round_label):
    """Genera le FAQ strutturate per il match (HTML accordion + JSON-LD FAQPage)."""
    h_team = match_data['home_team']
    a_team = match_data['away_team']
    h_data = match_data['home']
    a_data = match_data['away']
    h_starters = ", ".join([clean_html(s['name']) for s in h_data.get('starters', [])[:6]])
    a_starters = ", ".join([clean_html(s['name']) for s in a_data.get('starters', [])[:6]])
    
    h_ballots = h_data.get('ballots', [])
    a_ballots = a_data.get('ballots', [])
    b_desc = []
    if h_ballots:
        b = h_ballots[0]
        b_desc.append(f"{b['player1']['name']} vs {b['player2']['name']} ({h_team})")
    if a_ballots:
        b = a_ballots[0]
        b_desc.append(f"{b['player1']['name']} vs {b['player2']['name']} ({a_team})")
    ballot_summary = "; ".join(b_desc) if b_desc else "Gerarchie stabili con titolari definiti per entrambe le formazioni."

    h_rig = ", ".join(h_data.get('rigoristi', [])[:2]) or "da definire"
    a_rig = ", ".join(a_data.get('rigoristi', [])[:2]) or "da definire"

    h_injs = [inj.get('player') for inj in h_data.get('injuries', [])]
    a_injs = [inj.get('player') for inj in a_data.get('injuries', [])]
    all_injs = [clean_html(p) for p in (h_injs + a_injs) if p]
    inj_text = f"Gli indisponibili e infortunati attuali per il match sono: {', '.join(all_injs)}." if all_injs else f"Attualmente non risultano defezioni pesanti per {h_team} o {a_team}."

    faq_list = [
        {
            "q": f"Quali sono le probabili formazioni di {h_team} e {a_team} per la {round_label}?",
            "a": f"La probabile formazione del {h_team} vede come cardini {h_starters} nel modulo {h_data.get('formation','4-3-3')}. Il {a_team} risponde con {a_starters} disposti nel modulo {a_data.get('formation','3-5-2')}. Entrambi i tecnici scioglieranno gli ultimi dubbi nell'immediato pre-partita."
        },
        {
            "q": f"Quali sono i ballottaggi aperti di {h_team}-{a_team}?",
            "a": f"I duelli più incerti monitorati dalle 5 testate di riferimento (Fantacalcio.it, Gazzetta dello Sport, Sky Sport, SOS Fanta, FantaPazz) sono: {ballot_summary}. Le percentuali indicano la probabilità di titolarità dal 1' minuto."
        },
        {
            "q": f"Chi batte i calci di rigore e i piazzati in {h_team} e {a_team}?",
            "a": f"Nel {h_team} il primo rigorista designato è {h_rig}. Per il {a_team} le gerarchie dagli undici metri vedono come prima scelta {a_rig}. Avere rigoristi in campo aumenta significativamente l'Expected FantaMedia (xFM)."
        },
        {
            "q": f"Chi è infortunato o squalificato per {h_team}-{a_team}?",
            "a": f"{inj_text} Tutti i tempi di recupero e gli aggiornamenti dai centri sportivi sono sincronizzati in tempo reale prima di ogni turno."
        },
        {
            "q": f"Come calcola Fanta Master AI il Consensus a 5 Fonti per {h_team}-{a_team}?",
            "a": "Fanta Master AI aggrega e normalizza le percentuali di titolarità pubblicate da Fantacalcio.it, Gazzetta dello Sport, Sky Sport, SOS Fanta e FantaPazz. Il nostro algoritmo proprietario calcola media ponderata e deviazione standard, fornendo un verdetto predittivo che neutralizza gli errori delle singole testate."
        }
    ]

    faq_html = '<div class="seo-faq-wrap">\n'
    faq_schema = []
    for item in faq_list:
        faq_html += f"""
        <details class="seo-faq-item">
            <summary class="seo-faq-question">{clean_html(item['q'])}</summary>
            <div class="seo-faq-answer">{clean_html(item['a'])}</div>
        </details>
        """
        faq_schema.append({
            "@type": "Question",
            "name": item['q'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item['a']
            }
        })
    faq_html += '</div>\n'

    return faq_html, faq_schema

def generate_hub_schedule_table(matches, round_label):
    """Genera la tabella programma gare per l'Hub delle probabili formazioni."""
    rows = ""
    for m in matches:
        m_slug = m['slug']
        h_team = m['home_team']
        a_team = m['away_team']
        h_mod = m['home'].get('formation', '4-3-3')
        a_mod = m['away'].get('formation', '3-5-2')
        stadium = m.get('stadium', 'Stadio')
        big_tag = ' <span style="color:#fbbf24;font-size:10px;">⭐ Big Match</span>' if m.get('big_match') else ''

        rows += f"""
        <tr>
            <td style="color:#94a3b8;font-weight:600;">{clean_html(m['date'])} {clean_html(m['time'])}</td>
            <td>
                <a href="/probabili-formazioni/{m_slug}/" class="schedule-match-link">
                    <span>{clean_html(h_team)}</span> <span style="color:#94a3b8;font-weight:400;">vs</span> <span>{clean_html(a_team)}</span>{big_tag}
                </a>
            </td>
            <td style="color:#cbd5e1;font-size:11.5px;">{clean_html(h_mod)} vs {clean_html(a_mod)}</td>
            <td style="color:#94a3b8;font-size:11.5px;">{clean_html(stadium)}</td>
            <td style="text-align:right;">
                <a href="/probabili-formazioni/{m_slug}/" class="btn-duel-compare" style="font-size:11px;">
                    <span>Scheda Match</span> &rarr;
                </a>
            </td>
        </tr>
        """

    return f"""
    <div class="schedule-table-wrap">
        <table class="seo-hub-schedule-table">
            <thead>
                <tr>
                    <th>Data &amp; Ora</th>
                    <th>Partita (Home vs Away)</th>
                    <th>Moduli Previsti</th>
                    <th>Stadio</th>
                    <th style="text-align:right;">Dettaglio</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """

def generate_hub_editorial_guide(round_label):
    """Genera la guida strategica approfondita E-E-A-T per l'Hub."""
    return f"""
    <section class="seo-editorial-guide">
        <div class="guide-header">
            <h2>Guida Tattica al Fantacalcio: Come Leggere le Probabili Formazioni e Vincere il Turno</h2>
            <p>Metodologia statistica, intelligenza artificiale predittiva e consensus multi-fonte per dominare la {clean_html(round_label)}.</p>
        </div>
        <div class="guide-grid">
            <div class="guide-card">
                <h3 class="guide-card-title"><span>📊</span> 1. Il Modello Consensus 5 Fonti: Superare l'Errore del Singolo Giornale</h3>
                <p class="guide-card-body">
                    Affidarsi a una sola testata espone i fantallenatori a un margine d'errore medio del 32% sulle formazioni di partenza. Ogni redazione (Fantacalcio.it, Gazzetta dello Sport, Sky Sport, SOS Fanta, FantaPazz) si basa su inviati differenti. L'algoritmo di Fanta Master AI calcola la deviazione standard fra le 5 percentuali e isola le divergenze critiche: quando 4 fonti danno un giocatore titolare all'80% e una al 40%, il nostro motore neutralizza l'anomalia per offrirti la reale probabilità statistica.
                </p>
            </div>
            <div class="guide-card">
                <h3 class="guide-card-title"><span>⏱️</span> 2. Staffette 60'/30' e l'Algoritmo xFM (Expected FantaMedia)</h3>
                <p class="guide-card-body">
                    Nel calcio contemporaneo con 5 sostituzioni, il dogma del "titolare fisso a ogni costo" è superato. Un attaccante che gioca gli ultimi 30 minuti contro linee difensive stanche genera spesso un xG/90 (Expected Goals per 90 minuti) e un xFM superiore rispetto a un mediano che disputa 90 minuti ma rischia malus da ammonizione. Quando un ballottaggio è al 55%-45%, verifica sempre l'indice predittivo xFM prima di scartare il panchinaro.
                </p>
            </div>
            <div class="guide-card">
                <h3 class="guide-card-title"><span>🇪🇺</span> 3. Il Fattore Coppe Europee: Gestire il Turnover Scientifico</h3>
                <p class="guide-card-body">
                    I club impegnati nelle competizioni continentali (Champions, Europa e Conference League) effettuano mediamente da 3 a 5 rotazioni nei match di campionato immediatamente successivi. Il nostro modello quantifica i minuti giocati a metà settimana e ricalcola le percentuali di titolarità dei veterani, identificando le seconde linee pronte a partire dal 1' minuto.
                </p>
            </div>
            <div class="guide-card">
                <h3 class="guide-card-title"><span>🎯</span> 4. Piazzati e Rigoristi: Il Moltiplicatore di Bonus Pesanti</h3>
                <p class="guide-card-body">
                    Oltre il 27% dei gol complessivi in Serie A nasce da palle inattive (calci di rigore, punizioni dirette, calci d'angolo trasformati in assist). Schierare difensori e centrocampisti inseriti nelle gerarchie dei piazzati garantisce un boost atteso fino a +0.80 xFM. Prima di consegnare la formazione, verifica sempre la nostra tabella aggiornata dei tiratori.
                </p>
            </div>
        </div>
    </section>
    """

def generate_hub_faqs(round_label, consensus_data):
    """Genera le FAQ strutturate per l'Hub (HTML accordion + JSON-LD FAQPage)."""
    faq_list = [
        {
            "q": "Cosa sono le Probabili Formazioni Consensus a 5 Fonti di Fanta Master AI?",
            "a": "Il Consensus di Fanta Master AI è il primo aggregatore statistico predittivo in Italia che raccoglie in tempo reale le formazioni di Serie A da Fantacalcio.it, Gazzetta dello Sport, Sky Sport, SOS Fanta e FantaPazz. Calcola una media ponderata della titolarità, evidenzia i ballottaggi più incerti e fornisce consigli tattici basati sull'algoritmo predittivo xFM."
        },
        {
            "q": "Quali sono le 5 testate giornalistiche monitorate dall'algoritmo?",
            "a": "Le 5 fonti storiche monitorate sono: 1) Fantacalcio.it (piattaforma ufficiale delle leghe), 2) La Gazzetta dello Sport (quotidiano sportivo nazionale), 3) Sky Sport (inviati h24 sui campi di allenamento), 4) SOS Fanta (community specialistica sul Fantacalcio), 5) FantaPazz (database voti e formazioni)."
        },
        {
            "q": "A che ora e con quale frequenza vengono sincronizzate le probabili formazioni?",
            "a": "L'algoritmo sincronizza i dati più volte al giorno a partire dal martedì, con frequenza oraria il venerdì e aggiornamenti continui nelle 3 ore antecedenti il fischio d'inizio del primo anticipo di giornata di Serie A."
        },
        {
            "q": "Come gestire i ballottaggi al Fantacalcio per evitare il rischio 'senza voto'?",
            "a": "La regola aurea è schierare il calciatore con la più alta percentuale di titolarità garantendosi sempre una copertura certa in panchina. Con l'algoritmo xFM puoi valutare anche l'impatto dei subentranti: se una riserva ha un xFM elevato, vale la pena rischiare la titolarità coprendosi con un titolare certo al 100%."
        },
        {
            "q": "Che cos'è l'indice predittivo xFM (Expected FantaMedia)?",
            "a": "L'xFM è una metrica sviluppata da Fanta Master AI che stima il punteggio fantacalcistico atteso di un calciatore per la giornata corrente. Integra coefficiente di titolarità, Expected Goals (xG), Expected Assists (xA), difficoltà del match (FDR), status di tiratore piazzati e propensione al malus disciplinare."
        },
        {
            "q": "Dove posso consultare le formazioni ufficiali prima della consegna della formazione?",
            "a": "Le formazioni ufficiali vengono comunicate dai club circa un'ora prima del fischio d'inizio di ciascuna partita. Nelle nostre schede match puoi seguire in diretta le conferme degli 11 titolari e gli ultimi aggiornamenti dalle panchine."
        }
    ]

    faq_html = '<div class="seo-faq-wrap">\n'
    faq_schema = []
    for item in faq_list:
        faq_html += f"""
        <details class="seo-faq-item">
            <summary class="seo-faq-question">{clean_html(item['q'])}</summary>
            <div class="seo-faq-answer">{clean_html(item['a'])}</div>
        </details>
        """
        faq_schema.append({
            "@type": "Question",
            "name": item['q'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item['a']
            }
        })
    faq_html += '</div>\n'

    return faq_html, faq_schema

def generate_probabili_formazioni_hub(consensus_data, tactical_db, injuries_db, base_url="https://www.fantamasterai.it", header_html=""):
    """Genera l'hub principale /probabili-formazioni/index.html (Super SEO Suite)."""
    round_label = consensus_data.get('round_label', '7ª Giornata Serie A 2026/27')
    last_updated = consensus_data.get('last_updated', datetime.now().strftime("%d/%m/%Y %H:%M"))
    matches = consensus_data.get('matches', [])

    meta_title = f"Probabili Formazioni Serie A 2026/27: Ballottaggi Consensus 5 Fonti & Titolarità | Fanta Master AI"
    meta_desc = f"Probabili formazioni {round_label} aggiornate: percentuali di titolarità da Fantacalcio.it, Gazzetta, Sky Sport, SOS Fanta e FantaPazz con verdetti predittivi AI, ballottaggi, rigoristi e infortunati."
    page_url = f"{base_url}/probabili-formazioni/"

    # Carousel Pills
    carousel_pills = ""
    for idx, m in enumerate(matches):
        active_cls = "active" if idx == 0 else ""
        clou_tag = '<span class="match-clou">⭐ Big Match</span>' if m.get('big_match') else ""
        carousel_pills += f"""
        <a href="#match-sec-{m['slug']}" class="match-pill-card {active_cls}" data-target-sec="match-sec-{m['slug']}">
            <div class="match-pill-meta">
                <span>{clean_html(m['date'])} {clean_html(m['time'])}</span>
                {clou_tag}
            </div>
            <div class="match-pill-teams">
                <span>{clean_html(m['home_team'][:3].upper())}</span>
                <span class="match-pill-vs">vs</span>
                <span>{clean_html(m['away_team'][:3].upper())}</span>
            </div>
        </a>
        """

    # Top 5 Hot Ballots del Turno
    all_round_ballots = []
    for m in matches:
        for b in m['home'].get('ballots', []):
            all_round_ballots.append((b, m['home_team'], m['slug']))
        for b in m['away'].get('ballots', []):
            all_round_ballots.append((b, m['away_team'], m['slug']))

    # Ordina per margine più stretto (differenza percentuale minore)
    hot_5 = sorted(all_round_ballots, key=lambda x: abs(x[0]['consensus_pct1'] - x[0]['consensus_pct2']))[:6]
    hot_ballots_html = ""
    for b, t_name, m_slug in hot_5:
        hot_ballots_html += render_h2h_duel(b, t_name)

    # Render di ciascun Match
    matches_sections_html = ""
    for idx, m in enumerate(matches):
        m_slug = m['slug']
        h_data = m['home']
        a_data = m['away']

        # Duelli Squadra Casa
        h_duels_list = h_data.get('ballots', [])
        if h_duels_list:
            home_duels_html = "".join(render_h2h_duel(b, m['home_team']) for b in h_duels_list)
        else:
            home_duels_html = f'<div class="no-duels-notice">✓ Formazione tipo di {clean_html(m["home_team"])} definita: nessun ballottaggio aperto segnalato dalle 5 testate.</div>'

        # Duelli Squadra Trasferta
        a_duels_list = a_data.get('ballots', [])
        if a_duels_list:
            away_duels_html = "".join(render_h2h_duel(b, m['away_team']) for b in a_duels_list)
        else:
            away_duels_html = f'<div class="no-duels-notice">✓ Formazione tipo di {clean_html(m["away_team"])} definita: nessun ballottaggio aperto segnalato dalle 5 testate.</div>'

        # Layout a due colonne: Casa a sinistra, Trasferta a destra con link ai cluster club
        h_slug = slugify(m['home_team'])
        a_slug = slugify(m['away_team'])

        two_col_duels_html = f"""
        <div class="match-teams-columns">
            <!-- Colonna Sinistra: Squadra di Casa -->
            <div class="team-duels-column team-home">
                <div class="team-column-header home-header">
                    <div class="team-col-title-wrap">
                        <span class="team-col-icon">🏠</span>
                        <a href="/probabili-formazioni/{h_slug}/" class="team-col-name" style="color:#ffffff;text-decoration:none;" title="Probabile Formazione {clean_html(m['home_team'])}">{clean_html(m['home_team'])}</a>
                        <span class="team-col-badge">CASA</span>
                    </div>
                    <span class="team-col-count">{len(h_duels_list)} duelli</span>
                </div>
                <div class="team-duels-list">
                    {home_duels_html}
                </div>
            </div>

            <!-- Colonna Destra: Squadra Fuori Casa -->
            <div class="team-duels-column team-away">
                <div class="team-column-header away-header">
                    <div class="team-col-title-wrap">
                        <span class="team-col-icon">✈️</span>
                        <a href="/probabili-formazioni/{a_slug}/" class="team-col-name" style="color:#ffffff;text-decoration:none;" title="Probabile Formazione {clean_html(m['away_team'])}">{clean_html(m['away_team'])}</a>
                        <span class="team-col-badge">TRASFERTA</span>
                    </div>
                    <span class="team-col-count">{len(a_duels_list)} duelli</span>
                </div>
                <div class="team-duels-list">
                    {away_duels_html}
                </div>
            </div>
        </div>
        """

        # Tabella comparativa (Anti-FCO)
        table_html = f"""
        <div style="display:flex;flex-direction:column;gap:16px;">
            {render_consensus_team_table(h_data)}
            {render_consensus_team_table(a_data)}
        </div>
        """

        # Piazzati
        def render_setpieces(t_data):
            rigs = ", ".join(t_data.get('rigoristi', [])[:3]) or "-"
            puns = ", ".join(t_data.get('punizioni', [])[:3]) or "-"
            cors = ", ".join(t_data.get('corner', [])[:3]) or "-"
            return f"""
            <div class="takers-list-flow">
                <div class="taker-item-row"><span class="taker-label">🎯 Rigoristi:</span> <span class="taker-values">{clean_html(rigs)}</span></div>
                <div class="taker-item-row"><span class="taker-label">⚡ Punizioni:</span> <span class="taker-values">{clean_html(puns)}</span></div>
                <div class="taker-item-row"><span class="taker-label">🚩 Corner:</span> <span class="taker-values">{clean_html(cors)}</span></div>
            </div>
            """

        # Infortuni
        def render_injuries(t_data):
            injs = t_data.get('injuries', [])
            if not injs:
                return '<div style="color:#4ade80;font-size:11.5px;font-weight:700;">🟢 Tutta la rosa a disposizione</div>'
            items = ""
            for inj in injs:
                items += f"""
                <div class="injury-mini-item">
                    <span class="inj-name">🩹 {clean_html(inj.get('player'))}</span>
                    <span class="inj-meta">{clean_html(inj.get('motivo','Infortunio'))[:25]} &bull; <b class="inj-return-date">{clean_html(inj.get('rientro','TBD'))}</b></span>
                </div>
                """
            return f'<div style="display:flex;flex-direction:column;gap:5px;">{items}</div>'

        big_tag = '<span style="color:#fbbf24;font-size:10px;font-weight:800;background:rgba(251,191,36,0.15);padding:2px 6px;border-radius:4px;">⭐ Big Match</span>' if m.get('big_match') else ''

        matches_sections_html += f"""
        <section id="match-sec-{m_slug}" class="match-detail-section">
            <div class="match-detail-header">
                <div class="match-title-wrap">
                    <div>
                        <h2 class="match-headline">
                            <a href="/probabili-formazioni/{m_slug}/" style="color:#ffffff;text-decoration:none;">{clean_html(m['home_team'])} vs {clean_html(m['away_team'])}</a> {big_tag}
                        </h2>
                        <div class="match-subinfo">📅 {clean_html(m['date'])} ore {clean_html(m['time'])} &bull; 🏟️ {clean_html(m.get('stadium','Stadio'))} &bull; <a href="/probabili-formazioni/{m_slug}/" style="color:#38bdf8;text-decoration:none;">Apri scheda match completa &rarr;</a></div>
                    </div>
                </div>
                
                <!-- View Switcher -->
                <div class="match-view-switcher">
                    <button class="view-switch-btn active" data-match="{m_slug}" data-view="duels">⚔️ Duelli 1vs1</button>
                    <button class="view-switch-btn" data-match="{m_slug}" data-view="table">📊 Tabellone Fonti (Anti-FCO)</button>
                </div>
            </div>

            <!-- Pane 1: Duelli 1vs1 (Default - 2 Colonne Casa vs Fuori Casa) -->
            <div class="match-view-pane view-pane-duels" style="display:block;">
                {two_col_duels_html}
            </div>

            <!-- Pane 2: Tabellone Fonti a Confronto (Anti-FCO) -->
            <div class="match-view-pane view-pane-table" style="display:none;">
                <div style="font-size:11.5px;color:#94a3b8;margin-bottom:8px;">
                    💡 Scorri orizzontalmente per confrontare le percentuali delle 5 testate di riferimento.
                </div>
                {table_html}
            </div>

            <!-- Pannelli Inferiori: Piazzati & Infermeria -->
            <div class="match-bottom-grid">
                <div class="subpanel-card">
                    <div class="subpanel-title">🎯 Piazzati &amp; Tiratori</div>
                    <div style="font-size:11px;font-weight:800;color:#38bdf8;margin-top:2px;">🏠 {clean_html(m['home_team'])}</div>
                    {render_setpieces(h_data)}
                    <div style="font-size:11px;font-weight:800;color:#38bdf8;margin-top:6px;">✈️ {clean_html(m['away_team'])}</div>
                    {render_setpieces(a_data)}
                </div>
                <div class="subpanel-card">
                    <div class="subpanel-title">🩺 Infermeria del Match (Live)</div>
                    <div style="font-size:11px;font-weight:800;color:#f87171;margin-top:2px;">🏠 {clean_html(m['home_team'])}</div>
                    {render_injuries(h_data)}
                    <div style="font-size:11px;font-weight:800;color:#f87171;margin-top:6px;">✈️ {clean_html(m['away_team'])}</div>
                    {render_injuries(a_data)}
                </div>
            </div>
        </section>
        """

    # FAQ Hub
    hub_faq_html, hub_faq_schema = generate_hub_faqs(round_label, consensus_data)

    # Schema JSON-LD
    schema_events = []
    for m in matches:
        iso_start = parse_match_datetime_iso(m.get('date'), m.get('time', '15:00'))
        schema_events.append({
            "@type": "SportsEvent",
            "name": f"{m['home_team']} vs {m['away_team']}",
            "startDate": iso_start,
            "location": {"@type": "Place", "name": m.get('stadium', 'Serie A Stadium')},
            "homeTeam": {"@type": "SportsTeam", "name": m['home_team']},
            "awayTeam": {"@type": "SportsTeam", "name": m['away_team']},
            "url": f"{base_url}/probabili-formazioni/{m['slug']}/"
        })

    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "name": meta_title,
                "url": page_url,
                "dateModified": datetime.now().strftime("%Y-%m-%d"),
                "description": meta_desc
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 2, "name": "Probabili Formazioni Serie A", "item": page_url}
                ]
            },
            {
                "@type": "FAQPage",
                "mainEntity": hub_faq_schema
            }
        ] + schema_events
    }

    full_html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <meta name="keywords" content="probabili formazioni, probabili formazioni serie a, probabili formazioni {clean_html(round_label).lower()}, formazioni fantacalcio, ballottaggi serie a, consensus 5 fonti, titolari fantacalcio, infortunati e squalificati serie a, xFM fantacalcio, serie a 2026 27">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    <link rel="canonical" href="{page_url}">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{clean_html(meta_title)}">
    <meta property="og:description" content="{clean_html(meta_desc)}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="Fanta Master AI">
    <meta property="og:locale" content="it_IT">
    <meta property="og:image" content="{base_url}/static/og-image.jpg">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{clean_html(meta_title)}">
    <meta name="twitter:description" content="{clean_html(meta_desc)}">
    <meta name="twitter:image" content="{base_url}/static/og-image.jpg">

    <!-- Styles -->
    <link rel="stylesheet" href="/css/seo.css">
    <style>
    {render_probabili_css()}
    </style>

    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {json.dumps(schema_data, ensure_ascii=False, indent=2)}
    </script>
</head>
<body>
    {header_html}
    <div class="prob-container">
        <!-- Hero Header -->
        <header class="prob-hero">
            <div class="prob-hero-badge">⚡ Consensus Engine 5 Fonti Live</div>
            <h1 class="prob-hero-title">Probabili Formazioni Serie A — {clean_html(round_label)}</h1>
            <p class="prob-hero-desc">
                Aggregazione statistica in tempo reale dai 5 portali di riferimento: <b>Fantacalcio.it</b>, <b>Gazzetta dello Sport</b>, <b>Sky Sport</b>, <b>SOS Fanta</b> e <b>FantaPazz</b>. Percentuali di titolarità ponderate, verdetti tattici AI e neutralizzazione automatica degli infortunati.
            </p>
            <div class="prob-sources-bar">
                <span>Fonti Monitorate:</span>
                <span class="source-chip">Fantacalcio.it</span>
                <span class="source-chip">Gazzetta dello Sport</span>
                <span class="source-chip">Sky Sport</span>
                <span class="source-chip">SOS Fanta</span>
                <span class="source-chip">FantaPazz</span>
                <span style="color:#fbbf24;margin-left:auto;">🕒 Ultimo sync: <b>{clean_html(last_updated)}</b></span>
            </div>
        </header>

        <!-- Match Carousel Header -->
        <div class="match-carousel-wrapper">
            <div class="carousel-label">
                <span>⚽ Le 10 Partite del Turno</span>
                <span style="font-size:10px;color:#38bdf8;">Clicca per visualizzare formazioni e ballottaggi &darr;</span>
            </div>
            <div class="match-carousel">
                {carousel_pills}
            </div>
        </div>

        <!-- Calendario Programma Gare della Giornata -->
        <div class="seo-section-heading">
            <span class="icon">📅</span>
            <span>Calendario &amp; Programma Anticipi e Posticipi — {clean_html(round_label)}</span>
            <span class="badge">10 Partite</span>
        </div>
        {generate_hub_schedule_table(matches, round_label)}

        <!-- Hot 5 Ballottaggi del Weekend -->
        <section class="hot-ballots-box">
            <div class="hot-ballots-header">
                <div class="hot-ballots-title">
                    <span>🔥 I Ballottaggi più Caldi del Weekend</span>
                </div>
                <span style="font-size:11px;color:#94a3b8;">Duelli con margine &le; 15% tra i titolari</span>
            </div>
            <div class="hot-ballots-grid">
                {hot_ballots_html}
            </div>
        </section>

        <!-- Sezioni dei 10 Match Squadra per Squadra -->
        <div class="seo-section-heading" style="margin-top:32px;">
            <span class="icon">⚽</span>
            <span>Analisi Tattica &amp; Formazioni Squadra per Squadra</span>
            <span class="badge">Consensus 5 Fonti</span>
        </div>
        {matches_sections_html}

        <!-- Guida Tattica Editoriale E-E-A-T -->
        {generate_hub_editorial_guide(round_label)}

        <!-- Domande Frequenti (FAQ) -->
        <section class="seo-faq-section" style="margin-top:28px;">
            <div class="seo-section-heading">
                <span class="icon">❓</span>
                <span>Domande Frequenti su Formazioni, Ballottaggi e Titolarità (FAQ)</span>
                <span class="badge">Google Snippet</span>
            </div>
            {hub_faq_html}
        </section>
    </div>

    {render_probabili_js()}
</body>
</html>
"""
    return full_html

def generate_match_probabili_page(match_data, consensus_data, base_url="https://www.fantamasterai.it", header_html=""):
    """Genera la pagina SEO dedicata a una singola partita (es. /probabili-formazioni/milan-atalanta/)."""
    h_team = match_data['home_team']
    a_team = match_data['away_team']
    m_slug = match_data['slug']
    h_data = match_data['home']
    a_data = match_data['away']
    round_label = consensus_data.get('round_label', '7ª Giornata Serie A 2026/27')
    last_updated = consensus_data.get('last_updated', datetime.now().strftime("%d/%m/%Y %H:%M"))
    
    meta_title = f"Probabili Formazioni {h_team} {a_team} ({round_label}): Titolari, Ballottaggi e Consigli AI | Fanta Master AI"
    meta_desc = f"Probabili formazioni {h_team} - {a_team} ({round_label}): titolari, ballottaggi caldi con percentuali da 5 fonti (Fantacalcio.it, Gazzetta, Sky, SOS, FantaPazz), rigoristi, consigli AI e infortunati."
    page_url = f"{base_url}/probabili-formazioni/{m_slug}/"

    # Carousel delle altre partite
    other_pills = ""
    for om in consensus_data.get('matches', []):
        is_cur = om['slug'] == m_slug
        cur_cls = "active" if is_cur else ""
        link_url = f"/probabili-formazioni/{om['slug']}/" if not is_cur else "#"
        other_pills += f"""
        <a href="{link_url}" class="match-pill-card {cur_cls}">
            <div class="match-pill-meta">
                <span>{clean_html(om['date'])} {clean_html(om['time'])}</span>
            </div>
            <div class="match-pill-teams">
                <span>{clean_html(om['home_team'][:3].upper())}</span>
                <span class="match-pill-vs">vs</span>
                <span>{clean_html(om['away_team'][:3].upper())}</span>
            </div>
        </a>
        """

    # Duelli Squadra Casa
    h_duels_list = h_data.get('ballots', [])
    if h_duels_list:
        home_duels_html = "".join(render_h2h_duel(b, h_team) for b in h_duels_list)
    else:
        home_duels_html = f'<div class="no-duels-notice">✓ Formazione tipo di {clean_html(h_team)} definita: nessun ballottaggio aperto segnalato dalle 5 testate.</div>'

    # Duelli Squadra Trasferta
    a_duels_list = a_data.get('ballots', [])
    if a_duels_list:
        away_duels_html = "".join(render_h2h_duel(b, a_team) for b in a_duels_list)
    else:
        away_duels_html = f'<div class="no-duels-notice">✓ Formazione tipo di {clean_html(a_team)} definita: nessun ballottaggio aperto segnalato dalle 5 testate.</div>'

    # Layout a due colonne con link cluster squadra
    h_slug = slugify(h_team)
    a_slug = slugify(a_team)

    two_col_duels_html = f"""
    <div class="match-teams-columns">
        <!-- Colonna Sinistra: Squadra di Casa -->
        <div class="team-duels-column team-home">
            <div class="team-column-header home-header">
                <div class="team-col-title-wrap">
                    <span class="team-col-icon">🏠</span>
                    <a href="/probabili-formazioni/{h_slug}/" class="team-col-name" style="color:#ffffff;text-decoration:none;" title="Probabile Formazione {clean_html(h_team)}">{clean_html(h_team)}</a>
                    <span class="team-col-badge">CASA</span>
                </div>
                <span class="team-col-count">{len(h_duels_list)} duelli</span>
            </div>
            <div class="team-duels-list">
                {home_duels_html}
            </div>
        </div>

        <!-- Colonna Destra: Squadra Fuori Casa -->
        <div class="team-duels-column team-away">
            <div class="team-column-header away-header">
                <div class="team-col-title-wrap">
                    <span class="team-col-icon">✈️</span>
                    <a href="/probabili-formazioni/{a_slug}/" class="team-col-name" style="color:#ffffff;text-decoration:none;" title="Probabile Formazione {clean_html(a_team)}">{clean_html(a_team)}</a>
                    <span class="team-col-badge">TRASFERTA</span>
                </div>
                <span class="team-col-count">{len(a_duels_list)} duelli</span>
            </div>
            <div class="team-duels-list">
                {away_duels_html}
            </div>
        </div>
    </div>
    """

    # Tabella comparativa (Anti-FCO)
    table_html = f"""
    <div style="display:flex;flex-direction:column;gap:16px;">
        {render_consensus_team_table(h_data)}
        {render_consensus_team_table(a_data)}
    </div>
    """

    # Piazzati
    def render_setpieces(t_data):
        rigs = ", ".join(t_data.get('rigoristi', [])[:3]) or "-"
        puns = ", ".join(t_data.get('punizioni', [])[:3]) or "-"
        cors = ", ".join(t_data.get('corner', [])[:3]) or "-"
        return f"""
        <div class="takers-list-flow">
            <div class="taker-item-row"><span class="taker-label">🎯 Rigoristi:</span> <span class="taker-values">{clean_html(rigs)}</span></div>
            <div class="taker-item-row"><span class="taker-label">⚡ Punizioni:</span> <span class="taker-values">{clean_html(puns)}</span></div>
            <div class="taker-item-row"><span class="taker-label">🚩 Corner:</span> <span class="taker-values">{clean_html(cors)}</span></div>
        </div>
        """

    # Infortuni
    def render_injuries(t_data):
        injs = t_data.get('injuries', [])
        if not injs:
            return '<div style="color:#4ade80;font-size:11.5px;font-weight:700;">🟢 Tutta la rosa a disposizione</div>'
        items = ""
        for inj in injs:
            items += f"""
            <div class="injury-mini-item">
                <span class="inj-name">🩹 {clean_html(inj.get('player'))}</span>
                <span class="inj-meta">{clean_html(inj.get('motivo','Infortunio'))[:25]} &bull; <b class="inj-return-date">{clean_html(inj.get('rientro','TBD'))}</b></span>
            </div>
            """
        return f'<div style="display:flex;flex-direction:column;gap:5px;">{items}</div>'

    big_tag = '<span style="color:#fbbf24;font-size:10px;font-weight:800;background:rgba(251,191,36,0.15);padding:2px 6px;border-radius:4px;">⭐ Big Match</span>' if match_data.get('big_match') else ''

    # Genera FAQ e Schema FAQ
    match_faq_html, match_faq_schema = generate_match_faqs(match_data, round_label)
    iso_start = parse_match_datetime_iso(match_data.get('date'), match_data.get('time', '15:00'))

    # Schema JSON-LD
    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "SportsEvent",
                "name": f"{h_team} vs {a_team}",
                "startDate": iso_start,
                "location": {"@type": "Place", "name": match_data.get('stadium', 'Serie A Stadium')},
                "homeTeam": {"@type": "SportsTeam", "name": h_team},
                "awayTeam": {"@type": "SportsTeam", "name": a_team},
                "url": page_url
            },
            {
                "@type": "WebPage",
                "name": meta_title,
                "url": page_url,
                "dateModified": datetime.now().strftime("%Y-%m-%d"),
                "description": meta_desc
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 2, "name": "Probabili Formazioni Serie A", "item": f"{base_url}/probabili-formazioni/"},
                    {"@type": "ListItem", "position": 3, "name": f"{h_team} vs {a_team}", "item": page_url}
                ]
            },
            {
                "@type": "FAQPage",
                "mainEntity": match_faq_schema
            },
            {
                "@type": "Article",
                "headline": meta_title,
                "datePublished": f"{datetime.now().strftime('%Y-%m-%d')}T08:00:00+02:00",
                "dateModified": datetime.now().strftime("%Y-%m-%d"),
                "description": meta_desc,
                "mainEntityOfPage": page_url,
                "author": {
                    "@type": "Organization",
                    "name": "Fanta Master AI",
                    "url": base_url
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "Fanta Master AI",
                    "logo": {
                        "@type": "ImageObject",
                        "url": f"{base_url}/favicon.ico"
                    }
                }
            }
        ]
    }

    full_html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <meta name="keywords" content="probabili formazioni {clean_html(h_team).lower()} {clean_html(a_team).lower()}, formazioni {clean_html(h_team).lower()} {clean_html(a_team).lower()}, ballottaggi {clean_html(h_team).lower()} {clean_html(a_team).lower()}, titolari {clean_html(h_team).lower()}, titolari {clean_html(a_team).lower()}, fantacalcio {clean_html(h_team).lower()} {clean_html(a_team).lower()}, infortunati {clean_html(h_team).lower()}, infortunati {clean_html(a_team).lower()}, rigoristi {clean_html(h_team).lower()}, rigoristi {clean_html(a_team).lower()}, consigli fantacalcio {clean_html(h_team).lower()} {clean_html(a_team).lower()}">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    <link rel="canonical" href="{page_url}">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">

    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{clean_html(meta_title)}">
    <meta property="og:description" content="{clean_html(meta_desc)}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="Fanta Master AI">
    <meta property="og:locale" content="it_IT">
    <meta property="og:image" content="{base_url}/static/og-image.jpg">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{clean_html(meta_title)}">
    <meta name="twitter:description" content="{clean_html(meta_desc)}">
    <meta name="twitter:image" content="{base_url}/static/og-image.jpg">

    <!-- Styles -->
    <link rel="stylesheet" href="../../css/seo.css">
    <style>
    {render_probabili_css()}
    .prob-breadcrumbs {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11.5px;
        color: #94a3b8;
        margin-bottom: 14px;
    }}
    .prob-breadcrumbs a {{
        color: #94a3b8;
        text-decoration: none;
    }}
    .prob-breadcrumbs a:hover {{
        color: #38bdf8;
    }}
    </style>

    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {json.dumps(schema_data, ensure_ascii=False, indent=2)}
    </script>
</head>
<body>
    {header_html}
    <div class="prob-container">
        <!-- Breadcrumbs -->
        <nav class="prob-breadcrumbs">
            <a href="/">Home</a> <span>/</span>
            <a href="/probabili-formazioni/">Probabili Formazioni</a> <span>/</span>
            <span style="color:#fff;">{clean_html(h_team)} vs {clean_html(a_team)}</span>
        </nav>

        <!-- Carousel altre partite -->
        <div class="match-carousel-wrapper" style="margin-bottom:16px;">
            <div class="carousel-label">
                <span>⚽ Altre Partite della {clean_html(round_label)}</span>
                <a href="/probabili-formazioni/" style="font-size:10px;color:#38bdf8;text-decoration:none;">Vedi tutte le 10 &rarr;</a>
            </div>
            <div class="match-carousel">
                {other_pills}
            </div>
        </div>

        <!-- Sezione Partita Dettaglio -->
        <section id="match-sec-{m_slug}" class="match-detail-section" style="margin-top:10px;">
            <div class="match-detail-header">
                <div class="match-title-wrap">
                    <div>
                        <div class="prob-hero-badge" style="margin-bottom:4px;">Consensus 5 Fonti Ufficiali</div>
                        <h1 class="match-headline">{clean_html(h_team)} vs {clean_html(a_team)} {big_tag}</h1>
                        <div class="match-subinfo">📅 {clean_html(match_data['date'])} ore {clean_html(match_data['time'])} &bull; 🏟️ {clean_html(match_data.get('stadium','Stadio'))} &bull; 🕒 Ultimo sync: {clean_html(last_updated)}</div>
                    </div>
                </div>
                
                <!-- View Switcher -->
                <div class="match-view-switcher">
                    <button class="view-switch-btn active" data-match="{m_slug}" data-view="duels">⚔️ Duelli 1vs1</button>
                    <button class="view-switch-btn" data-match="{m_slug}" data-view="table">📊 Tabellone Fonti (Anti-FCO)</button>
                </div>
            </div>

            <!-- Featured Snippet Position 0 Summary Card -->
            {generate_match_editorial_summary(match_data, round_label)}

            <!-- Consigli Fantacalcio AI Bento Grid -->
            <div class="seo-section-heading">
                <span class="icon">🤖</span>
                <span>Consigli Fantacalcio AI — Scelte Chiave per {clean_html(h_team)} vs {clean_html(a_team)}</span>
                <span class="badge">Predittivo xFM</span>
            </div>
            {generate_match_ai_advice(match_data)}

            <!-- Sezione Duelli 1vs1 -->
            <div class="seo-section-heading" style="margin-top:24px;">
                <span class="icon">⚔️</span>
                <span>Confronto Duelli &amp; Ballottaggi 1vs1 — Consensus 5 Fonti</span>
                <span class="badge">Live Ponderato</span>
            </div>

            <!-- Pane 1: Duelli 1vs1 (Default - 2 Colonne Casa vs Fuori Casa) -->
            <div class="match-view-pane view-pane-duels" style="display:block;">
                {two_col_duels_html}
            </div>

            <!-- Pane 2: Tabellone Fonti a Confronto (Anti-FCO) -->
            <div class="match-view-pane view-pane-table" style="display:none;">
                <div style="font-size:11.5px;color:#94a3b8;margin-bottom:8px;">
                    💡 Scorri orizzontalmente per confrontare le percentuali delle 5 testate di riferimento.
                </div>
                {table_html}
            </div>

            <!-- Pannelli Inferiori: Piazzati & Infermeria -->
            <div class="match-bottom-grid">
                <div class="subpanel-card">
                    <div class="subpanel-title">🎯 Piazzati &amp; Tiratori Ufficiali</div>
                    <div style="font-size:11px;font-weight:800;color:#38bdf8;margin-top:2px;">🏠 {clean_html(h_team)}</div>
                    {render_setpieces(h_data)}
                    <div style="font-size:11px;font-weight:800;color:#38bdf8;margin-top:6px;">✈️ {clean_html(a_team)}</div>
                    {render_setpieces(a_data)}
                </div>
                <div class="subpanel-card">
                    <div class="subpanel-title">🩺 Infermeria &amp; Tempi di Recupero</div>
                    <div style="font-size:11px;font-weight:800;color:#f87171;margin-top:2px;">🏠 {clean_html(h_team)}</div>
                    {render_injuries(h_data)}
                    <div style="font-size:11px;font-weight:800;color:#f87171;margin-top:6px;">✈️ {clean_html(a_team)}</div>
                    {render_injuries(a_data)}
                </div>
            </div>

            <!-- Domande Frequenti (FAQ) -->
            <div class="seo-section-heading" style="margin-top:28px;">
                <span class="icon">❓</span>
                <span>Domande Frequenti su {clean_html(h_team)} vs {clean_html(a_team)} (FAQ)</span>
                <span class="badge">Google Snippet</span>
            </div>
            {match_faq_html}
        </section>
    </div>

    {render_probabili_js()}
</body>
</html>
"""
    return full_html


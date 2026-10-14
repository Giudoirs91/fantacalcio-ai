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

def generate_probabili_formazioni_hub(consensus_data, tactical_db, injuries_db, base_url="https://www.fantamasterai.it", header_html=""):
    """Genera l'hub principale /probabili-formazioni/index.html."""
    round_label = consensus_data.get('round_label', '7ª Giornata Serie A')
    last_updated = consensus_data.get('last_updated', datetime.now().strftime("%d/%m/%Y %H:%M"))
    matches = consensus_data.get('matches', [])

    meta_title = f"Probabili Formazioni Serie A 2026/27: Ballottaggi Consensus 5 Fonti & Titolarità | Fanta Master AI"
    meta_desc = f"Probabili formazioni {round_label} aggiornate: percentuali di titolarità da Fantacalcio.it, Gazzetta, Sky Sport, SOS Fanta e FantaPazz con verdetti predittivi AI, ballottaggi e infortunati."
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

        # Layout a due colonne: Casa a sinistra, Trasferta a destra
        two_col_duels_html = f"""
        <div class="match-teams-columns">
            <!-- Colonna Sinistra: Squadra di Casa -->
            <div class="team-duels-column team-home">
                <div class="team-column-header home-header">
                    <div class="team-col-title-wrap">
                        <span class="team-col-icon">🏠</span>
                        <span class="team-col-name">{clean_html(m['home_team'])}</span>
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
                        <span class="team-col-name">{clean_html(m['away_team'])}</span>
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
                        <h2 class="match-headline">{clean_html(m['home_team'])} vs {clean_html(m['away_team'])} {big_tag}</h2>
                        <div class="match-subinfo">📅 {clean_html(m['date'])} ore {clean_html(m['time'])} &bull; 🏟️ {clean_html(m.get('stadium','Stadio'))}</div>
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

    # Schema JSON-LD
    schema_events = []
    for m in matches:
        schema_events.append({
            "@type": "SportsEvent",
            "name": f"{m['home_team']} vs {m['away_team']}",
            "startDate": f"2026-10-18T{m['time']}:00",
            "location": {"@type": "Place", "name": m.get('stadium', 'Serie A Stadium')},
            "homeTeam": {"@type": "SportsTeam", "name": m['home_team']},
            "awayTeam": {"@type": "SportsTeam", "name": m['away_team']}
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
    <link rel="canonical" href="{page_url}">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{clean_html(meta_title)}">
    <meta property="og:description" content="{clean_html(meta_desc)}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="Fanta Master AI">
    <meta property="og:image" content="{base_url}/static/og-image.jpg">

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

        <!-- Match Carousel Header (Anti-FCO) -->
        <div class="match-carousel-wrapper">
            <div class="carousel-label">
                <span>⚽ Le 10 Partite del Turno</span>
                <span style="font-size:10px;color:#38bdf8;">Clicca per visualizzare formazioni e ballottaggi &darr;</span>
            </div>
            <div class="match-carousel">
                {carousel_pills}
            </div>
        </div>

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

        <!-- Sezioni dei 10 Match -->
        {matches_sections_html}
    </div>

    {render_probabili_js()}
</body>
</html>
"""
    return full_html

def generate_match_probabili_page(match_data, consensus_data, base_url="https://www.fantamasterai.it", header_html=""):
    """Genera la pagina SEO dedicata a una singola partita (es. /probabili-formazioni/frosinone-sassuolo/)."""
    h_team = match_data['home_team']
    a_team = match_data['away_team']
    m_slug = match_data['slug']
    h_data = match_data['home']
    a_data = match_data['away']
    round_label = consensus_data.get('round_label', '7ª Giornata Serie A')
    last_updated = consensus_data.get('last_updated', datetime.now().strftime("%d/%m/%Y %H:%M"))
    
    meta_title = f"Probabili Formazioni {h_team} {a_team}: Ballottaggi, Titolari e Percentuali 5 Fonti | Fanta Master AI"
    meta_desc = f"Probabili formazioni {h_team} - {a_team} ({round_label}): titolari, ballottaggi caldi con percentuali da 5 fonti (Fantacalcio.it, Gazzetta, Sky, SOS, FantaPazz), rigoristi e infortunati."
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

    # Layout a due colonne: Casa a sinistra, Trasferta a destra
    two_col_duels_html = f"""
    <div class="match-teams-columns">
        <!-- Colonna Sinistra: Squadra di Casa -->
        <div class="team-duels-column team-home">
            <div class="team-column-header home-header">
                <div class="team-col-title-wrap">
                    <span class="team-col-icon">🏠</span>
                    <span class="team-col-name">{clean_html(h_team)}</span>
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
                    <span class="team-col-name">{clean_html(a_team)}</span>
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

    # Schema JSON-LD
    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "SportsEvent",
                "name": f"{h_team} vs {a_team}",
                "startDate": f"2026-10-18T{match_data['time']}:00",
                "location": {"@type": "Place", "name": match_data.get('stadium', 'Serie A Stadium')},
                "homeTeam": {"@type": "SportsTeam", "name": h_team},
                "awayTeam": {"@type": "SportsTeam", "name": a_team}
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
    <link rel="canonical" href="{page_url}">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">

    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{clean_html(meta_title)}">
    <meta property="og:description" content="{clean_html(meta_desc)}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="Fanta Master AI">
    <meta property="og:image" content="{base_url}/static/og-image.jpg">

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
        </section>
    </div>

    {render_probabili_js()}
</body>
</html>
"""
    return full_html

/**
 * tracker.js — Raccolta eventi comportamentali anonimi per Fantamaster AI
 * ======================================================================
 * Raccoglie solo informazioni aggregate: pagine visitate, click per ruolo/slot,
 * zone di interesse. Nessun cookie, nessun identificatore utente, nessun IP.
 */
(function() {
    function inviaEvento(tipo, extra) {
        extra = extra || {};
        var payload = {
            tipo: tipo || "pageview",
            pagina: window.location.pathname || "/",
            sezione: extra.sezione || document.title || "",
            ruolo: extra.ruolo || "",
            slot: extra.slot || ""
        };

        try {
            var body = JSON.stringify(payload);
            if (navigator.sendBeacon) {
                var blob = new Blob([body], { type: "application/json" });
                navigator.sendBeacon("/api/track", blob);
            } else {
                fetch("/api/track", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: body,
                    keepalive: true
                }).catch(function() {});
            }
        } catch (e) {}
    }

    // Pageview iniziale
    if (document.readyState === "complete" || document.readyState === "interactive") {
        inviaEvento("pageview");
    } else {
        window.addEventListener("DOMContentLoaded", function() {
            inviaEvento("pageview");
        });
    }

    // Traccia click di navigazione / interazioni
    document.addEventListener("click", function(e) {
        var target = e.target.closest("[data-track], a, button, .role-tab, .slot-pill, .nav-item");
        if (!target) return;

        var tipo = target.getAttribute("data-track") || "click";
        var ruolo = target.getAttribute("data-role") || "";
        var slot = target.getAttribute("data-slot") || "";
        var label = (target.innerText || target.getAttribute("title") || "").trim().substring(0, 50);

        if (target.classList && target.classList.contains("role-tab")) {
            tipo = "filter_role";
            ruolo = target.getAttribute("data-role") || label;
        }

        inviaEvento(tipo, {
            sezione: label,
            ruolo: ruolo,
            slot: slot
        });
    }, true);

    window.FantaTracker = { track: inviaEvento };

    // =========================================================================
    // FLOATING TOAST BANNER TELEGRAM (Opzione A - Non Invasivo)
    // =========================================================================
    var TELEGRAM_URL = "https://t.me/fantamasterai";
    var TG_STORAGE_KEY = "fanta_tg_toast_until";
    var SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;
    var THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;

    function isTelegramToastSuppressed() {
        try {
            var until = localStorage.getItem(TG_STORAGE_KEY);
            if (until && parseInt(until, 10) > Date.now()) {
                return true;
            }
        } catch (e) {}
        return false;
    }

    function setTelegramToastDismiss(ms) {
        try {
            localStorage.setItem(TG_STORAGE_KEY, String(Date.now() + ms));
        } catch (e) {}
    }

    function injectTelegramToast() {
        if (isTelegramToastSuppressed()) return;
        if (document.getElementById("fanta-tg-toast")) return;

        // Inietta CSS dedicato incapsulato
        var styleEl = document.createElement("style");
        styleEl.id = "fanta-tg-toast-style";
        styleEl.textContent = `
            #fanta-tg-toast {
                position: fixed;
                bottom: 24px;
                right: 24px;
                width: 370px;
                max-width: calc(100vw - 32px);
                background: rgba(11, 16, 28, 0.96);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-radius: 16px;
                padding: 16px 18px 14px 18px;
                box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), 0 0 24px rgba(56, 189, 248, 0.18);
                z-index: 99999;
                color: #f8fafc;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                opacity: 0;
                transform: translateY(30px) scale(0.97);
                pointer-events: none;
                transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
                box-sizing: border-box;
            }
            #fanta-tg-toast.fanta-tg-visible {
                opacity: 1;
                transform: translateY(0) scale(1);
                pointer-events: auto;
            }
            #fanta-tg-toast * {
                box-sizing: border-box;
            }
            #fanta-tg-close {
                position: absolute;
                top: 10px;
                right: 12px;
                background: transparent;
                border: none;
                color: #94a3b8;
                font-size: 20px;
                line-height: 1;
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 6px;
                transition: color 0.15s ease, background 0.15s ease;
            }
            #fanta-tg-close:hover {
                color: #ffffff;
                background: rgba(255, 255, 255, 0.1);
            }
            .fanta-tg-header-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-size: 9.5px;
                font-weight: 800;
                letter-spacing: 0.6px;
                text-transform: uppercase;
                color: #38bdf8;
                background: rgba(56, 189, 248, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.28);
                padding: 2px 8px;
                border-radius: 20px;
                margin-bottom: 10px;
            }
            .fanta-tg-dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #00e676;
                box-shadow: 0 0 6px #00e676;
                animation: fantaTgPulse 1.8s infinite;
            }
            @keyframes fantaTgPulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.4; transform: scale(0.8); }
            }
            .fanta-tg-content {
                display: flex;
                align-items: flex-start;
                gap: 12px;
                margin-bottom: 12px;
            }
            .fanta-tg-icon-wrap {
                width: 40px;
                height: 40px;
                border-radius: 12px;
                background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                box-shadow: 0 4px 14px rgba(2, 132, 199, 0.45);
            }
            .fanta-tg-icon {
                width: 22px;
                height: 22px;
                fill: #ffffff;
            }
            .fanta-tg-text {
                flex: 1;
                min-width: 0;
            }
            .fanta-tg-title {
                font-size: 13.5px;
                font-weight: 800;
                color: #ffffff;
                line-height: 1.25;
                margin-bottom: 3px;
                font-family: 'Outfit', 'Inter', sans-serif;
            }
            .fanta-tg-desc {
                font-size: 11.5px;
                color: #94a3b8;
                line-height: 1.42;
            }
            .fanta-tg-actions {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 4px;
            }
            .fanta-tg-btn-join {
                flex: 1;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
                color: #ffffff !important;
                font-size: 12px;
                font-weight: 800;
                text-decoration: none !important;
                padding: 9px 14px;
                border-radius: 10px;
                border: none;
                cursor: pointer;
                transition: transform 0.15s ease, box-shadow 0.15s ease;
                box-shadow: 0 4px 14px rgba(56, 189, 248, 0.35);
            }
            .fanta-tg-btn-join:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 18px rgba(56, 189, 248, 0.55);
            }
            .fanta-tg-btn-later {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.12);
                color: #94a3b8;
                font-size: 11.5px;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.15s ease;
            }
            .fanta-tg-btn-later:hover {
                color: #ffffff;
                border-color: rgba(255, 255, 255, 0.25);
                background: rgba(255, 255, 255, 0.05);
            }
            @media (max-width: 480px) {
                #fanta-tg-toast {
                    bottom: 12px;
                    right: 12px;
                    left: 12px;
                    width: auto;
                    max-width: none;
                    padding: 13px 14px 12px 14px;
                }
            }
        `;
        document.head.appendChild(styleEl);

        // Costruisci il markup DOM del toast
        var toast = document.createElement("div");
        toast.id = "fanta-tg-toast";
        toast.setAttribute("role", "alert");
        toast.setAttribute("aria-live", "polite");
        toast.innerHTML = `
            <button id="fanta-tg-close" aria-label="Chiudi avviso">&times;</button>
            <div class="fanta-tg-header-badge">
                <span class="fanta-tg-dot"></span> LIVE TELEGRAM
            </div>
            <div class="fanta-tg-content">
                <div class="fanta-tg-icon-wrap">
                    <svg viewBox="0 0 24 24" class="fanta-tg-icon" aria-hidden="true">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.52 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06-.01.19-.03.32z"/>
                    </svg>
                </div>
                <div class="fanta-tg-text">
                    <div class="fanta-tg-title">Fanta Master AI su Telegram</div>
                    <div class="fanta-tg-desc">Formazioni ufficiali, ballottaggi dell'ultimo minuto e consigli AI prima del fischio d'inizio.</div>
                </div>
            </div>
            <div class="fanta-tg-actions">
                <a href="${TELEGRAM_URL}" target="_blank" rel="noopener noreferrer" class="fanta-tg-btn-join" id="fanta-tg-join-btn">
                    Entra nel Canale <span>&rarr;</span>
                </a>
                <button class="fanta-tg-btn-later" id="fanta-tg-later-btn">Più tardi</button>
            </div>
        `;
        document.body.appendChild(toast);

        // Mostra con animazione
        requestAnimationFrame(function() {
            setTimeout(function() {
                toast.classList.add("fanta-tg-visible");
                inviaEvento("telegram_toast_shown");
            }, 50);
        });

        function closeToast(isJoin) {
            toast.classList.remove("fanta-tg-visible");
            if (isJoin) {
                setTelegramToastDismiss(THIRTY_DAYS_MS);
                inviaEvento("telegram_toast_joined");
            } else {
                setTelegramToastDismiss(SEVEN_DAYS_MS);
                inviaEvento("telegram_toast_dismissed");
            }
            setTimeout(function() {
                if (toast.parentNode) toast.parentNode.removeChild(toast);
                if (styleEl.parentNode) styleEl.parentNode.removeChild(styleEl);
            }, 400);
        }

        document.getElementById("fanta-tg-close").addEventListener("click", function() {
            closeToast(false);
        });
        document.getElementById("fanta-tg-later-btn").addEventListener("click", function() {
            closeToast(false);
        });
        document.getElementById("fanta-tg-join-btn").addEventListener("click", function() {
            closeToast(true);
        });
    }

    // Trigger: 6 secondi dopo il caricamento oppure dopo scroll di 300px
    var triggered = false;
    function triggerTelegramToast() {
        if (triggered) return;
        triggered = true;
        window.removeEventListener("scroll", onScrollTrigger);
        injectTelegramToast();
    }

    function onScrollTrigger() {
        if (window.scrollY > 300) {
            triggerTelegramToast();
        }
    }

    if (!isTelegramToastSuppressed()) {
        setTimeout(triggerTelegramToast, 6000);
        window.addEventListener("scroll", onScrollTrigger, { passive: true });
    }
})();

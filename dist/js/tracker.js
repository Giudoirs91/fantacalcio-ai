
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
    if (document.readyState === "complete" || document.readyState === "interactive") {
        inviaEvento("pageview");
    } else {
        window.addEventListener("DOMContentLoaded", function() {
            inviaEvento("pageview");
        });
    }
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
})();
(() => {
  "use strict";

  const byId = (id) => document.getElementById(id);
  const numberFormat = new Intl.NumberFormat();
  let toastTimer = null;
  let lastPayload = null;

  function setText(id, value, fallback = "—") {
    const node = byId(id);
    if (node) node.textContent = value === undefined || value === null || value === "" ? fallback : String(value);
  }

  function formatNumber(value) {
    const n = Number(value);
    return Number.isFinite(n) ? numberFormat.format(n) : "—";
  }

  function formatDuration(seconds) {
    const total = Math.max(0, Math.floor(Number(seconds) || 0));
    const days = Math.floor(total / 86400);
    const hours = Math.floor((total % 86400) / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const secs = total % 60;
    if (days) return days + "d " + hours + "h " + minutes + "m";
    if (hours) return hours + "h " + minutes + "m";
    if (minutes) return minutes + "m " + secs + "s";
    return secs + "s";
  }

  function dateNow() {
    return new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date());
  }

  function setConnection(ready, loading = false) {
    const state = loading ? "loading" : ready ? "online" : "offline";
    const label = loading ? "CHECKING CONNECTION" : ready ? "DISCORD CONNECTED" : "DISCORD DISCONNECTED";
    ["connection-status", "diagnostics-status"].forEach((id) => {
      const el = byId(id);
      if (el) el.dataset.state = state;
    });
    setText("connection-label", label);
    setText("diagnostics-label", ready ? "CONNECTED" : loading ? "CHECKING" : "DISCONNECTED");
  }

  function showToast(message) {
    const toast = byId("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2200);
  }

  function applyPayload(payload) {
    lastPayload = payload;
    const ready = Boolean(payload.ready);
    const guildCount = formatNumber(payload.guild_count);
    const uptime = formatDuration(payload.uptime_seconds);
    const requests = Math.max(0, Number(payload.ai_requests) || 0);
    const successes = Math.max(0, Number(payload.ai_successes) || 0);
    const failures = Math.max(0, Number(payload.ai_failures) || 0);
    const rate = requests > 0 ? Math.round((successes / requests) * 100) : 0;

    setConnection(ready);
    setText("hero-version", "VERSION " + (payload.version || "—"));
    setText("hero-title", ready ? "The stage is in your hands." : "The curtain is not quite up.");
    setText("hero-description", ready
      ? "Hades is connected to Discord. Everything is in place, Administrator."
      : "The web process is responding, but the Discord connection is not ready yet.");
    setText("hero-uptime", uptime);
    setText("hero-guilds", guildCount);
    setText("stat-guilds", guildCount);
    setText("stat-messages", formatNumber(payload.messages_seen));
    setText("stat-requests", formatNumber(payload.ai_requests));
    setText("stat-success-rate", requests > 0 ? rate + "%" : "—");
    setText("stat-success-count", formatNumber(successes) + " successes");
    setText("stat-failure-count", formatNumber(failures) + " failures");
    setText("stat-scope-blocks", formatNumber(payload.scope_blocks));
    setText("stat-media-sent", formatNumber(payload.media_sent));
    setText("discord-user", payload.user || (ready ? "Connected" : "Not connected"));
    setText("runtime-name", payload.runtime || "Unknown");
    setText("runtime-branch", payload.branch || "Unknown");
    setText("runtime-commit", payload.commit || "Unknown");
    setText("last-updated", dateNow());
    setText("groq-model", payload.groq_model || "llama-3.3-70b-versatile");

    setText("diag-discord-title", ready ? "Gateway connected" : "Gateway not ready");
    setText("diag-discord-copy", ready ? "The bot reports an active Discord session." : "The web server is responding, but Discord has not reported readiness.");
    setText("diag-user", payload.user || "Not connected");
    setText("diag-guilds", guildCount);
    setText("diag-app-name", payload.name || "Hades Discord Bot");
    setText("diag-version", payload.version || "Unknown");
    setText("diag-uptime", uptime);
    setText("diag-runtime", payload.runtime || "Unknown");
    setText("diag-process-title", payload.service || "Process metadata");

    const error = payload.last_error ? String(payload.last_error) : "";
    const errorBox = byId("error-box");
    if (errorBox) errorBox.hidden = !error;
    setText("error-title", error ? "A recent error was reported" : "No reported error");
    setText("error-description", error ? "The runtime has recorded a recent error. Check server logs for full context." : "The process has not reported a current runtime error.");
    setText("error-message", error, "");

    document.body.dataset.connection = ready ? "online" : "offline";
  }

  async function refreshStatus(showFeedback = false) {
    const button = byId("refresh-button");
    if (button) button.classList.add("is-refreshing");
    try {
      const response = await fetch("/api/status", { cache: "no-store", headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error("Status endpoint returned HTTP " + response.status);
      const payload = await response.json();
      applyPayload(payload);
      if (showFeedback) showToast("Runtime information refreshed.");
    } catch (error) {
      setConnection(false);
      setText("hero-title", "The curtain is closed.");
      setText("hero-description", "Could not reach the status endpoint. Check whether the web process is running.");
      setText("last-updated", "Unavailable");
      setText("diag-discord-title", "Status unavailable");
      setText("diag-discord-copy", "The dashboard could not retrieve runtime data.");
      if (showFeedback) showToast("Could not refresh status. Check the connection.");
    } finally {
      if (button) button.classList.remove("is-refreshing");
    }
  }

  function selectView(view) {
    const labels = { overview: "Overview", diagnostics: "Diagnostics", commands: "Commands" };
    document.querySelectorAll("[data-panel]").forEach((panel) => {
      panel.hidden = panel.dataset.panel !== view;
    });
    document.querySelectorAll(".nav-item[data-view]").forEach((button) => {
      const active = button.dataset.view === view;
      button.classList.toggle("active", active);
      button.setAttribute("aria-current", active ? "page" : "false");
    });
    setText("current-section", labels[view] || "Overview");
  }

  async function copyCommand(button) {
    const value = button.dataset.command || "";
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(value);
      } else {
        const field = document.createElement("textarea");
        field.value = value;
        field.setAttribute("readonly", "");
        field.style.position = "fixed";
        field.style.opacity = "0";
        document.body.appendChild(field);
        field.select();
        const ok = document.execCommand("copy");
        field.remove();
        if (!ok) throw new Error("Copy command failed");
      }
      button.classList.add("copied");
      const mark = button.querySelector(".copy-mark");
      if (mark) mark.textContent = "✓";
      showToast("Copied " + value.trim() + (value.endsWith(" ") ? " " : "") + "to clipboard.");
      setTimeout(() => {
        button.classList.remove("copied");
        if (mark) mark.textContent = "⧉";
      }, 1600);
    } catch {
      showToast("Copy was blocked by the browser. Select the command text manually.");
    }
  }

  document.querySelectorAll(".nav-item[data-view]").forEach((button) => {
    button.addEventListener("click", () => selectView(button.dataset.view));
  });
  document.querySelectorAll("[data-open-view]").forEach((button) => {
    button.addEventListener("click", () => selectView(button.dataset.openView));
  });
  document.querySelectorAll(".command-card[data-command]").forEach((button) => {
    button.addEventListener("click", () => copyCommand(button));
  });
  byId("refresh-button")?.addEventListener("click", () => refreshStatus(true));

  selectView("overview");
  refreshStatus();
  window.setInterval(() => refreshStatus(false), 15000);
})();
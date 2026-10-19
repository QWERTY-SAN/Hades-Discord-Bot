(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const numberFormat = new Intl.NumberFormat();
  const MAX_VISIBLE_LOGS = 300;
  let toastTimer = null;
  let eventStream = null;
  let currentLogs = [];
  let queuedLogs = [];
  let paused = false;
  let lastLogId = 0;
  let hasBootstrapped = false;

  function setText(id, value, fallback = "—") {
    const node = $(id);
    if (node) node.textContent = value === undefined || value === null || value === "" ? fallback : String(value);
  }

  function formatNumber(value) {
    const number = Number(value);
    return Number.isFinite(number) ? numberFormat.format(number) : "—";
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

  function localTime(iso) {
    const date = new Date(iso);
    return Number.isNaN(date.getTime()) ? String(iso || "—") : date.toLocaleTimeString([], { hour12: false });
  }

  function setDiscordConnection(ready) {
    const state = ready ? "online" : "offline";
    const label = ready ? "DISCORD CONNECTED" : "DISCORD DISCONNECTED";
    ["connection-status", "diagnostics-status"].forEach((id) => {
      const node = $(id);
      if (node) node.dataset.state = state;
    });
    setText("connection-label", label);
    setText("diagnostics-label", ready ? "CONNECTED" : "DISCONNECTED");
  }

  function setStreamConnection(connected, message) {
    const state = connected ? "online" : "offline";
    const label = message || (connected ? "LIVE FEED CONNECTED" : "RECONNECTING LIVE FEED");
    const stateNode = $("stream-state");
    if (stateNode) stateNode.dataset.state = state;
    const indicator = $("logs-stream-indicator");
    if (indicator) indicator.dataset.state = state;
    setText("stream-label", label);
    setText("logs-stream-label", connected ? "Live feed connected" : "Reconnecting to event stream");
    setText("logs-tail-status", paused ? "Display paused; events are being buffered" : connected ? "Receiving live events" : "Waiting for the server to reconnect");
  }

  function showToast(message) {
    const toast = $("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("show"), 2400);
  }

  function applyPayload(payload) {
    if (!payload || typeof payload !== "object") return;
    const ready = Boolean(payload.ready);
    const guildCount = formatNumber(payload.guild_count);
    const uptime = formatDuration(payload.uptime_seconds);
    const requests = Math.max(0, Number(payload.ai_requests) || 0);
    const successes = Math.max(0, Number(payload.ai_successes) || 0);
    const failures = Math.max(0, Number(payload.ai_failures) || 0);
    const rate = requests > 0 ? Math.min(100, Math.round((successes / requests) * 100)) : 0;

    setDiscordConnection(ready);
    setText("hero-version", "VERSION " + (payload.version || "—"));
    setText("hero-title", ready ? "Runtime operational" : "Waiting for Discord");
    setText("hero-description", ready
      ? "Discord is connected. Runtime metrics update as the bot processes events."
      : "The web server is responding, but the Discord gateway is not ready.");
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
    setText("last-updated", localTime(new Date().toISOString()));
    setText("groq-model", payload.groq_model || "llama-3.3-70b-versatile");
    setText("gemini-primary-model", payload.gemini_model || "gemini-3.5-flash-lite");
    const fallbackModels = Array.isArray(payload.gemini_fallback_models) ? payload.gemini_fallback_models : ["gemini-3.1-flash-lite"];
    setText("gemini-fallback-model", fallbackModels.join(", ") || "No Gemini fallback configured");

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
    const errorBox = $("error-box");
    if (errorBox) errorBox.hidden = !error;
    setText("error-title", error ? "A recent error was reported" : "No reported error");
    setText("error-description", error ? "The runtime recorded a recent error. Consult host logs for diagnostic detail." : "The process has not reported a current runtime error.");
    setText("error-message", error, "");
  }

  async function refreshStatus(showFeedback = false) {
    const button = $("refresh-button");
    if (button) button.classList.add("is-refreshing");
    try {
      const response = await fetch("/api/status", { cache: "no-store", headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error("Status endpoint returned HTTP " + response.status);
      applyPayload(await response.json());
      if (showFeedback) showToast("Runtime snapshot refreshed.");
    } catch {
      setDiscordConnection(false);
      setText("hero-title", "Status unavailable");
      setText("hero-description", "Could not reach the runtime endpoint. Check the web process and server logs.");
      if (showFeedback) showToast("Could not refresh status.");
    } finally {
      if (button) button.classList.remove("is-refreshing");
    }
  }

  function selectView(view) {
    const labels = { overview: "Overview", diagnostics: "Diagnostics", commands: "Commands", logs: "Live logs" };
    document.querySelectorAll("[data-panel]").forEach((panel) => {
      panel.hidden = panel.dataset.panel !== view;
    });
    document.querySelectorAll(".nav-item[data-view]").forEach((button) => {
      const active = button.dataset.view === view;
      button.classList.toggle("active", active);
      button.setAttribute("aria-current", active ? "page" : "false");
    });
    setText("current-section", labels[view] || "Overview");
    if (view === "logs") renderLogs();
  }

  function normaliseLog(item) {
    if (!item || typeof item !== "object") return null;
    const id = Number(item.id);
    if (!Number.isFinite(id)) return null;
    return {
      id,
      timestamp: String(item.timestamp || ""),
      level: String(item.level || "INFO").toUpperCase(),
      source: String(item.source || "runtime"),
      message: String(item.message || "")
    };
  }

  function appendLog(item) {
    const entry = normaliseLog(item);
    if (!entry || entry.id <= lastLogId) return;
    lastLogId = entry.id;
    if (paused) {
      queuedLogs.push(entry);
      if (queuedLogs.length > MAX_VISIBLE_LOGS) queuedLogs = queuedLogs.slice(-MAX_VISIBLE_LOGS);
      setText("logs-tail-status", "Display paused · " + formatNumber(queuedLogs.length) + " new events buffered");
      return;
    }
    currentLogs.push(entry);
    if (currentLogs.length > MAX_VISIBLE_LOGS) currentLogs = currentLogs.slice(-MAX_VISIBLE_LOGS);
    renderLogs();
  }

  function renderLogs() {
    const list = $("logs-list");
    if (!list) return;
    const query = ($("logs-search")?.value || "").trim().toLowerCase();
    const level = $("logs-level")?.value || "ALL";
    const filtered = currentLogs.filter((entry) => {
      if (level !== "ALL" && entry.level !== level) return false;
      if (!query) return true;
      return [entry.source, entry.level, entry.message, entry.timestamp].some((value) => String(value).toLowerCase().includes(query));
    });
    setText("logs-buffer-count", formatNumber(currentLogs.length));
    setText("logs-filter-count", formatNumber(filtered.length));
    list.replaceChildren();

    if (!filtered.length) {
      const empty = document.createElement("div");
      empty.className = "logs-empty";
      const title = document.createElement("strong");
      title.textContent = currentLogs.length ? "No matching events" : "Waiting for events";
      const detail = document.createElement("p");
      detail.textContent = currentLogs.length ? "Try a different search or severity filter." : "Runtime and provider events appear here as they happen.";
      empty.append(title, detail);
      list.appendChild(empty);
    } else {
      const fragment = document.createDocumentFragment();
      for (const entry of filtered) {
        const row = document.createElement("div");
        row.className = "log-row";
        row.dataset.level = entry.level;
        const timestamp = document.createElement("time");
        timestamp.className = "log-time";
        timestamp.dateTime = entry.timestamp;
        timestamp.textContent = localTime(entry.timestamp);
        timestamp.title = entry.timestamp;
        const badge = document.createElement("span");
        badge.className = "log-level";
        badge.dataset.level = entry.level;
        badge.textContent = entry.level;
        const source = document.createElement("span");
        source.className = "log-source";
        source.textContent = entry.source;
        source.title = entry.source;
        const message = document.createElement("span");
        message.className = "log-message";
        message.textContent = entry.message;
        row.append(timestamp, badge, source, message);
        fragment.appendChild(row);
      }
      list.appendChild(fragment);
      if (!paused) {
        list.scrollTop = list.scrollHeight;
      }
    }
    setText("logs-tail-status", paused ? "Display paused · " + formatNumber(queuedLogs.length) + " new events buffered" : "Showing newest events first");
  }

  function connectEventStream() {
    if (!("EventSource" in window)) {
      setStreamConnection(false, "LIVE FEED UNSUPPORTED");
      refreshStatus();
      return;
    }
    if (eventStream) eventStream.close();
    eventStream = new EventSource("/api/events");

    eventStream.addEventListener("open", () => setStreamConnection(true));
    eventStream.addEventListener("bootstrap", (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status) applyPayload(data.status);
        currentLogs = [];
        queuedLogs = [];
        lastLogId = 0;
        for (const item of (Array.isArray(data.logs) ? data.logs : [])) {
          const entry = normaliseLog(item);
          if (entry) {
            currentLogs.push(entry);
            lastLogId = Math.max(lastLogId, entry.id);
          }
        }
        if (Number.isFinite(Number(data.cursor))) lastLogId = Math.max(lastLogId, Number(data.cursor));
        currentLogs = currentLogs.slice(-MAX_VISIBLE_LOGS);
        hasBootstrapped = true;
        renderLogs();
        setStreamConnection(true);
      } catch {
        showToast("The live feed sent invalid data.");
      }
    });
    eventStream.addEventListener("snapshot", (event) => {
      try {
        applyPayload(JSON.parse(event.data));
      } catch {
        // Ignore malformed snapshots; the next event replaces the current values.
      }
    });
    eventStream.addEventListener("log", (event) => {
      try {
        appendLog(JSON.parse(event.data));
      } catch {
        // Skip a malformed log entry rather than breaking the live stream.
      }
    });
    eventStream.addEventListener("error", () => {
      setStreamConnection(false);
      setText("logs-tail-status", "Connection interrupted; attempting to reconnect");
    });
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
        const copied = document.execCommand("copy");
        field.remove();
        if (!copied) throw new Error("Copy command failed");
      }
      button.classList.add("copied");
      const mark = button.querySelector(".copy-mark");
      if (mark) mark.textContent = "✓";
      showToast("Copied command to clipboard.");
      window.setTimeout(() => {
        button.classList.remove("copied");
        if (mark) mark.textContent = "⧉";
      }, 1600);
    } catch {
      showToast("Copy was blocked by the browser. Select the command manually.");
    }
  }

  function clearLogs() {
    currentLogs = [];
    queuedLogs = [];
    renderLogs();
    showToast("Cleared the visible log buffer. Server history is unchanged.");
  }

  function togglePause() {
    paused = !paused;
    const button = $("logs-pause");
    if (button) button.textContent = paused ? "Resume display" : "Pause display";
    if (!paused && queuedLogs.length) {
      currentLogs.push(...queuedLogs);
      currentLogs = currentLogs.slice(-MAX_VISIBLE_LOGS);
      queuedLogs = [];
    }
    renderLogs();
  }

  function exportLogs() {
    const payload = {
      exported_at: new Date().toISOString(),
      count: currentLogs.length,
      logs: currentLogs
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "hades-runtime-logs.json";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
    showToast("Exported visible operational logs.");
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
  $("refresh-button")?.addEventListener("click", () => refreshStatus(true));
  $("logs-search")?.addEventListener("input", renderLogs);
  $("logs-level")?.addEventListener("change", renderLogs);
  $("logs-pause")?.addEventListener("click", togglePause);
  $("logs-clear")?.addEventListener("click", clearLogs);
  $("logs-export")?.addEventListener("click", exportLogs);
  $("logs-scroll-bottom")?.addEventListener("click", () => {
    const list = $("logs-list");
    if (list) list.scrollTop = list.scrollHeight;
  });

  selectView("overview");
  connectEventStream();
  refreshStatus();
})();
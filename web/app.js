/**
 * ORION Web Dashboard Client Script
 * Handles WebSocket telemetry, state updates, command dispatch, and UI rendering.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation Tabs
  const navItems = document.querySelectorAll(".nav-item");
  const contentTabs = document.querySelectorAll(".content-tab");
  const sectionTitle = document.getElementById("section-title");

  const tabTitles = {
    overview: "System Overview",
    personas: "Voice Personas & Styles",
    plugins: "Cloud Plugin & Skills Hub",
    history: "Command Execution Audit",
  };

  navItems.forEach((item) => {
    item.addEventListener("click", () => {
      const targetTab = item.getAttribute("data-tab");
      navItems.forEach((n) => n.classList.remove("active"));
      contentTabs.forEach((c) => c.classList.remove("active"));

      item.classList.add("active");
      const activeContent = document.getElementById(`tab-${targetTab}`);
      if (activeContent) activeContent.classList.add("active");
      if (sectionTitle && tabTitles[targetTab]) {
        sectionTitle.textContent = tabTitles[targetTab];
      }

      if (targetTab === "personas") fetchPersonas();
      if (targetTab === "plugins") fetchPlugins();
      if (targetTab === "history") fetchFullHistory();
    });
  });

  // ── WebSocket Client Setup ──────────────────────────────────────────────
  let ws = null;
  const connDot = document.querySelector(".conn-dot");
  const connText = document.getElementById("conn-text");

  function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host || "127.0.0.1:8080";
    const wsUrl = `${protocol}//${host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      if (connDot) {
        connDot.className = "conn-dot online";
      }
      if (connText) connText.textContent = "Connected";
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleServerEvent(msg);
      } catch (err) {
        console.error("WS Parse Error:", err);
      }
    };

    ws.onclose = () => {
      if (connDot) {
        connDot.className = "conn-dot offline";
      }
      if (connText) connText.textContent = "Reconnecting...";
      setTimeout(connectWebSocket, 3000);
    };
  }

  function handleServerEvent(msg) {
    if (msg.type === "status") {
      updateStatusOrb(msg.status);
    } else if (msg.type === "command_result") {
      renderCommandResult(msg.data);
      fetchHistoryMini();
    } else if (msg.type === "persona_changed") {
      const badge = document.getElementById("badge-persona-name");
      if (badge) badge.textContent = msg.persona;
    }
  }

  // ── Status Orb Updates ──────────────────────────────────────────────────
  function updateStatusOrb(status) {
    const orb = document.getElementById("status-orb");
    const statusText = document.getElementById("orb-status-text");
    const subtext = document.getElementById("orb-subtext");

    if (!orb) return;
    orb.className = `status-orb status-${status.toLowerCase()}`;

    if (status === "IDLE") {
      statusText.textContent = "IDLE — STANDBY";
      subtext.textContent = "Listening for wake word 'Hey ORION'";
    } else if (status === "LISTENING") {
      statusText.textContent = "LISTENING...";
      subtext.textContent = "Capturing speech via microphone";
    } else if (status === "PROCESSING") {
      statusText.textContent = "PROCESSING...";
      subtext.textContent = "Classifying intent and executing action";
    } else if (status === "SPEAKING") {
      statusText.textContent = "SPEAKING...";
      subtext.textContent = "Synthesizing voice response";
    } else if (status === "ERROR") {
      statusText.textContent = "EXECUTION ERROR";
      subtext.textContent = "Action failed or rejected";
    }
  }

  // ── Command Submission ──────────────────────────────────────────────────
  const cmdForm = document.getElementById("command-form");
  const cmdInput = document.getElementById("cmd-input");

  if (cmdForm) {
    cmdForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = cmdInput.value.trim();
      if (!text) return;

      updateStatusOrb("PROCESSING");
      cmdInput.value = "";

      try {
        const res = await fetch("/api/command", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ command: text }),
        });
        const data = await res.json();
        renderCommandResult(data);
        fetchHistoryMini();
      } catch (err) {
        console.error("Command error:", err);
        updateStatusOrb("ERROR");
      }
    });
  }

  function renderCommandResult(data) {
    const box = document.getElementById("result-box");
    const intentLbl = document.getElementById("res-intent");
    const confLbl = document.getElementById("res-conf");
    const outcomeLbl = document.getElementById("res-outcome");

    if (intentLbl) intentLbl.textContent = `Intent: ${data.intent || "--"}`;
    if (confLbl) confLbl.textContent = `Confidence: ${(data.confidence * 100).toFixed(0)}%`;
    if (outcomeLbl) outcomeLbl.textContent = data.outcome || "No outcome reported.";
  }

  // ── System Telemetry Polling ────────────────────────────────────────────
  async function fetchTelemetry() {
    try {
      const res = await fetch("/api/metrics");
      if (res.ok) {
        const m = await res.json();
        const cpu = document.getElementById("metric-cpu");
        const ram = document.getElementById("metric-ram");
        const bat = document.getElementById("metric-bat");

        if (cpu) cpu.textContent = `${m.cpu_percent}%`;
        if (ram) ram.textContent = `${m.ram_percent}%`;
        if (bat) bat.textContent = m.battery_percent !== null ? `${m.battery_percent}%` : "AC";
      }
    } catch (e) {
      // Ignore network errors in polling
    }
  }
  setInterval(fetchTelemetry, 2500);
  fetchTelemetry();

  // ── Personas Fetch & Switch ─────────────────────────────────────────────
  async function fetchPersonas() {
    try {
      const res = await fetch("/api/personas");
      if (res.ok) {
        const data = await res.json();
        const grid = document.getElementById("personas-grid");
        if (!grid) return;

        grid.innerHTML = "";
        data.personas.forEach((p) => {
          const isActive = p.is_active === "True";
          const card = document.createElement("div");
          card.className = `persona-card ${isActive ? "active" : ""}`;
          card.innerHTML = `
            <div>
              <div class="persona-header">
                <h4 class="persona-title">${p.name}</h4>
                <span class="persona-status-tag ${isActive ? "active" : ""}">${isActive ? "ACTIVE" : "INACTIVE"}</span>
              </div>
              <p class="persona-desc">${p.description}</p>
            </div>
            <div class="persona-footer">
              <div class="persona-meta">
                <span>Speed: ${p.rate} WPM</span>
                <span>Type: ${p.use_neural === "True" ? "Neural" : "Native"}</span>
              </div>
              ${!isActive ? `<button class="btn-sm btn-select-persona" data-id="${p.id}">Activate</button>` : ""}
            </div>
          `;
          grid.appendChild(card);
        });

        document.querySelectorAll(".btn-select-persona").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const pid = btn.getAttribute("data-id");
            await switchPersona(pid);
          });
        });
      }
    } catch (e) {
      console.error("Error fetching personas:", e);
    }
  }

  async function switchPersona(personaId) {
    try {
      const res = await fetch("/api/personas/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ persona_id: personaId }),
      });
      if (res.ok) {
        fetchPersonas();
      }
    } catch (e) {
      console.error("Error selecting persona:", e);
    }
  }

  // ── Plugins Fetch & Install ─────────────────────────────────────────────
  async function fetchPlugins() {
    try {
      const res = await fetch("/api/plugins");
      if (res.ok) {
        const data = await res.json();
        const instContainer = document.getElementById("installed-plugins-list");
        const cloudContainer = document.getElementById("cloud-plugins-list");

        if (instContainer) {
          instContainer.innerHTML = data.installed.length
            ? ""
            : "<p class='card-caption'>No community plugins installed yet.</p>";
          data.installed.forEach((p) => {
            const div = document.createElement("div");
            div.className = "plugin-card";
            div.innerHTML = `
              <div class="plugin-info">
                <h5>${p.name || p.id}</h5>
                <span class="plugin-desc">${p.description || "Custom plugin"}</span>
              </div>
              <button class="btn-sm btn-uninstall-plugin" data-id="${p.id}">Uninstall</button>
            `;
            instContainer.appendChild(div);
          });
        }

        if (cloudContainer) {
          cloudContainer.innerHTML = "";
          data.catalog.forEach((p) => {
            const isInstalled = data.installed.some((i) => i.id === p.id);
            const div = document.createElement("div");
            div.className = "plugin-card";
            div.innerHTML = `
              <div class="plugin-info">
                <h5>${p.name} <span class="version-tag">${p.version || "1.0"}</span></h5>
                <span class="plugin-desc">${p.description}</span>
              </div>
              ${
                isInstalled
                  ? "<span class='persona-status-tag active'>INSTALLED</span>"
                  : `<button class="btn-primary btn-sm btn-install-plugin" data-id="${p.id}">Install</button>`
              }
            `;
            cloudContainer.appendChild(div);
          });
        }

        document.querySelectorAll(".btn-install-plugin").forEach((b) => {
          b.addEventListener("click", async () => {
            const pid = b.getAttribute("data-id");
            await fetch("/api/plugins/install", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ plugin_id: pid }),
            });
            fetchPlugins();
          });
        });

        document.querySelectorAll(".btn-uninstall-plugin").forEach((b) => {
          b.addEventListener("click", async () => {
            const pid = b.getAttribute("data-id");
            await fetch("/api/plugins/uninstall", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ plugin_id: pid }),
            });
            fetchPlugins();
          });
        });
      }
    } catch (e) {
      console.error("Error fetching plugins:", e);
    }
  }

  // ── History Feeds ───────────────────────────────────────────────────────
  async function fetchHistoryMini() {
    try {
      const res = await fetch("/api/history?limit=5");
      if (res.ok) {
        const data = await res.json();
        const list = document.getElementById("mini-history-list");
        if (!list) return;

        list.innerHTML = "";
        data.history.forEach((h) => {
          const div = document.createElement("div");
          div.className = "history-entry";
          div.innerHTML = `
            <div class="entry-left">
              <span class="entry-text">"${h.raw_text}"</span>
              <span class="entry-outcome">${h.outcome || "--"}</span>
            </div>
            <span class="entry-badge">${h.intent}</span>
          `;
          list.appendChild(div);
        });
      }
    } catch (e) {}
  }

  async function fetchFullHistory() {
    try {
      const res = await fetch("/api/history?limit=50");
      if (res.ok) {
        const data = await res.json();
        const tbody = document.getElementById("full-history-tbody");
        if (!tbody) return;

        tbody.innerHTML = "";
        data.history.forEach((h) => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${h.timestamp || "--"}</td>
            <td><strong>"${h.raw_text}"</strong></td>
            <td><span class="entry-badge">${h.intent}</span></td>
            <td>${(h.confidence * 100).toFixed(0)}%</td>
            <td>${h.outcome || "--"}</td>
          `;
          tbody.appendChild(tr);
        });
      }
    } catch (e) {}
  }

  const refreshBtn = document.getElementById("btn-refresh-history");
  if (refreshBtn) refreshBtn.addEventListener("click", fetchHistoryMini);

  // Initialize
  connectWebSocket();
  fetchHistoryMini();
});

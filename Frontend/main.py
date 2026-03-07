from flask import Flask, render_template_string, request, jsonify
import requests
import json
import os

app = Flask(__name__)

HOSTNAME = os.getenv("HOSTNAME", "unknown")
BACKEND_BASE = os.getenv("BACKEND_BASE", "http://localhost:3000")

HTML = """
<!doctype html>
<html>
  <head>
    <title>SRE Playground // {{ hostname }}</title>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
      :root {
        --bg: #0f1117;
        --surface: #161b27;
        --border: #1e2736;
        --accent: #00d9ff;
        --accent2: #7b61ff;
        --green: #00ff88;
        --red: #ff4d6a;
        --yellow: #ffd700;
        --text: #cdd6f4;
        --muted: #454c5e;
        --mono: 'IBM Plex Mono', monospace;
        --sans: 'IBM Plex Sans', sans-serif;
      }

      * { box-sizing: border-box; margin: 0; padding: 0; }

      body {
        background: var(--bg);
        color: var(--text);
        font-family: var(--sans);
        min-height: 100vh;
      }

      body::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
          linear-gradient(rgba(0,217,255,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0,217,255,0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
      }

      .container {
        position: relative;
        z-index: 1;
        max-width: 960px;
        margin: 0 auto;
        padding: 48px 24px;
      }

      .header { margin-bottom: 40px; animation: fadeDown 0.5s ease; }

      .header-top {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
      }

      .status-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 8px var(--green);
        animation: pulse 2s infinite;
      }

      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
      }

      .header-label {
        font-family: var(--mono);
        font-size: 11px;
        letter-spacing: 3px;
        color: var(--muted);
        text-transform: uppercase;
      }

      h1 {
        font-family: var(--mono);
        font-size: clamp(22px, 4vw, 36px);
        font-weight: 600;
        color: #fff;
        letter-spacing: -0.5px;
      }

      h1 span { color: var(--accent); }

      .pod-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-top: 10px;
        padding: 4px 12px;
        background: rgba(0,217,255,0.08);
        border: 1px solid rgba(0,217,255,0.2);
        border-radius: 4px;
        font-family: var(--mono);
        font-size: 12px;
        color: var(--accent);
      }

      .section-label {
        font-family: var(--mono);
        font-size: 10px;
        letter-spacing: 3px;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 12px;
        margin-top: 32px;
      }

      .stats-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        animation: fadeUp 0.4s ease 0.05s both;
      }

      .stat-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
      }

      .stat-value {
        font-family: var(--mono);
        font-size: 32px;
        font-weight: 600;
        color: var(--accent);
        line-height: 1;
        margin-bottom: 6px;
      }

      .stat-label {
        font-family: var(--mono);
        font-size: 11px;
        color: var(--muted);
        letter-spacing: 1px;
      }

      .action-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 16px;
        animation: fadeUp 0.4s ease 0.1s both;
      }

      .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 24px;
        transition: border-color 0.2s, transform 0.15s;
      }

      .card:hover {
        border-color: rgba(0,217,255,0.2);
        transform: translateY(-1px);
      }

      .card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
      }

      .method-badge {
        font-family: var(--mono);
        font-size: 10px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 3px;
        letter-spacing: 1px;
      }

      .method-post {
        background: rgba(123,97,255,0.15);
        color: var(--accent2);
        border: 1px solid rgba(123,97,255,0.3);
      }

      .method-get {
        background: rgba(0,255,136,0.1);
        color: var(--green);
        border: 1px solid rgba(0,255,136,0.25);
      }

      .endpoint {
        font-family: var(--mono);
        font-size: 13px;
        color: var(--muted);
      }

      input {
        width: 100%;
        background: rgba(255,255,255,0.04);
        border: 1px solid var(--border);
        border-radius: 5px;
        padding: 10px 12px;
        font-family: var(--mono);
        font-size: 13px;
        color: var(--text);
        margin-bottom: 10px;
        transition: border-color 0.2s;
        outline: none;
      }

      input::placeholder { color: var(--muted); }
      input:focus { border-color: var(--accent); background: rgba(0,217,255,0.04); }

      button {
        width: 100%;
        padding: 10px 16px;
        background: transparent;
        border: 1px solid var(--accent);
        border-radius: 5px;
        color: var(--accent);
        font-family: var(--mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 1.5px;
        cursor: pointer;
        transition: background 0.2s, color 0.2s, transform 0.1s;
        text-transform: uppercase;
      }

      button:hover { background: var(--accent); color: var(--bg); transform: translateY(-1px); }
      button:active { transform: translateY(0); }

      .btn-get { border-color: var(--green); color: var(--green); }
      .btn-get:hover { background: var(--green); color: var(--bg); }

      .notify {
        font-family: var(--mono);
        font-size: 12px;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        animation: fadeUp 0.3s ease;
      }

      .notify-success {
        color: var(--green);
        background: rgba(0,255,136,0.07);
        border: 1px solid rgba(0,255,136,0.2);
      }

      .notify-error {
        color: var(--red);
        background: rgba(255,77,106,0.07);
        border: 1px solid rgba(255,77,106,0.2);
      }

      .bottom-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        animation: fadeUp 0.4s ease 0.2s both;
      }

      @media (max-width: 640px) { .bottom-grid { grid-template-columns: 1fr; } }

      .panel {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
      }

      .panel-header {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        border-bottom: 1px solid var(--border);
        background: rgba(255,255,255,0.02);
      }

      .panel-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
      }

      .panel-dot-accent { background: var(--accent); }
      .panel-dot-yellow { background: var(--yellow); }

      .panel-title {
        font-family: var(--mono);
        font-size: 10px;
        letter-spacing: 2px;
        color: var(--muted);
        text-transform: uppercase;
      }

      .user-table {
        width: 100%;
        border-collapse: collapse;
        font-family: var(--mono);
        font-size: 12px;
      }

      .user-table th {
        text-align: left;
        padding: 10px 16px;
        color: var(--muted);
        font-size: 10px;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-bottom: 1px solid var(--border);
      }

      .user-table td {
        padding: 10px 16px;
        border-bottom: 1px solid rgba(30,39,54,0.5);
        color: var(--text);
      }

      .user-table tr:last-child td { border-bottom: none; }
      .user-table tr:hover td { background: rgba(255,255,255,0.02); }

      .event-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px;
        border-bottom: 1px solid rgba(30,39,54,0.5);
        font-family: var(--mono);
        font-size: 12px;
      }

      .event-item:last-child { border-bottom: none; }

      .event-tag {
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 10px;
        background: rgba(0,217,255,0.1);
        color: var(--accent);
        border: 1px solid rgba(0,217,255,0.2);
        white-space: nowrap;
      }

      .event-user { color: var(--text); flex: 1; }
      .event-time { color: var(--muted); font-size: 11px; white-space: nowrap; }

      .empty-state {
        padding: 24px 16px;
        font-family: var(--mono);
        font-size: 12px;
        color: var(--muted);
        font-style: italic;
      }

      @keyframes fadeUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
      }

      @keyframes fadeDown {
        from { opacity: 0; transform: translateY(-8px); }
        to { opacity: 1; transform: translateY(0); }
      }
    </style>
  </head>
  <body>
    <div class="container">

      <div class="header">
        <div class="header-top">
          <div class="status-dot"></div>
          <span class="header-label">SRE Playground // Microservice Frontend</span>
        </div>
        <h1>API <span>Explorer</span></h1>
        <div class="pod-badge">▸ pod/{{ hostname }}</div>
      </div>

      <div class="section-label">// system stats</div>
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-value" id="stat-total">{{ stats.total_registrations }}</div>
          <div class="stat-label">total registrations</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" id="stat-last-minute" style="color: var(--green)">{{ stats.registrations_last_minute }}</div>
          <div class="stat-label">last 60 seconds</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" id="stat-users" style="color: var(--accent2)">{{ users | length }}</div>
          <div class="stat-label">users in db</div>
        </div>
      </div>

      <div class="section-label">// actions</div>
      <div class="action-grid">

        <div class="card">
          <div class="card-header">
            <span class="method-badge method-post">POST</span>
            <span class="endpoint">/user</span>
          </div>
          <input type="text" id="input-username" placeholder="username">
          <input type="password" id="input-password" placeholder="password">
          <button id="btn-create">↳ Create User + Produce Event</button>
        </div>

        <div class="card">
          <div class="card-header">
            <span class="method-badge method-get">GET</span>
            <span class="endpoint">/user</span>
          </div>
          <p style="font-size:13px; color: var(--muted); margin-bottom: 16px; line-height: 1.5;">
            Fetch all registered users from PostgreSQL.
          </p>
          <button class="btn-get" id="btn-get-users">↳ Get All Users</button>
        </div>

      </div>

      <div id="notification-area"></div>

      <div class="section-label">// data</div>
      <div class="bottom-grid">

        <div class="panel" id="panel-users">
          <div class="panel-header">
            <div class="panel-dot panel-dot-accent"></div>
            <span class="panel-title">Users — PostgreSQL</span>
          </div>
          <div id="users-body">
          {% if users %}
          <table class="user-table">
            <thead>
              <tr><th>#</th><th>Username</th></tr>
            </thead>
            <tbody id="users-tbody">
              {% for user in users %}
              <tr>
                <td style="color: var(--muted)">{{ loop.index }}</td>
                <td>{{ user.username }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          {% else %}
          <div class="empty-state">// no users yet</div>
          {% endif %}
          </div>
        </div>

        <div class="panel" id="panel-events">
          <div class="panel-header">
            <div class="panel-dot panel-dot-yellow"></div>
            <span class="panel-title">Recent Events — Redis</span>
          </div>
          <div id="events-body">
          {% if events %}
            {% for event in events %}
            <div class="event-item">
              <span class="event-tag">{{ event.event }}</span>
              <span class="event-user">{{ event.username }}</span>
              <span class="event-time">{{ event.timestamp | datetimeformat }}</span>
            </div>
            {% endfor %}
          {% else %}
          <div class="empty-state">// no events yet</div>
          {% endif %}
          </div>
        </div>

      </div>

    </div>

    <script>
      function formatTime(ts) {
        try { return new Date(ts).toTimeString().slice(0, 8); }
        catch { return '—'; }
      }

      function showNotification(ok, message) {
        const area = document.getElementById('notification-area');
        area.innerHTML = `
          <div class="notify ${ok ? 'notify-success' : 'notify-error'}">
            ${ok ? '✓' : '✗'} ${message}
          </div>`;
        setTimeout(() => { area.innerHTML = ''; }, 5000);
      }

      function renderUsers(users) {
        const el = document.getElementById('users-body');
        document.getElementById('stat-users').textContent = users.length;
        if (!users.length) {
          el.innerHTML = '<div class="empty-state">// no users yet</div>';
          return;
        }
        el.innerHTML = `
          <table class="user-table">
            <thead><tr><th>#</th><th>Username</th></tr></thead>
            <tbody>
              ${users.map((u, i) => `
                <tr>
                  <td style="color:var(--muted)">${i + 1}</td>
                  <td>${u.username}</td>
                </tr>`).join('')}
            </tbody>
          </table>`;
      }

      function renderEvents(events) {
        const el = document.getElementById('events-body');
        if (!events.length) {
          el.innerHTML = '<div class="empty-state">// no events yet</div>';
          return;
        }
        el.innerHTML = events.map(e => `
          <div class="event-item">
            <span class="event-tag">${e.event}</span>
            <span class="event-user">${e.username}</span>
            <span class="event-time">${formatTime(e.timestamp)}</span>
          </div>`).join('');
      }

      async function refreshData() {
        try {
          const [statsRes, usersRes, eventsRes] = await Promise.all([
            fetch('/stats'),
            fetch('/user'),
            fetch('/events'),
          ]);
          if (statsRes.ok) {
            const s = await statsRes.json();
            document.getElementById('stat-total').textContent = s.total_registrations ?? '—';
            document.getElementById('stat-last-minute').textContent = s.registrations_last_minute ?? '—';
          }
          if (usersRes.ok) renderUsers(await usersRes.json());
          if (eventsRes.ok) renderEvents(await eventsRes.json());
        } catch (err) {
          console.warn('Poll error:', err);
        }
      }

      // Create user — no page reload
      document.getElementById('btn-create').addEventListener('click', async () => {
        const username = document.getElementById('input-username').value.trim();
        const password = document.getElementById('input-password').value.trim();
        if (!username || !password) {
          showNotification(false, 'Username and password are required');
          return;
        }
        try {
          const res = await fetch('/create-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
          });
          const data = await res.json();
          if (res.ok) {
            showNotification(true, `User '${username}' created and event pushed to Kafka → worker → Redis`);
            document.getElementById('input-username').value = '';
            document.getElementById('input-password').value = '';
            refreshData();
          } else {
            showNotification(false, data.error || 'Failed to create user');
          }
        } catch (err) {
          showNotification(false, err.toString());
        }
      });

      // Manual refresh button
      document.getElementById('btn-get-users').addEventListener('click', refreshData);

      // Background poll every 5s — data only, no page reload
      setInterval(refreshData, 5000);
    </script>
  </body>
</html>
"""

def fetch_stats():
    try:
        res = requests.get(f"{BACKEND_BASE}/stats", timeout=2)
        return res.json()
    except:
        return {"total_registrations": "—", "registrations_last_minute": "—"}

def fetch_users():
    try:
        res = requests.get(f"{BACKEND_BASE}/user", timeout=2)
        return res.json()
    except:
        return []

def fetch_events():
    try:
        res = requests.get(f"{BACKEND_BASE}/events", timeout=2)
        return res.json()
    except:
        return []

def datetimeformat(ts):
    try:
        from datetime import datetime
        return datetime.fromtimestamp(ts / 1000).strftime("%H:%M:%S")
    except:
        return "—"

app.jinja_env.filters['datetimeformat'] = datetimeformat


# ── API proxy routes (called by the frontend JS) ──────────────────────────────

@app.route("/stats")
def api_stats():
    return jsonify(fetch_stats())

@app.route("/user")
def api_users():
    return jsonify(fetch_users())

@app.route("/events")
def api_events():
    return jsonify(fetch_events())

@app.route("/user", methods=["POST"])
def api_create_user():
    body = request.get_json(force=True)
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    try:
        res = requests.post(f"{BACKEND_BASE}/user", json={"username": username, "password": password}, timeout=5)
        if res.status_code in (200, 201):
            requests.post(f"{BACKEND_BASE}/kafka-produce", json={"username": username}, timeout=2)
            return jsonify({"ok": True}), 201
        return jsonify({"error": res.json().get("error", "Failed to create user")}), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Main page ─────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    stats = fetch_stats()
    users = fetch_users()
    events = fetch_events()
    return render_template_string(
        HTML,
        hostname=HOSTNAME,
        stats=stats,
        users=users,
        events=events,
        notification=None,
    )


# ── Health checks ─────────────────────────────────────────────────────────────

@app.route("/healthz/live")
def liveness():
    return {"status": "ok"}, 200


@app.route("/healthz/ready")
def readiness():
    print(f"Readiness check started, BACKEND_BASE={BACKEND_BASE}", flush=True)
    try:
        res = requests.get(f"{BACKEND_BASE}/healthz/live", timeout=10)
        print(f"Backend responded with status={res.status_code}", flush=True)
        if res.status_code == 200:
            return {"status": "ready"}, 200
        return {"status": f"backend returned {res.status_code}"}, 503
    except requests.exceptions.Timeout:
        print(f"TIMEOUT connecting to {BACKEND_BASE}", flush=True)
        return {"status": "timeout"}, 503
    except requests.exceptions.ConnectionError as e:
        print(f"CONNECTION ERROR: {str(e)}", flush=True)
        return {"status": "connection error"}, 503
    except Exception as e:
        print(f"UNEXPECTED ERROR: {type(e).__name__}: {str(e)}", flush=True)
        return {"status": "error"}, 503


if __name__ == "__main__":
    port = int(os.getenv("FRONTEND_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
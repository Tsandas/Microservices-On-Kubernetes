from flask import Flask, render_template_string, request
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
    <title>Microservice Frontend - Pod {{ hostname }}</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 40px; }
      input, button { padding: 8px; font-size: 14px; margin: 5px 0; }
      #response { margin-top: 20px; white-space: pre-wrap; background: #f4f4f4; padding: 10px; border-radius: 5px; }
      h2 { margin-top: 30px; }
    </style>
  </head>
  <body>
    <h1>Frontend App (Pod {{ hostname }})</h1>

    <h2>POST /user</h2>
    <form method="post">
      <input type="text" name="username" placeholder="Enter username" required>
      <input type="password" name="password" placeholder="Enter password" required>
      <button name="action" value="create_user">Create User</button>
    </form>

    <h2>GET /data</h2>
    <form method="post">
      <button name="action" value="get_data">Get Random Data</button>
    </form>

    <h2>GET /user</h2>
    <form method="post">
      <button name="action" value="get_users">Get All Users</button>
    </form>

    {% if response %}
      <div id="response"><strong>Response:</strong><br>{{ response }}</div>
    {% endif %}
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = None
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "create_user":
                username = request.form.get("username")
                password = request.form.get("password")
                res = requests.post(f"{BACKEND_BASE}/user", json={"username": username, "password": password})
                response_text = json.dumps(res.json(), indent=2)

            elif action == "get_data":
                res = requests.get(f"{BACKEND_BASE}/data")
                response_text = json.dumps(res.json(), indent=2)

            elif action == "get_users":
                res = requests.get(f"{BACKEND_BASE}/user")
                response_text = json.dumps(res.json(), indent=2)

        except Exception as e:
            response_text = f"Error: {e}"

    return render_template_string(HTML, response=response_text, hostname=HOSTNAME)

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
        return {"status": f"connection error"}, 503
    except Exception as e:
        print(f"UNEXPECTED ERROR: {type(e).__name__}: {str(e)}", flush=True)
        return {"status": f"error"}, 503

if __name__ == "__main__":
    port = int(os.getenv("FRONTEND_PORT", 5000))
    app.run(host="0.0.0.0", port=port)

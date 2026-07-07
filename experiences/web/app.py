import os

from flask import Flask, render_template, jsonify
import requests

DOMAIN_API_URL = os.getenv("DOMAIN_API_URL", "http://behaviour-service:8000")

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/colours", methods=["POST"])
def create_colour_proxy():
    """Proxy endpoint that calls the behaviour service.

    The browser POSTs same-origin here; this server forwards to the domain API
    (POST /colours) to avoid CORS on writes. The API location comes from
    DOMAIN_API_URL, like the mobile and agent experiences.
    """
    try:
        resp = requests.post(f"{DOMAIN_API_URL}/colours", timeout=5)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "failed to reach behaviour service", "details": str(e)}), 502

    try:
        data = resp.json()
    except ValueError:
        return jsonify({"error": "behaviour service returned non-json"}), 502

    return jsonify(data), resp.status_code


if __name__ == "__main__":
    # Simple dev server; docker-compose maps 5000:5000
    app.run(host="0.0.0.0", port=5000)

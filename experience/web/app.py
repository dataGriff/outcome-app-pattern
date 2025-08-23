from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate-colour", methods=["POST", "GET"])
def generate_colour_proxy():
    """Proxy endpoint that calls the behaviour service.

    When running inside docker-compose the behaviour service is reachable
    at http://behaviour-service:8000. This server proxies requests there
    to avoid CORS from the browser.
    """
    try:
        resp = requests.post("http://behaviour-service:8000/generate-colour", timeout=5)
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

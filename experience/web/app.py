import requests
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

API_URL = "http://behaviour-service:8000/generate-colour"

HTML = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>Colour Generator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        button { font-size: 1.2em; padding: 0.5em 1em; }
        #result { margin-top: 1em; white-space: pre-wrap; font-size: 1.2em; }
    </style>
</head>
<body>
    <h1>Generate Colour</h1>
    <button id="generateBtn">Generate</button>
    <div id="result"></div>
    <script>
        // Call the backend to request a generated colour
        function generateColour() {
            const resEl = document.getElementById('result');
            console.log('generateColour clicked');
            resEl.innerText = 'Requesting...';
            // quick visual cue while we wait and debug logs for the browser
            try {
                fetch('/generate', {method: 'POST'})
                    .then(response => {
                        console.log('fetch /generate response', response.status);
                        return response.json().catch(err => ({ error: 'invalid-json' }));
                    })
                    .then(data => {
                        console.log('fetch /generate data', data);
                        const colour = (data && (data.colour || data.color || data.error)) || 'N/A';
                        const ts = (data && (data.timestamp || data.time)) || '';
                        resEl.innerText = 'Colour: ' + colour + '\nTimestamp: ' + ts;
                    })
                    .catch(err => {
                        console.error('fetch /generate error', err);
                        resEl.innerText = 'Error contacting API. See console.';
                    });
            } catch (e) {
                console.error('generateColour exception', e);
                resEl.innerText = 'Error initiating request.';
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('generateBtn').addEventListener('click', generateColour);
        });
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/generate", methods=["POST"])
def generate():
    try:
        resp = requests.post(API_URL, timeout=5)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/run', methods=['POST'])
def run_route():
    return jsonify({
        "status": "deprecated_entry",
        "message": "Use /upload instead of /run"
    })


@app.route('/health')
def health():
    return {"status": "V3_OK_PIPELINE"}


if __name__ == "__main__":
    print("🚀 V3.9 MAIN STARTED (ENTRY DISABLED)")
    app.run(host="0.0.0.0", port=8000)
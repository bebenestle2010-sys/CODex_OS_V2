from flask import Flask, request, jsonify
from pipeline_runner import run

app = Flask(__name__)


@app.route('/run', methods=['POST'])
def run_route():
    data = request.json or {}
    files = data.get("files", [])

    if not isinstance(files, list):
        return jsonify({"error": "files must be list"}), 400

    # 🚀 V3.6唯一入口：进入 pipeline
    result = run(files)

    return jsonify(result)


@app.route('/health')
def health():
    return {"status": "V3_OK_PIPELINE"}


if __name__ == "__main__":
    print("🚀 V3.6 MAIN STARTED")
    app.run(host="0.0.0.0", port=8000)

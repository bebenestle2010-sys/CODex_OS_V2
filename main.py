from flask import Flask, request, jsonify
from pipeline_runner import run

app = Flask(__name__)


@app.route('/run', methods=['POST'])
def run_route():
    data = request.json or {}
    files = data.get("files", [])

    if not isinstance(files, list):
        return jsonify({"error": "files must be list"}), 400

    # 🚀 V3.6 正式链路入口（关键修复点）
    result = run(files)

    return jsonify(result)


@app.route('/health')
def health():
    return {"status": "V3.6_FIXED_OK"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

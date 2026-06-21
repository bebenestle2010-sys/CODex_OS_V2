from flask import Flask, request, jsonify
from task_queue import push
import uuid

app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload():
    data = request.json or {}
    files = data.get("files", [])

    if not isinstance(files, list):
        return jsonify({"error": "files must be list"}), 400

    task = {
        "task_id": str(uuid.uuid4()),
        "files": files
    }

    push(task)

    return jsonify({
        "status": "queued",
        "task_id": task["task_id"]
    })


@app.route("/health")
def health():
    return {"status": "UPLOAD_V3_OK"}


if __name__ == "__main__":
    print("🚀 UPLOAD SERVICE STARTED V3.9")
    app.run(host="0.0.0.0", port=9000)
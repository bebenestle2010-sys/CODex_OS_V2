from flask import Flask, request, jsonify
from task_queue import push
import uuid

app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload():
    data = request.json or {}
    files = data.get("files", [])

    task = {
        "id": str(uuid.uuid4()),
        "files": files
    }

    # 💥 关键：必须入队
    push(task)

    print("[UPLOAD] QUEUED:", task["id"])

    return jsonify({"id": task["id"], "status": "queued"})


@app.route("/health")
def health():
    return {"status": "V3_9_OK"}


if __name__ == "__main__":
    print("🚀 UPLOAD SERVICE STARTED")
    app.run(host="0.0.0.0", port=9000)

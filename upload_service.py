from upload_trigger import upload_trigger
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload():
    data = request.json or {}
    files = data.get("files", [])

    result = upload_trigger(files)

    return jsonify(result)


@app.route("/health")
def health():
    return {"status": "UPLOAD_V3_7_OK"}


if __name__ == "__main__":
    print("🚀 Upload Service V3.7 Started")
    app.run(host="0.0.0.0", port=9000)

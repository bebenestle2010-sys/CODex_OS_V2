import json

# ---------------------------
# SAFE LOAD: mapping file
# ---------------------------
def load_map():
    try:
        with open("CODex_MAPPING.json", "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print("❌ Mapping load failed:", e)
        return {}


# ---------------------------
# SAFE LOAD: index file
# ---------------------------
def load_index():
    try:
        with open("server_file_index.txt", "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print("❌ Index load failed:", e)
        return ""


# ---------------------------
# CORE CLASSIFIER
# ---------------------------
def classify_system():
    mapping = load_map()
    index = load_index()

    brain = []
    control = []
    execution = []

    # 防止空内容崩溃
    if not index:
        return {
            "error": "EMPTY_INDEX",
            "brain_candidates": [],
            "control_candidates": [],
            "execution_candidates": []
        }

    for line in index.splitlines():

        line_lower = line.lower()

        # ---------------- Brain Layer ----------------
        if (
            "brain" in line_lower
            or "v88500" in line_lower
            or "decision" in line_lower
            or "score" in line_lower
        ):
            brain.append(line)

        # ---------------- Control Layer ----------------
        elif (
            "router" in line_lower
            or "control" in line_lower
            or "guard" in line_lower
            or "lock" in line_lower
        ):
            control.append(line)

        # ---------------- Execution Layer ----------------
        elif (
            "executor" in line_lower
            or "upload" in line_lower
            or "execution" in line_lower
            or "feishu" in line_lower
            or "amazon" in line_lower
        ):
            execution.append(line)

    return {
        "brain_candidates": brain[:15],
        "control_candidates": control[:15],
        "execution_candidates": execution[:15],
        "mapping_loaded": bool(mapping)
    }


# ---------------------------
# ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    result = classify_system()
    print(json.dumps(result, indent=2, ensure_ascii=False))
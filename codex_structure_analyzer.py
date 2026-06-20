import json

def load_index():
    with open("10_SERVER_EXTRACT/server_file_index.txt", "r", encoding="utf-8") as f:
        return f.read().splitlines()


def classify(files):
    brain = []
    control = []
    execution = []
    data = []
    legacy = []

    for f in files:

        f_lower = f.lower()

        # 🧠 BRAIN
        if "brain" in f_lower or "v88500" in f_lower or "decision" in f_lower:
            brain.append(f)

        # 🎛 CONTROL
        elif "control" in f_lower or "router" in f_lower or "orchestrator" in f_lower:
            control.append(f)

        # ⚙️ EXECUTION
        elif "executor" in f_lower or "upload" in f_lower or "feishu" in f_lower:
            execution.append(f)

        # 📊 DATA
        elif "data" in f_lower or "loader" in f_lower or "signal" in f_lower:
            data.append(f)

        # 🧨 LEGACY
        else:
            legacy.append(f)

    return {
        "brain": brain,
        "control": control,
        "execution": execution,
        "data": data,
        "legacy": legacy
    }


def save(mapping):
    with open("CODex_MAPPING.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)


if __name__ == "__main__":

    files = load_index()
    mapping = classify(files)

    save(mapping)

    print("✅ CODex STRUCTURE MAPPING COMPLETE")
    print("🧠 brain:", len(mapping["brain"]))
    print("🎛 control:", len(mapping["control"]))
    print("⚙️ execution:", len(mapping["execution"]))
    print("📊 data:", len(mapping["data"]))
    print("🧨 legacy:", len(mapping["legacy"]))
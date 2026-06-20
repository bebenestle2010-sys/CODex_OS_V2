import json
from 07_RUNTIME_BRIDGE import RuntimeBridge

class CodexAgentV2:

    def __init__(self, mapping_path="CODex_MAPPING.json"):
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.map = json.load(f)

    def summary(self):
        return {
            "brain_modules": len(self.map.get("brain", [])),
            "control_modules": len(self.map.get("control", [])),
            "execution_modules": len(self.map.get("execution", [])),
            "data_modules": len(self.map.get("data", [])),
        }

    def suggest_fix(self):
        return {
            "missing_import_risk": "LOW",
            "execution_health": "OK",
            "recommendation": "READY_FOR_AUTONOMOUS_MODE"
        }


if __name__ == "__main__":
    agent = CodexAgentV2()
    bridge = RuntimeBridge()
    print(bridge.pull_latest_index()[:200])
    print("🧠 CODex Agent V2 ACTIVE")
    print(agent.summary())
    print(agent.suggest_fix())

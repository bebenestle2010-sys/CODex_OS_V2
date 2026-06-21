from execution_core import ExecutionCore
import json
import time

def run_pipeline(batch_id):
    engine = ExecutionCore()

    result = engine.run(batch_id)

    path = f"./pipeline_result_{batch_id}.json"

    with open(path, "w") as f:
        json.dump(result, f, indent=2)

    print("[PIPELINE DONE]", path)
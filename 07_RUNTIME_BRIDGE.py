import subprocess
import sys
import os
from 03_EXECUTION.pipeline_executor import run_pipeline


# 添加 execution path（关键）
sys.path.append(os.path.join(os.path.dirname(__file__), "03_EXECUTION"))

from pipeline_executor import run_pipeline


class CODexRuntimeBridge:

    def __init__(self):
        self.status = "ACTIVE"

    def trigger_pipeline(self, batch_id, force=False):
        print("[RUNTIME BRIDGE] trigger pipeline:", batch_id)

        result = run_pipeline(batch_id)

        print("[RUNTIME BRIDGE DONE]", result)

        return result
class CODexRuntimeBridge:

    def __init__(self):
        self.status = "ACTIVE"

    def trigger_pipeline(self, batch_id, force=False):
        print("[BRIDGE] trigger pipeline:", batch_id)

        result = run_pipeline(batch_id)

        return result
class RuntimeBridge:

    def __init__(self, server="admin@47.82.217.49"):
        self.server = server

    def run_remote(self, cmd):
        ssh_cmd = f'ssh {self.server} "{cmd}"'
        print(f"🚀 executing: {ssh_cmd}")
        return subprocess.getoutput(ssh_cmd)

    def pull_latest_index(self):
        return self.run_remote(
            "cat /home/admin/CODEX_V2_EXTRACT/server_file_index.txt"
        )


if __name__ == "__main__":
    bridge = RuntimeBridge()
    print(bridge.pull_latest_index()[:300])
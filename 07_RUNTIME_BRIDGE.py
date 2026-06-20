import subprocess

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
from file_writer_agent import FileWriterAgent
from git_auto_deploy import GitAutoDeploy
from server_hot_reload import HotReload


class CodexOSController:

    @staticmethod
    def apply_patch(file_path: str, content: str):

        print("[V3.6] APPLY PATCH START")

        # 1. 写文件
        FileWriterAgent.write(file_path, content)

        # 2. Git提交
        GitAutoDeploy.deploy("v3.6 auto patch")

        # 3. 重启服务器
        HotReload.restart_server()

        print("[V3.6] COMPLETE ✔")


# 测试入口
if __name__ == "__main__":
    CodexOSController.apply_patch(
        "event_bus.py",
        "print('hello v3.6')"
    )

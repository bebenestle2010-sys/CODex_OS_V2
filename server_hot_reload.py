import os
import time

class HotReload:

    @staticmethod
    def restart_server():
        print("[HOT RELOAD] restarting server...")

        os.system("pkill -f main.py")
        time.sleep(1)
        os.system("nohup python3 main.py > kernel.log 2>&1 &")

        print("[HOT RELOAD] server restarted ✔")

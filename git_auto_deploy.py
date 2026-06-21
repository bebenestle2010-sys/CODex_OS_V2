import os

class GitAutoDeploy:

    @staticmethod
    def deploy(message="auto deploy v3.6"):
        os.system("git add .")
        os.system(f'git commit -m "{message}"')
        os.system("git push")
        print("[GIT DEPLOY] DONE ✔")

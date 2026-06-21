import os

class FileWriterAgent:

    @staticmethod
    def write(file_path: str, content: str):
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[AUTO-WRITE] {file_path} ✔")

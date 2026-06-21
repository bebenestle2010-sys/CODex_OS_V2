import time
from task_queue import pop
from pipeline_runner import run


def worker_loop():
    print("[WORKER] STARTED")

    while True:
        task = pop()

        if not task:
            time.sleep(1)
            continue

        print("[WORKER] GOT TASK:", task)

        try:
            run(task["files"])
            print("[WORKER] DONE")

        except Exception as e:
            print("[WORKER] ERROR:", e)


if __name__ == "__main__":
    worker_loop()

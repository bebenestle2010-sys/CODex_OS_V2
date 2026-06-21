import json
import os

QUEUE_FILE = "queue.jsonl"


def push(task):
    with open(QUEUE_FILE, "a") as f:
        f.write(json.dumps(task) + "\n")


def pop():
    if not os.path.exists(QUEUE_FILE):
        return None

    with open(QUEUE_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        return None

    task = json.loads(lines[0])

    with open(QUEUE_FILE, "w") as f:
        f.writelines(lines[1:])

    return task

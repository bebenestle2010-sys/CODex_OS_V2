# worker.py
"""CODex OS queue worker with environment diagnostics."""

from __future__ import annotations

import logging
import os
import time
from uuid import uuid4

from event_bus import EventBus
from pipeline_runner import run
from task_queue import ack, claim, nack


logger = logging.getLogger(__name__)


def log_environment_status() -> str:
    webhook_loaded = bool(os.getenv("FEISHU_WEBHOOK_URL"))
    open_id_loaded = bool(os.getenv("FEISHU_OPEN_ID_URL"))

    print(
        "[ENV] FEISHU_WEBHOOK_URL "
        + ("loaded" if webhook_loaded else "missing")
    )
    print(
        "[ENV] FEISHU_OPEN_ID_URL "
        + ("loaded" if open_id_loaded else "missing")
    )

    status = (
        "ENABLED"
        if webhook_loaded or open_id_loaded
        else "DISABLED"
    )
    print(f"[ENV] Feishu {status}")

    if not webhook_loaded:
        logger.warning(
            "[ENV] FEISHU_WEBHOOK_URL is unavailable"
        )

    if not open_id_loaded:
        logger.warning(
            "[ENV] FEISHU_OPEN_ID_URL is unavailable"
        )

    return status


def worker_loop(poll_interval: float = 1.0) -> None:
    log_environment_status()

    worker_id = f"{os.getpid()}-{uuid4().hex}"
    logger.info("[PIPELINE] START worker=%s", worker_id)

    while True:
        queue_claim = claim(worker_id)

        if queue_claim is None:
            time.sleep(poll_interval)
            continue

        task = queue_claim.task
        task_id = task.get("task_id", "unknown")

        logger.info("[PIPELINE] GOT TASK task_id=%s", task_id)
        logger.info("[PIPELINE] RUNNING task_id=%s", task_id)

        try:
            run(task["files"])
        except Exception:
            logger.exception(
                "[PIPELINE] FAILED task_id=%s",
                task_id,
            )

            try:
                nack(queue_claim)
            except Exception:
                logger.critical(
                    "[PIPELINE] NACK FAILED task_id=%s",
                    task_id,
                    exc_info=True,
                )

            continue

        logger.info("[PIPELINE] COMPLETED task_id=%s", task_id)

        try:
            ack(queue_claim)
        except Exception:
            logger.critical(
                "[PIPELINE] ACK FAILED task_id=%s",
                task_id,
                exc_info=True,
            )
            continue

        logger.info("[PIPELINE] ACK SENT task_id=%s", task_id)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    worker_loop()
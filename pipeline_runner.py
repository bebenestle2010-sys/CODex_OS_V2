"""Single production pipeline for CODex OS V4.0."""

from __future__ import annotations

import logging
from typing import Any

from brain import decision_engine
from event_bus import EventBus


logger = logging.getLogger(__name__)


def run(files: list[Any]) -> dict[str, Any]:
    if not isinstance(files, list):
        raise TypeError("files must be a list")

    logger.info(
        "[PIPELINE_RUNNER] START files_count=%d",
        len(files),
    )

    try:
        result = {
            "files": files,
            "brain": decision_engine(files),
            "status": "COMPLETED",
        }

        result["delivery"] = {
            "webhook": EventBus.send_webhook(result),
            "open_id": EventBus.send_open_id(result),
            "feishu_status": EventBus.runtime_status(),
        }
    except Exception:
        logger.exception("[PIPELINE_RUNNER] FAILED")
        raise

    logger.info(
        "[PIPELINE_RUNNER] END feishu_status=%s",
        EventBus.runtime_status(),
    )
    return result
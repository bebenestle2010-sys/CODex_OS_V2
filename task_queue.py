"""Atomic, crash-safe, multi-worker queue for CODex OS V4.0."""

from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4


logger = logging.getLogger(__name__)

QUEUE_ROOT = Path(
    os.getenv(
        "CODEX_QUEUE_DIR",
        str(Path(__file__).resolve().parent / "queue"),
    )
)
PENDING_DIR = QUEUE_ROOT / "pending"
PROCESSING_DIR = QUEUE_ROOT / "processing"
COMPLETED_DIR = QUEUE_ROOT / "completed"
FAILED_DIR = QUEUE_ROOT / "failed"

DEFAULT_LEASE_SECONDS = 300


@dataclass(frozen=True)
class QueueClaim:
    task: dict[str, Any]
    token: str


def _ensure_directories() -> None:
    for directory in (
        PENDING_DIR,
        PROCESSING_DIR,
        COMPLETED_DIR,
        FAILED_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    _ensure_directories()
    temporary_path: Optional[Path] = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=".tmp-",
            suffix=".json",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(data, temporary, ensure_ascii=False)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())

        os.replace(temporary_path, path)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def push(task: dict[str, Any]) -> str:
    if not isinstance(task, dict):
        raise TypeError("task must be a dictionary")

    stored_task = dict(task)
    stored_task.setdefault("task_id", uuid4().hex)
    queue_id = uuid4().hex
    destination = PENDING_DIR / f"{queue_id}.json"

    _atomic_write(destination, stored_task)
    logger.info(
        "[QUEUE] PUSHED task_id=%s queue_id=%s",
        stored_task["task_id"],
        queue_id,
    )
    return stored_task["task_id"]


def _original_filename(token: str) -> str:
    parts = token.split("__", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid queue claim token: {token}")
    return parts[2]


def recover_stale(
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
) -> int:
    _ensure_directories()
    recovered = 0
    cutoff_ns = time.time_ns() - (lease_seconds * 1_000_000_000)

    for claimed_path in PROCESSING_DIR.glob("*.json"):
        try:
            claimed_ns = int(claimed_path.name.split("__", 1)[0])
        except (ValueError, IndexError):
            logger.error(
                "[QUEUE] Invalid processing filename: %s",
                claimed_path.name,
            )
            continue

        if claimed_ns >= cutoff_ns:
            continue

        pending_path = PENDING_DIR / _original_filename(
            claimed_path.name
        )

        try:
            os.replace(claimed_path, pending_path)
            recovered += 1
            logger.warning(
                "[QUEUE] Recovered stale task %s",
                pending_path.name,
            )
        except FileNotFoundError:
            continue
        except OSError:
            logger.exception(
                "[QUEUE] Failed to recover stale task %s",
                claimed_path.name,
            )

    return recovered


def claim(
    worker_id: str,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
) -> Optional[QueueClaim]:
    _ensure_directories()
    recover_stale(lease_seconds)

    safe_worker_id = "".join(
        character
        for character in worker_id
        if character.isalnum() or character in "-_"
    )

    for pending_path in sorted(PENDING_DIR.glob("*.json")):
        token = (
            f"{time.time_ns()}__{safe_worker_id}__"
            f"{pending_path.name}"
        )
        claimed_path = PROCESSING_DIR / token

        try:
            os.replace(pending_path, claimed_path)
        except FileNotFoundError:
            continue
        except OSError:
            logger.exception(
                "[QUEUE] Failed to claim %s",
                pending_path.name,
            )
            continue

        try:
            with claimed_path.open("r", encoding="utf-8") as source:
                task = json.load(source)
        except Exception:
            failed_path = FAILED_DIR / _original_filename(token)
            try:
                os.replace(claimed_path, failed_path)
            finally:
                logger.exception(
                    "[QUEUE] Corrupt task moved to failed queue: %s",
                    token,
                )
            continue

        return QueueClaim(task=task, token=token)

    return None


def ack(queue_claim: QueueClaim) -> None:
    _ensure_directories()
    source = PROCESSING_DIR / queue_claim.token
    destination = COMPLETED_DIR / _original_filename(
        queue_claim.token
    )

    os.replace(source, destination)
    logger.info(
        "[QUEUE] ACK task_id=%s",
        queue_claim.task.get("task_id", "unknown"),
    )


def nack(queue_claim: QueueClaim) -> None:
    _ensure_directories()
    source = PROCESSING_DIR / queue_claim.token
    destination = PENDING_DIR / _original_filename(
        queue_claim.token
    )

    os.replace(source, destination)
    logger.warning(
        "[QUEUE] NACK task_id=%s",
        queue_claim.task.get("task_id", "unknown"),
    )
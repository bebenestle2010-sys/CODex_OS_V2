# event_bus.py
"""Feishu EventBus for CODex OS V4.0."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)


class EventDeliveryError(RuntimeError):
    """Raised when Feishu delivery fails after retries."""


class EventBus:
    RETRIES = 2
    TIMEOUT_SECONDS = 10

    TOKEN_URL = (
        "https://open.feishu.cn/open-apis/"
        "auth/v3/tenant_access_token/internal"
    )
    OPEN_ID_MESSAGE_URL = (
        "https://open.feishu.cn/open-apis/im/v1/messages"
        "?receive_id_type=open_id"
    )

    feishu_status = "DISABLED"
    _endpoint_status = {
        "webhook": "DISABLED",
        "open_id": "DISABLED",
    }

    _tenant_access_token: str | None = None
    _tenant_access_token_expires_at = 0.0

    @staticmethod
    def _env_loaded(name: str) -> bool:
        return bool(os.getenv(name))

    @classmethod
    def log_environment_status(cls) -> str:
        variables = (
            "FEISHU_WEBHOOK_URL",
            "FEISHU_APP_ID",
            "FEISHU_APP_SECRET",
            "FEISHU_OPEN_ID",
        )

        for name in variables:
            print(
                f"[ENV] {name} "
                f"{'loaded' if cls._env_loaded(name) else 'missing'}"
            )

        cls._endpoint_status["webhook"] = (
            "ENABLED"
            if cls._env_loaded("FEISHU_WEBHOOK_URL")
            else "DISABLED"
        )

        open_id_ready = all(
            cls._env_loaded(name)
            for name in (
                "FEISHU_APP_ID",
                "FEISHU_APP_SECRET",
                "FEISHU_OPEN_ID",
            )
        )
        cls._endpoint_status["open_id"] = (
            "ENABLED" if open_id_ready else "DISABLED"
        )

        cls._refresh_status()
        print(f"[ENV] Feishu {cls.feishu_status}")
        return cls.feishu_status

    @classmethod
    def _refresh_status(cls) -> None:
        statuses = set(cls._endpoint_status.values())

        if "FAILED" in statuses:
            cls.feishu_status = "FAILED"
        elif "ENABLED" in statuses:
            cls.feishu_status = "ENABLED"
        else:
            cls.feishu_status = "DISABLED"

    @classmethod
    def runtime_status(cls) -> str:
        cls._refresh_status()
        return cls.feishu_status

    @staticmethod
    def _validate_url(url: str, name: str) -> None:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"{name} is not a valid HTTP URL")

    @staticmethod
    def _check_feishu_result(
        channel: str,
        result: dict[str, Any],
    ) -> None:
        if "code" in result and result.get("code") != 0:
            raise EventDeliveryError(
                f"{channel} rejected by Feishu: {result}"
            )

        if (
            "StatusCode" in result
            and result.get("StatusCode") != 0
        ):
            raise EventDeliveryError(
                f"{channel} rejected by Feishu: {result}"
            )

    @classmethod
    def _request_json(
        cls,
        *,
        channel: str,
        status_key: str,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        cls._validate_url(url, channel)

        request_headers = {
            "Content-Type": "application/json; charset=utf-8",
        }
        if headers:
            request_headers.update(headers)

        encoded_payload = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

        total_attempts = cls.RETRIES + 1

        for attempt in range(1, total_attempts + 1):
            request = Request(
                url,
                data=encoded_payload,
                headers=request_headers,
                method="POST",
            )

            try:
                with urlopen(
                    request,
                    timeout=cls.TIMEOUT_SECONDS,
                ) as response:
                    response_text = response.read().decode(
                        "utf-8",
                        errors="replace",
                    )
                    status = response.getcode()

                if not 200 <= status < 300:
                    raise EventDeliveryError(
                        f"{channel} returned HTTP {status}"
                    )

                result = (
                    json.loads(response_text)
                    if response_text.strip()
                    else {}
                )
                cls._check_feishu_result(channel, result)

                cls._endpoint_status[status_key] = "ENABLED"
                cls._refresh_status()

                logger.info(
                    "[EVENTBUS] %s delivered on attempt %d",
                    channel,
                    attempt,
                )
                return result

            except HTTPError as error:
                try:
                    response_body = error.read().decode(
                        "utf-8",
                        errors="replace",
                    )
                except Exception:
                    response_body = ""

                message = (
                    f"HTTP {error.code}: "
                    f"{response_body or error.reason}"
                )

            except (
                URLError,
                TimeoutError,
                OSError,
                ValueError,
                EventDeliveryError,
                json.JSONDecodeError,
            ) as error:
                message = str(error)

            if attempt < total_attempts:
                logger.warning(
                    "[EVENTBUS] %s attempt %d/%d failed: %s",
                    channel,
                    attempt,
                    total_attempts,
                    message,
                )
                time.sleep(0.5 * attempt)
                continue

            cls._endpoint_status[status_key] = "FAILED"
            cls._refresh_status()

            logger.error(
                "[EVENTBUS] %s failed after %d attempts: %s",
                channel,
                total_attempts,
                message,
            )
            raise EventDeliveryError(
                f"{channel} failed after "
                f"{total_attempts} attempts: {message}"
            )

        raise AssertionError("Unreachable EventBus state")

    @classmethod
    def send_webhook(cls, data: Any) -> bool:
        webhook_url = os.getenv("FEISHU_WEBHOOK_URL")

        if not webhook_url:
            cls._endpoint_status["webhook"] = "DISABLED"
            cls._refresh_status()
            logger.warning(
                "[WEBHOOK] FEISHU_WEBHOOK_URL missing; skipped"
            )
            return False

        payload = {
            "msg_type": "text",
            "content": {
                "text": json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2,
                )
            },
        }

        cls._request_json(
            channel="webhook",
            status_key="webhook",
            url=webhook_url,
            payload=payload,
        )
        return True

    @classmethod
    def _get_tenant_access_token(cls) -> str:
        now = time.time()

        if (
            cls._tenant_access_token
            and now < cls._tenant_access_token_expires_at
        ):
            return cls._tenant_access_token

        app_id = os.getenv("FEISHU_APP_ID")
        app_secret = os.getenv("FEISHU_APP_SECRET")

        if not app_id or not app_secret:
            raise EventDeliveryError(
                "FEISHU_APP_ID or FEISHU_APP_SECRET missing"
            )

        result = cls._request_json(
            channel="tenant_token",
            status_key="open_id",
            url=cls.TOKEN_URL,
            payload={
                "app_id": app_id,
                "app_secret": app_secret,
            },
        )

        token = result.get("tenant_access_token")
        if not token:
            raise EventDeliveryError(
                "tenant_access_token missing in Feishu response"
            )

        expires_in = int(result.get("expire", 7200))
        cls._tenant_access_token = token
        cls._tenant_access_token_expires_at = (
            now + max(expires_in - 60, 60)
        )

        return token

    @classmethod
    def send_open_id(cls, data: Any) -> bool:
        open_id = os.getenv("FEISHU_OPEN_ID")
        app_id = os.getenv("FEISHU_APP_ID")
        app_secret = os.getenv("FEISHU_APP_SECRET")

        missing = [
            name
            for name, value in (
                ("FEISHU_OPEN_ID", open_id),
                ("FEISHU_APP_ID", app_id),
                ("FEISHU_APP_SECRET", app_secret),
            )
            if not value
        ]

        if missing:
            cls._endpoint_status["open_id"] = "DISABLED"
            cls._refresh_status()
            logger.warning(
                "[OPEN_ID] Missing %s; delivery skipped",
                ", ".join(missing),
            )
            return False

        token = cls._get_tenant_access_token()

        message = {
            "receive_id": open_id,
            "msg_type": "text",
            "content": json.dumps(
                {
                    "text": json.dumps(
                        data,
                        ensure_ascii=False,
                        indent=2,
                    )
                },
                ensure_ascii=False,
            ),
        }

        cls._request_json(
            channel="open_id",
            status_key="open_id",
            url=cls.OPEN_ID_MESSAGE_URL,
            payload=message,
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
        return True


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    EventBus.log_environment_status()
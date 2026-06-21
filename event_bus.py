import json
from typing import Any


class EventBus:

    @staticmethod
    def _http_post_stub(channel: str, data: Any) -> None:
        print(f"[EVENTBUS] HTTP STUB {channel}")

    @classmethod
    def send_webhook(cls, data: Any) -> None:
        print("[EVENTBUS] SEND WEBHOOK")
        print("[WEBHOOK]", json.dumps(data, ensure_ascii=False))

    @classmethod
    def send_open_id(cls, data: Any) -> None:
        print("[EVENTBUS] SEND OPEN_ID")
        print("[OPEN_ID]", json.dumps(data, ensure_ascii=False))

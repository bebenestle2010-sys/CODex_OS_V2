import json


class EventBus:

    @staticmethod
    def send_webhook(data):
        print("[WEBHOOK]", json.dumps(data, ensure_ascii=False))

    @staticmethod
    def send_open_id(data):
        print("[OPEN_ID]", json.dumps(data, ensure_ascii=False))

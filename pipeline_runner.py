from kernel import run_cycle
from event_bus import EventBus

def run(files):
    result = run_cycle(files)
    EventBus.send_webhook(result)
    EventBus.send_open_id(result)
    return result

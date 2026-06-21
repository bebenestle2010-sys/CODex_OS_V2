from event_bus import EventBus
from kernel import run_cycle
from brain import decision_engine


def run(files):
    result = run_cycle(files)

    # 🚀 V3.9 AI decision
    brain = decision_engine(files)

    result["brain"] = brain

    EventBus.send_webhook(result)
    EventBus.send_open_id(result)

    return result

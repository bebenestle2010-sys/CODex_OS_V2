class ExecutionCore:

    def __init__(self):
        self.status = "ACTIVE"

    def run(self, batch_id):
        print("[EXECUTION CORE] running batch:", batch_id)

        # mock execution
        result = {
            "batch_id": batch_id,
            "status": "completed",
            "orders": 0,
            "acos": 0.0
        }

        return result
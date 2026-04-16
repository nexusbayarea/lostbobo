import time


class Worker:
    def __init__(self, worker_id: str, kernel):
        self.worker_id = worker_id
        self.kernel = kernel

    def run_forever(self):
        while True:
            task = self.kernel.lease_task(self.worker_id)

            if not task:
                time.sleep(0.2)
                continue

            try:
                result = task.fn()
                self.kernel.report_success(task.id, result)

            except Exception as e:
                self.kernel.report_failure(task.id, str(e))

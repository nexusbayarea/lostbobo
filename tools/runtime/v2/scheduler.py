class Scheduler:
    def __init__(self, kernel):
        self.kernel = kernel

    def submit(self, task):
        self.kernel.add_task(task)

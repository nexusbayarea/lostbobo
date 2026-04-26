import asyncio


class FakeWorker:
    def __init__(self, queue, handler, timeout=1.0):
        self.queue = queue
        self.handler = handler
        self.running = False
        self.timeout = timeout

    async def run_once(self):
        job = await self.queue.dequeue()
        if not job:
            return False

        try:
            await asyncio.wait_for(self.handler(job), timeout=self.timeout)
            await self.queue.mark_success(job)

        except Exception as e:
            await self.queue.mark_failure(job, e)

        return True

    async def run(self):
        self.running = True
        try:
            while self.running:
                processed = await self.run_once()
                if not processed:
                    await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass

    def stop(self):
        self.running = False

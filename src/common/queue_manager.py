import asyncio
import logging
import time
import uuid
from collections import deque


class ChatRequest:
    def __init__(self, message: str, headers: dict):
        self.id = str(uuid.uuid4())
        self.message = message
        self.headers = headers
        self.arrival_time = time.time()

        self.future = asyncio.get_event_loop().create_future()


class RequestQueue:
    def __init__(self):
        self.queue = deque()

    def push(self, request: ChatRequest):
        self.queue.append(request)

    def pop_batch(self, max_batch_size=5) -> list[ChatRequest]:
        batch = []
        while self.queue and len(batch) < max_batch_size:
            batch.append(self.queue.popleft())
        return batch
request_queue = RequestQueue()

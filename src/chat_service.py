from vllm import LLM, SamplingParams
import asyncio
import time
import uuid
from collections import deque
from src.common.queue_manager import request_queue

class ChatRequest:
    def __init__(self, message: str,headers: dict):
        self.id = str(uuid.uuid4())
        self.message = message
        self.headers = headers
        self.arrival_time = time.time()
        self.start_time = None
        self.end_time = None
        self.batch_size = None
        self.group_size = None
        self.future = asyncio.get_event_loop().create_future()

class ChatService:
    def __init__(self):
        pass

    async def chat(self, chat_request: dict, headers: dict) -> str:
        req = ChatRequest(
            message=chat_request["message"],
            headers=headers
        )
        request_queue.push(req)
        result = await req.future
        return result



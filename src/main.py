from fastapi import FastAPI
from src.common.fastapi import FastAPIStarter
from src.chat.chat_router import ChatRouter
from typing import Protocol,Type
import uvicorn
from src.common.configuration import AppSettings
from src.common.model_manager import model_manager

app_starter=FastAPIStarter(title="vLLM API")
app=app_starter.app()

class RouterClass(Protocol):
    def __init__(self, app: FastAPI) -> None: ...

routers: list[Type[RouterClass]] = [
    ChatRouter,
]

for router in routers:
    router_instance = router(app)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=AppSettings.host,
        port=AppSettings.port,
        reload=True if AppSettings.app_env == "development" else False,
        workers=AppSettings.workers,
    )


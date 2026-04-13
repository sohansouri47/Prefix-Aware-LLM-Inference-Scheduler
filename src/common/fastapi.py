import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.common.scheduler import scheduler_loop
from src.common.model_manager import model_manager


class FastAPIStarter:
    def __init__(self, title: str):

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            print("Starting up the FastAPI application...")
            model_manager.init_model()
            scheduler_task = asyncio.create_task(scheduler_loop())
            try:
                yield
            finally:
                print("Shutting down the FastAPI application...")
                scheduler_task.cancel()
                try:
                    await scheduler_task
                except asyncio.CancelledError:
                    print("Scheduler stopped.")

        self._app = FastAPI(
            debug=False,
            title=title,
            lifespan=lifespan,
        )

    def app(self):
        return self._app

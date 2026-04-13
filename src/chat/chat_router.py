from fastapi import APIRouter, Depends, FastAPI, Request, status, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.chat.chat_service import ChatService


class ChatRouter:
    def __init__(self, app: FastAPI):
        self.app = app
        self.router = APIRouter()
        self.register_routes()
        self.include_router()

    def register_routes(self):
        self.router.post(
            "/chat",
            status_code=status.HTTP_200_OK,
        )(self.chat)

    def include_router(self):
        self.app.include_router(
            self.router,
            prefix="/api/v1",
            tags=["chat"]
        )

    async def chat(
        self,
        chat_request: dict,
        request: Request,
        request_id: str = Header(...),   # correct Header import
        chat_service: ChatService = Depends(ChatService)
    ) -> JSONResponse:

        headers = {
            "request-id": request_id
        }

        response = await chat_service.chat(chat_request, headers)

        return JSONResponse(
            content=jsonable_encoder({"response": response})
        )

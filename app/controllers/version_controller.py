from fastapi import Request
from fastapi.responses import JSONResponse
from app.helpers.handler import show_model

def get(request: Request) -> JSONResponse:
    data = {
        "version": "1.0.1",
        "server_name": request.headers.get("host"),
        "user_agent": request.headers.get("User-Agent"),
        "ip": request.client.host
    }
    return show_model(0, "ML Service", data)

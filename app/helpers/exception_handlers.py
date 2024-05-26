from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if exc.status_code == 404:
        data = {
            "error_code": 404,
            "message": "Data Not Found : " + exc.detail,
            "data": None,
        }
        return JSONResponse(data, status_code=200)
    elif exc.status_code == 401:  # Menggunakan "elif" bukan "elseif"
        data = {
            "error_code": 401,
            "message": exc.detail,
            "data": None,
        }
        return JSONResponse(data, status_code=200)
    else:
        data = {
            "error_code": 500,
            "message": exc.detail,
            "data": None,
        }
        return JSONResponse(data, status_code=200)

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse({"error": "Validation error", "details": exc.errors()}, status_code=422)

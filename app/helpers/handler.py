from typing import Any, Union
from fastapi.responses import JSONResponse

def show_model(error_code: int, message: str, data: Any) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "error_code": error_code,
            "data": data,
            "message": message,
        }
    )


def show_list_model(error_code: int, message: str, data: Any,
                    total_data: Union[int, str]) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "error_code": error_code,
            "data": data,
            "message": message,
            "total_data": total_data,
        }
    )

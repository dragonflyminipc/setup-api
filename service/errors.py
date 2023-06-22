from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi import Request
import logging

class ErrorResponse(BaseModel):
    message: str = Field(example="Example error message")
    code: str = Field(example="example_error")

errors = {
    "general": {
        "wrong-mac": ["Wrong mac address", 400],
    },
    "wifi": {
        "couldnt-connect": ["Couldn't connect to the wifi network", 400]
    }
}

class Abort(Exception):
    def __init__(self, scope: str, message: str):
        self.scope = scope
        self.message = message

async def abort_handler(request: Request, exc: Abort):
    error_code = exc.scope.replace("-", "_") + "_" + exc.message.replace("-", "_")

    try:
        error_message = errors[exc.scope][exc.message][0]
        status_code = errors[exc.scope][exc.message][1]
    except Exception:
        error_message = "Unknown error"
        status_code = 400

    logging.warning(f"Abort at {request.url.path}: {error_message}, {error_code}")

    return JSONResponse(
        content={"error": {
            "message": error_message, "code": error_code
        }, "data": {}},
        status_code=status_code
    )

async def validation_handler(request: Request, exc: RequestValidationError):
    exc_str = str(exc).replace("\n", " ").replace("   ", " ")
    return JSONResponse(
        content={"error": {
            "message": exc_str, "code": "validation_error"
        }, "data": {}},
        status_code=422
    )

from .plugin import *
from .loader import load_all
from .timers import timer
from fastapi.responses import JSONResponse

def e(message: str, code: int):
    return JSONResponse(
        content={
            "result": "failure",
            "reason": message
        },
        status_code=code,
        media_type="application/json"
    )
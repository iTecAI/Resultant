from .plugin import *
from .loader import load_all
from .timers import timer
from fastapi.responses import JSONResponse
import random, time, hashlib, base64


def e(message: str, code: int):
    return JSONResponse(
        content={"result": "failure", "reason": message},
        status_code=code,
        media_type="application/json",
    )


def clientToken():
    return base64.urlsafe_b64encode(
        hashlib.sha256(str(random.random() + time.time()).encode("utf-8"))
        .hexdigest()
        .encode("utf-8")
    ).decode("utf-8")[:12]

from .plugin import *
from .loader import load_all
from .timers import timer
from fastapi.responses import JSONResponse
import random, time, hashlib, base64
import os, json
import logging


def e(message: str, code: int):
    logging.debug(f"Request error {code} : {message}")
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

def conf():
    with open(
        (
            os.environ["RESULTANT_CONFIG"]
            if "RESULTANT_CONFIG" in os.environ.keys()
            else "_config.json"
        ),
        "r",
    ) as c:
        return json.load(c)

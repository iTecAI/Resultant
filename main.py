from plugins import *
from utils import load_all, timer, e
import json
from fastapi import FastAPI, Request
from tinydb import TinyDB
import os
from logging import basicConfig, debug, info, warning, error, critical, exception
from starlette.status import *

if __name__ == "__main__":
    print("Running tests...")
    with open("_config.json", "r") as f:
        config = json.load(f)
    plugins = load_all(config)

    print("DDG Plugin test [gurning, amazon]")
    ddg = plugins["ddg"]("Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0")
    r = timer(ddg.search, "[DDG - GURNING - 2 results - has noclick]", "gurning", count=2)
    print(json.dumps([i.formatted() for i in r], indent=4))
    r = timer(ddg.search, "[DDG - AMAZON - 30 results - no noclick]", "amazon", count=30)
    print(json.dumps([i.formatted() for i in r], indent=4))

    exit(0)

with open((os.environ["RESULTANT_CONFIG"] if "RESULTANT_CONFIG" in os.environ.keys() else "_config.json"), "r") as c:
    config = json.load(c)

basicConfig(
    level=config["logging"]["level"],
    format=config["logging"]["format"],
    style="{",
)

info("Server online.")

db = TinyDB(config["database"])
userDb = db.table("users")

app = FastAPI()

@app.middleware("http")
async def authenticate(request: Request, call_next):
    root = request.url.path.strip("/").split("/")[0]
    if root in ["theme", "open", ""]:
        return await call_next(request)
    
    if not "Authorization" in request.headers.keys():
        return e("Failed to authorize: No authentication token.", HTTP_400_BAD_REQUEST)
    
    token_raw = request.headers["Authorization"]
    if token_raw.split(" ")[0] != "Bearer" or len(token_raw.split(" ")) != 2:
        return e("Failed to authorize: Bad authentication header.", HTTP_400_BAD_REQUEST)
    
    

    
    

    



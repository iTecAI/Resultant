from plugins import *
from utils import load_all, timer, e, clientToken
import json
from fastapi import FastAPI, Request
from tinydb import TinyDB, where
import os
from logging import basicConfig, debug, info, warning, error, critical, exception
from starlette.status import *
from keycloak import Keycloak, Token, KeycloakError
from pydantic import BaseModel

if __name__ == "__main__":
    print("Running tests...")
    with open("_config.json", "r") as f:
        config = json.load(f)
    plugins = load_all(config)

    print("DDG Plugin test [gurning, amazon]")
    ddg = plugins["ddg"](
        "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
    )
    r = timer(
        ddg.search, "[DDG - GURNING - 2 results - has noclick]", "gurning", count=2
    )
    print(json.dumps([i.formatted() for i in r], indent=4))
    r = timer(
        ddg.search, "[DDG - AMAZON - 30 results - no noclick]", "amazon", count=30
    )
    print(json.dumps([i.formatted() for i in r], indent=4))

    exit(0)

with open(
    (
        os.environ["RESULTANT_CONFIG"]
        if "RESULTANT_CONFIG" in os.environ.keys()
        else "_config.json"
    ),
    "r",
) as c:
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

keycloak = Keycloak(
    config["keycloak"]["server"],
    config["keycloak"]["realm"],
    config["keycloak"]["clientId"],
    client_secret=(
        config["keycloak"]["secret"] if "secret" in config["keycloak"] else None
    ),
)


@app.middleware("http")
async def authenticate(request: Request, call_next):
    # Check if endpoint is unauthenticated
    root = request.url.path.strip("/").split("/")[0]
    if root in ["theme", "open", ""]:
        return await call_next(request)

    # Check validity of request
    if not "Authorization" in request.headers.keys():
        return e("Failed to authorize: No authentication token.", HTTP_400_BAD_REQUEST)

    token_raw = request.headers["Authorization"]
    if token_raw.split(" ")[0] != "Bearer" or len(token_raw.split(" ")) != 2:
        return e(
            "Failed to authorize: Bad authentication header.", HTTP_400_BAD_REQUEST
        )

    # Check token validity
    token_str = token_raw.split(" ")[1]
    results = userDb.search(where("clientToken") == token_str)
    if len(results) == 0:
        return e("Failed to authorize: Token not recognized.", HTTP_401_UNAUTHORIZED)

    # Check token expiry
    try:
        token: Token = keycloak.load_token(results[0])
        if not token.check_auth():
            return e("Failed to authorize: Token expired.", HTTP_401_UNAUTHORIZED)
    except KeycloakError:
        exception("Failed to login user with client id:\n")
        return e("Failed to authorize: Invalid token.", HTTP_401_UNAUTHORIZED)

    # Check token scope
    if not token.is_scoped(config["keycloak"]["requiredScope"]):
        return e(
            "Failed to authorize: Not authorized to access endpoint", HTTP_403_FORBIDDEN
        )

    if root in config["keycloak"]["specificScopes"].keys():
        if not token.is_scoped(config["keycloak"]["specificScopes"]["root"]):
            return e(
                "Failed to authorize: Not authorized to access endpoint",
                HTTP_403_FORBIDDEN,
            )

    request.state.token = token
    return await call_next(request)


class LoginModel(BaseModel):
    username: str
    password: str


@app.post("/login")
async def post_login(model: LoginModel):
    try:
        token: Token = keycloak.auth(model.username, model.password)
    except KeycloakError:
        return e("Failed to authenticate: bad login", HTTP_403_FORBIDDEN)

    if not token.is_scoped(config["keycloak"]["requiredScope"]):
        return e(
            "Failed to authorize: Not authorized to access application",
            HTTP_403_FORBIDDEN,
        )

    token.content["clientToken"] = clientToken()
    userDb.insert(token.content)
    return {
        "result": "success",
        "clientToken": token.content["clientToken"],
        "userInfo": token.info(),
    }

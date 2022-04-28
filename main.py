from plugins import *
from utils import load_all, timer, e, clientToken, conf
import json
from fastapi import FastAPI, Request
from tinydb import TinyDB, where
import os
from logging import basicConfig, debug, info, warning, error, critical, exception
from starlette.status import *
from keycloak import Keycloak, Token, KeycloakError
from pydantic import BaseModel
from fastapi_restful.tasks import repeat_every
import time
from api.user import router as UserRouter
from api.search import router as SearchRouter

config = conf()

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
    # debug(f"Got request to {request.url.path} with headers:\n{json.dumps(request.headers.items(), indent=4)}")

    # Check if endpoint is unauthenticated
    root = request.url.path.strip("/").split("/")[0]
    if root in ["theme", "open", "", "login", "redoc"]:
        return await call_next(request)

    # Check validity of request
    if not "authorization" in request.headers.keys():
        return e("Failed to authorize: No authentication token.", HTTP_400_BAD_REQUEST)

    token_raw = request.headers["authorization"]
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
    token.content["userInfo"] = token.info().to_dict()
    userDb.insert(token.content)
    return {
        "result": "success",
        "clientToken": token.content["clientToken"],
        "userInfo": token.content["userInfo"],
    }


@app.on_event("startup")
@repeat_every(seconds=60 * config["keycloak"]["refreshInterval"])
def refresh_idle_tokens():
    """
    Refresh all tokens provided that they have not been idle for more than [config.keycloak.maxIdleLength] minutes.
    Removes expired/idle tokens
    Repeats every [config.keycloak.refreshInterval] minutes
    """
    for t in userDb.all():
        if t["last_auth"] + config["keycloak"]["maxIdleLength"] * 60 < time.time():
            info(
                f"Token with clientToken {t['clientToken']} has idled for too long. Removing."
            )
            userDb.remove(where("clientToken") == t["clientToken"])
            continue
        token: Token = keycloak.load_token(t)
        if not token.check_auth():
            info(
                f"Token with clientToken {token.content['clientToken']} has expired. Removing."
            )
            userDb.remove(where("clientToken") == t["clientToken"])
            continue


@app.get("/theme/{theme}")
async def get_theme(theme: str):
    with open(config["themes"], "r") as f:
        thm = json.load(f)
        if theme in thm.keys():
            return {"--" + k: v for k, v in thm[theme].items()}
        else:
            return e(
                f"Failed to locate theme {theme}. Available themes are [{', '.join(thm.keys())}]",
                HTTP_404_NOT_FOUND,
            )


app.include_router(UserRouter)
app.include_router(SearchRouter)
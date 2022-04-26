from fastapi import APIRouter, Request
from utils import *
from starlette.status import *
from keycloak import Token, KeycloakError
from logging import warning, info, error, exception

config = conf()

router = APIRouter(prefix="/user", tags=["users", "authenticated"])

@router.get("/info")
async def get_user_info(request: Request):
    token: Token = request.state.token
    try:
        return {"result": "success", "info": token.info().to_dict()}
    except KeycloakError:
        exception(f"Token {token.content['clientToken']} failed to retrieve user info:\n")
        return e("Unexpected error occurred.", HTTP_500_INTERNAL_SERVER_ERROR)

@router.post("/logout")
async def logout(request: Request):
    token: Token = request.state.token
    try:
        info(f"Token {token.content['clientToken']} logged out.")
        token.logout()
        return {"result": "success"}
    except KeycloakError:
        exception(f"Token {token.content['clientToken']} failed to log out:\n")
        return e("Unexpected error occurred.", HTTP_500_INTERNAL_SERVER_ERROR)
from typing import Any
from fastapi import APIRouter, Request
from utils import *
from starlette.status import *
from keycloak import Token, KeycloakError
from logging import warning, info, error, exception, debug
from tinydb import TinyDB, where

config = conf()
searchDb = TinyDB(config["database"]).table("search")

router = APIRouter(prefix="/search", tags=["search", "authenticated"])

plugins: dict[str, Plugin] = load_all(config)


class UserSearchData:
    DEFAULT = {
        "email": "",
        "recent": [],
        "pluginsActive": config["plugins"]["pluginList"],
    }

    def __init__(self, content: dict = {}):
        self.content = content
        for k, v in self.DEFAULT.items():
            if not k in self.content.keys():
                self.content[k] = v

    @property
    def recent(self) -> list[str]:
        return self.content["recent"]

    @property
    def plugins(self) -> dict[str, dict[str, Any]]:
        return {
            p: plugins[p].get_info()
            for p in self.content["pluginsActive"]
        }

    @property
    def email(self):
        return self.content["email"]


def userSearchDataEmail(email: str) -> UserSearchData:
    """Gets user search data based on email

    Args:
        email (str): User email

    Returns:
        UserSearchData: User Search Data
    """
    results = searchDb.search(where("email") == email)
    if len(results) > 0:
        return UserSearchData(content=results[0])
    else:
        data = UserSearchData(content={"email": email})
        searchDb.insert(data.content)
        return data


def userSearchData(r: Request) -> UserSearchData:
    return userSearchDataEmail(r.state.token.content["userInfo"]["email"])


@router.get("/plugins")
async def get_plugins(r: Request):
    data = userSearchData(r)
    return data.plugins

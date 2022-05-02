from typing import Any
from fastapi import APIRouter, Request
from utils import *
from starlette.status import *
from keycloak import Token, KeycloakError
from logging import warning, info, error, exception, debug
from tinydb import TinyDB, where
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor

config = conf()
searchDb = TinyDB(config["database"]).table("search")

router = APIRouter(prefix="/search", tags=["search", "authenticated"])

plugins: dict[str, Plugin] = load_all(config)


class UserSearchData:
    DEFAULT = {
        "email": "",
        "recent": [],
        "pluginsActive": config["plugins"]["pluginList"],
        "pluginSettings": config["plugins"]["pluginOptions"]
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
    def plugins(self) -> dict:
        return {
            p: {
                "info": plugins[p].get_info(),
                "settings": self.content["pluginSettings"][p],
                "active": p in self.content["pluginsActive"]
            }
            for p in plugins.keys()
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

class SettingsUpdateModel(BaseModel):
    settings: dict

@router.post("/plugins/{plugin}/settings")
async def update_plugin_settings(r: Request, plugin: str, model: SettingsUpdateModel):
    data = userSearchData(r).content
    if "active" in model.settings.keys():
        active = model.settings.pop("active")
    else:
        active = plugin in data["pluginsActive"]
    if plugin in data["pluginSettings"].keys():
        data["pluginSettings"][plugin] = model.settings
        if active and not plugin in data["pluginsActive"]: data["pluginsActive"].append(plugin)
        if not active and plugin in data["pluginsActive"]: data["pluginsActive"].remove(plugin)
            
        debug(f"Updating {data['email']} settings for {plugin} to {json.dumps(model.settings)}")
        searchDb.update({"pluginSettings": data["pluginSettings"], "pluginsActive": data["pluginsActive"]}, where("email") == data["email"])
        return {"result": "success"}
    else:
        return e(f"Plugin {plugin} not found.", HTTP_404_NOT_FOUND)

@router.get("/")
async def search_initialize(r: Request, query: str):
    data = userSearchData(r)
    schema = {
        "root": [],
        "tabs": []
    }
    for p in data.plugins.values():
        if p["active"]:
            if p["info"]["isTab"]:
                schema["tabs"].append({
                    "tab": p["info"]["name"],
                    "display": p["info"]["displayName"],
                    "icon": p["info"]["icon"],
                    "url": f"/search/results/{p['info']['name']}/?q={query}"
                })
            else:
                schema["root"].append({
                    "name": p["info"]["name"],
                    "icon": p["info"]["icon"],
                    "url": f"/search/results/{p['info']['name']}/?q={query}"
                })
    return schema



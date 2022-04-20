import requests
from utils.plugin import Plugin, SearchError
from urllib.parse import quote
from bs4 import BeautifulSoup

class DuckDuckGo(Plugin):
    NAME: str = "ddg"
    DISPLAY_NAME = "DuckDuckGo"
    DISPLAY_ICON = ["mdi", "duck"]
    TAB: bool = False
    EXPOSED_OPTIONS: list[dict] = []

    def __init__(self, user_agent) -> None:
        super().__init__(user_agent)
        self.headers = {
            "Host": "html.duckduckgo.com",
            "Origin": "https://html.duckduckgo.com",
            "Referer": "https://html.duckduckgo.com/",
            "User-Agent": self.user_agent,
            "Cookie": "kl=wt-wt",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }
        self.url_base = "https://html.duckduckgo.com/html/?q={query}"

    def search(self, query: str, options: list[dict] = {}) -> list[dict]:
        response = requests.get(self.url_base.format(query=quote(query, safe="")), headers=self.headers)
        if response.status_code != 200:
            raise SearchError(f"DDG Search Attempt failed (Error {response.status_code})")
        
        soup = BeautifulSoup(markup=response.text, features="html.parser")
        resElements = soup.select(".result.web-result > .links_main")
        results = []
        for r in resElements:
            results.append({
                "link": r.select_one("h2 a").attrs["href"],
                "title": r.select_one("h2 a").find(text=True, recursive=False).strip(),
                "icon": "https:" + r.select_one(".result__icon__img").attrs["src"],
                "snippet": r.select_one(".result__snippet").find(text=True, recursive=False).strip()
            })
        
        if len(soup.select(".zci")) > 0:
            noclick = {
                "type": "definition",
                "heading": soup.select_one(".zci .zci__heading a").find(text=True, recursive=False).strip(),
                "link": soup.select_one(".zci__heading a").attrs["href"],
                "content": soup.select_one(".zci .zci__result").find(text=True, recursive=False).strip()
            }
        else:
            noclick = None
        return {
            "results": results,
            "noclick": noclick
        }


# Plugin info
PLUGIN: Plugin = DuckDuckGo
__all__ = ["PLUGIN"]
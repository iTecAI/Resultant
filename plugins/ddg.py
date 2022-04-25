import requests
from utils.plugin import Plugin, SearchError, SearchResult
from urllib.parse import quote
from bs4 import BeautifulSoup

class DDGResult(SearchResult):
    TYPE: str = "ddg_sr"
    def __init__(self, link: str, title: str, icon: str, snippet: str):
        super().__init__(DuckDuckGo, link=link, title=title, icon=icon, snippet=snippet)
    
    def formatted(self):
        return {
            "type": self.TYPE,
            "location": "main",
            "actions": [
                {
                    "type": "link",
                    "target": self.link
                }
            ],
            "elements": [
                {
                    "type": "header",
                    "value": self.title
                },
                {
                    "type": "subtitle",
                    "hasImage": True,
                    "image": self.icon,
                    "value": self.link
                },
                {
                    "type": "description",
                    "value": self.snippet
                }
            ]
        }

class DDGNoClick(SearchResult):
    TYPE: str = "ddg_noclick"
    def __init__(self, heading: str, link: str, content: str):
        super().__init__(DuckDuckGo, heading=heading, link=link, content=content)
    
    def formatted(self):
        return {
            "type": self.TYPE,
            "location": "noclick",
            "actions": [
                {
                    "type": "link",
                    "target": self.link
                }
            ],
            "elements": [
                {
                    "type": "header",
                    "value": self.heading
                },
                {
                    "type": "description",
                    "value": self.content
                }
            ]
        }

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
        self.headers_post = {
            "Host": "html.duckduckgo.com",
            "Origin": "https://html.duckduckgo.com",
            "Referer": "https://html.duckduckgo.com/",
            "User-Agent": self.user_agent,
            "Cookie": "kl=wt-wt",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "TE": "trailers",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1"
        }
        self.url_base = "https://html.duckduckgo.com/html/"

    def search(self, query: str, options: list[dict] = {}, count: int = -1) -> list[SearchResult]:
        response = requests.get(self.url_base, headers=self.headers, params={"q": quote(query, safe="")})
        if response.status_code != 200:
            raise SearchError(f"DDG Search Attempt failed (Error {response.status_code})")
        
        soup = BeautifulSoup(markup=response.text, features="html.parser")
        resElements = soup.select(".result.web-result > .links_main")

        if len(resElements) < count and count >= -1:
            while len(resElements) < count:
                form = soup.select_one(".nav-link form")
                formData = {e["name"]: e["value"] for e in form.find_all("input", attrs={"type": "hidden"})}
                response = requests.post(self.url_base, headers=self.headers_post, data=formData)

                if response.status_code != 200:
                    print(f"Error {response.status_code}:\n{response.text}\n")
                    break
                soup = BeautifulSoup(markup=response.text, features="html.parser")
                items = soup.select(".result.web-result > .links_main")
                if len(items) == 0:
                    print("out of results")
                    break
                resElements.extend(soup.select(".result.web-result > .links_main"))
        if len(resElements) > count:
            resElements = resElements[:count]


        results = []
        for r in resElements:
            snippet = r.select_one(".result__snippet")
            results.append(DDGResult(
                r.select_one("h2 a").attrs["href"],
                r.select_one("h2 a").find(text=True, recursive=False).strip(),
                "https:" + r.select_one(".result__icon__img").attrs["src"],
                snippet.find(text=True, recursive=False).strip() if snippet else ""
            ))
        
        if len(soup.select(".zci")) > 0:
            noclick = DDGNoClick(
                soup.select_one(".zci .zci__heading a").find(text=True, recursive=False).strip(),
                soup.select_one(".zci__heading a").attrs["href"],
                soup.select_one(".zci .zci__result").find(text=True, recursive=False).strip()
            )
            results.append(noclick)
        return results


# Plugin info
PLUGIN: Plugin = DuckDuckGo
__all__ = ["PLUGIN"]
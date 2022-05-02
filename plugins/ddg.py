if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.realpath("."))
    print(sys.path)

import requests
from utils.plugin import Plugin, SearchError, SearchResult
from urllib.parse import quote
from utils import timer
from bs4 import BeautifulSoup
import json


class DDGResult(SearchResult):
    TYPE: str = "ddg_sr"

    def __init__(self, link: str, title: str, icon: str, snippet: str):
        super().__init__(DuckDuckGo, link=link, title=title, icon=icon, snippet=snippet)

    def formatted(self):
        return {
            "type": self.TYPE,
            "location": "main",
            "actions": [{"type": "link", "target": self.link}],
            "elements": [
                {"type": "header", "value": self.title},
                {
                    "type": "subtitle",
                    "hasImage": True,
                    "image": self.icon,
                    "value": self.link,
                },
                {"type": "description", "value": self.snippet},
            ],
        }


class DDGNoClick(SearchResult):
    TYPE: str = "ddg_noclick"

    def __init__(self, heading: str, link: str, content: str):
        super().__init__(DuckDuckGo, heading=heading, link=link, content=content)

    def formatted(self):
        return {
            "type": self.TYPE,
            "location": "noclick",
            "actions": [{"type": "link", "target": self.link}],
            "elements": [
                {"type": "header", "value": self.heading},
                {"type": "description", "value": self.content},
            ],
        }


class DuckDuckGo(Plugin):
    NAME: str = "ddg"
    DISPLAY_NAME = "DuckDuckGo"
    DISPLAY_ICON = ["mdi", "duck"]
    TAB: bool = False
    EXPOSED_OPTIONS: list[dict] = [
        {
            "name": "region",
            "displayName": "Region",
            "type": "select",
            "icon": ["mdi", "earth"],
            "options": {
                "$null": "All Regions",
                "ar-es": "Argentina",
                "at-de": "Austria",
                "au-en": "Australia",
                "be-fr": "Belgium (fr)",
                "be-nl": "Belgium (nl)",
                "bg-bg": "Bulgaria",
                "br-pt": "Brazil",
                "ca-en": "Canada (en)",
                "ca-fr": "Canada (fr)",
                "ch-de": "Switzerland (de)",
                "ch-fr": "Switzerland (fr)",
                "cl-es": "Chile",
                "cn-zh": "China",
                "co-es": "Colombia",
                "ct-ca": "Catalonia",
                "cz-cs": "Czech Republic",
                "de-de": "Germany",
                "dk-da": "Denmark",
                "ee-et": "Estonia",
                "es-ca": "Spain (ca)",
                "es-es": "Spain (es)",
                "fi-fi": "Finland",
                "fr-fr": "France",
                "gr-el": "Greece",
                "hk-tzh": "Hong Kong",
                "hr-hr": "Croatia",
                "hu-hu": "Hungary",
                "id-en": "Indonesia (en)",
                "ie-en": "Ireland",
                "il-en": "Israel (en)",
                "in-en": "India (en)",
                "it-it": "Italy",
                "jp-jp": "Japan",
                "kr-kr": "Korea",
                "lt-lt": "Lithuania",
                "lv-lv": "Latvia",
                "mx-es": "Mexico",
                "my-en": "Malaysia (en)",
                "nl-nl": "Netherlands",
                "no-no": "Norway",
                "nz-en": "New Zealand",
                "pe-es": "Peru",
                "ph-en": "Philippines (en)",
                "pk-en": "Pakistan (en)",
                "pl-pl": "Poland",
                "pt-pt": "Portugal",
                "ro-ro": "Romania",
                "ru-ru": "Russia",
                "se-sv": "Sweden",
                "sg-en": "Singapore",
                "sk-sk": "Slovakia",
                "sl-sl": "Slovenia",
                "th-en": "Thailand (en)",
                "tr-tr": "Turkey",
                "tw-tzh": "Taiwan",
                "ua-uk": "Ukraine",
                "uk-en": "United Kingdom",
                "us-en": "US (English)",
                "us-es": "US (Spanish)",
                "vn-en": "Vietnam (en)",
                "xa-ar": "Saudi Arabia",
                "za-en": "South Africa",
            },
        },
        {
            "name": "time",
            "displayName": "Time",
            "type": "select",
            "icon": ["mdi", "clock"],
            "options": {
                "$null": "Any Time",
                "d": "Past Day",
                "w": "Past Week",
                "m": "Past Month",
                "y": "Past Year"
            }
        }
    ]
    METHODS: list[str] = ["search", "suggest"]

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
            "Sec-Fetch-User": "?1",
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
            "DNT": "1",
        }
        self.headers_suggest = {
            "Host": "duckduckgo.com",
            "Origin": "https://duckduckgo.com",
            "Referer": "https://duckduckgo.com/",
            "User-Agent": self.user_agent,
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }
        self.url_base = "https://html.duckduckgo.com/html/"
        self.url_base_suggest = "https://duckduckgo.com/ac/"

    def search(
        self, query: str, options: dict = {}, count: int = -1
    ) -> list[SearchResult]:
        params = {"q": quote(query, safe="")}
        if "region" in options.keys():
            params["kl"] = options["region"]
        if "time" in options.keys():
            params["df"] = options["time"]

        response = requests.get(
            self.url_base, headers=self.headers, params=params
        )
        if response.status_code != 200:
            raise SearchError(
                f"DDG Search Attempt failed (Error {response.status_code} : {response.text})"
            )

        soup = BeautifulSoup(markup=response.text, features="html.parser")
        resElements = soup.select(".result.web-result > .links_main")

        if len(resElements) < count and count >= -1:
            while len(resElements) < count:
                form = soup.select_one(".nav-link form")
                formData = {
                    e["name"]: e["value"]
                    for e in form.find_all("input", attrs={"type": "hidden"})
                }
                response = requests.post(
                    self.url_base, headers=self.headers_post, data=formData
                )

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
            results.append(
                DDGResult(
                    r.select_one("h2 a").attrs["href"],
                    r.select_one("h2 a").find(text=True, recursive=False).strip(),
                    "https:" + r.select_one(".result__icon__img").attrs["src"],
                    snippet.find(text=True, recursive=False).strip() if snippet else "",
                )
            )

        if len(soup.select(".zci")) > 0:
            noclick = DDGNoClick(
                soup.select_one(".zci .zci__heading a")
                .find(text=True, recursive=False)
                .strip(),
                soup.select_one(".zci__heading a").attrs["href"],
                soup.select_one(".zci .zci__result")
                .find(text=True, recursive=False)
                .strip(),
            )
            results.append(noclick)
        return results
    
    def suggest(self, query: str, options: dict = {}) -> list[str]:
        params = {"q": quote(query, safe="")}
        if "region" in options.keys():
            params["kl"] = options["region"]
        else:
            params["kl"] = "wt-wt"
        
        resp = requests.get(self.url_base_suggest, params=params, headers=self.headers_suggest)
        print(resp.url)
        if resp.status_code != 200:
            raise SearchError(
                f"DDG Search Attempt failed (Error {resp.status_code} : {resp.text})"
            )
        
        return [s["phrase"] for s in resp.json() if "phrase" in s.keys()]

# Plugin info
PLUGIN: Plugin = DuckDuckGo
__all__ = ["PLUGIN"]

if __name__ == "__main__":
    print("DDG Plugin test [gurning, amazon]")
    ddg: DuckDuckGo = DuckDuckGo(
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
    r = timer(
        ddg.search,
        "[DDG - WIKIPEDIA - 30 results - Argentina past week]",
        "wikipedia",
        count=30,
        options={"region": "ar-es", "time": "w"},
    )
    print(json.dumps([i.formatted() for i in r], indent=4))
    r = timer(ddg.suggest, '[DDG - Suggest "te"]', "te")
    print(r)

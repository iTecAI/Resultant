from plugins import *
from utils import load_all, timer
import json
from fastapi import FastAPI

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

app = FastAPI()
    



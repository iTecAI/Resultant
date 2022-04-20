from plugins import *
from utils import load_all
import json

TEST = True

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)
    plugins = load_all(config)

    if TEST:
        print("DDG Plugin test [gurning]")
        ddg = plugins["ddg"]("Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0")
        print(json.dumps(ddg.search("gurning"), indent=4))
        print(json.dumps(ddg.search("amazon"), indent=4))

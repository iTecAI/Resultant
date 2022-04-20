class Plugin:
    NAME: str = "" # Technical name (Unique)
    DISPLAY_NAME: str = "" # Display name
    DISPLAY_ICON: list[str] = ["mdi", "search_web"] # Icon specification
    TAB: bool = True # Whether this plugin should appear in a separate tab
    EXPOSED_OPTIONS: list[dict] = [];

    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent
    
    def search(self, query: str, options: list[dict] = {}) -> list[dict]:
        return []

class SearchError(ConnectionError):
    pass
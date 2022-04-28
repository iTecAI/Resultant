class Plugin:
    NAME: str = "" # Technical name (Unique)
    DISPLAY_NAME: str = "" # Display name
    DISPLAY_ICON: list[str] = ["mdi", "search_web"] # Icon specification
    TAB: bool = True # Whether this plugin should appear in a separate tab
    EXPOSED_OPTIONS: list[dict] = [] # Options
    METHODS: list[str] = ["search"] # Methods exposed

    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent
    
    def search(self, query: str, options: list[dict] = {}, count: int = -1) -> list[dict]:
        return []
    
    def get_info(self):
        return {
            "name": self.NAME,
            "displayName": self.DISPLAY_NAME,
            "icon": self.DISPLAY_ICON,
            "isTab": self.TAB,
            "options": self.EXPOSED_OPTIONS,
            "methods": self.METHODS
        }

class SearchResult:
    TYPE: str = "default"
    def __init__(self, plugin: Plugin, **kwargs):
        self.plugin = plugin
        self.params = kwargs
    
    def __getattr__(self, item: str):
        if (item in self.params.keys()):
            return self.params[item]
        else:
            raise AttributeError(f"'{self.__name__}' object has no attribute '{item}'")
    
    def formatted(self):
        return {}

class SearchError(ConnectionError):
    pass
from .dataclass import Dataclass

class AccessToken(Dataclass):    
    @property
    def token(self) -> str:
        return self.content["access_token"]
    
    @property
    def expires(self) -> str:
        return self.content["expires_in"]

    @property
    def refresh_expires(self) -> str:
        return self.content["refresh_expires_in"]
    
    @property
    def token_refresh(self) -> str:
        return self.content["refresh_token"]

    @property
    def token_type(self) -> str:
        return self.content["token_type"]
    
    @property
    def not_before_policy(self) -> int:
        return self.content["not-before-policy"]
    
    @property
    def session_state(self) -> str:
        return self.content["session_state"]
    
    @property
    def scope(self) -> list[str]:
        return self.content["scope"].split(" ")
    
    def make_auth_header(self) -> str:
        """Makes auth header

        Returns:
            str: <token type> <token> (Example: "Bearer 12345asdfg")
        """
        return self.token_type + " " +self.token
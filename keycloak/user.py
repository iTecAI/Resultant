from .dataclass import Dataclass
class UserInfo(Dataclass):
    @property
    def sub(self) -> str:
        return self.content["sub"]
    
    @property
    def email(self) -> str:
        return self.content["email"]
    
    @property
    def email_verified(self) -> bool:
        return self.content["email_verified"]
    
    @property
    def name(self) -> str:
        return self.content["name"]
    
    @property
    def name_parts(self) -> tuple[str]:
        return self.content["given_name"], self.content["family_name"]
    
    @property
    def username(self) -> str:
        return self.content["preferred_username"]
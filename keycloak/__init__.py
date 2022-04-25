import requests
from urllib.parse import quote

from .token import AccessToken
from .user import *

class KeycloakError(Exception):
    pass

class KeycloakConnectionError(KeycloakError):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"Request to keycloak failed with code {code}: {message}")

def formencode(data: dict):
    return "&".join([quote(k) + "=" + quote(v) for k, v in data.items()])

class Keycloak:
    def __init__(
        self,
        server_url: str,
        realm: str,
        client_id: str,
        client_secret: str = None,
        well_known: str = "/realms/{realm}/.well-known/openid-configuration",
    ):
        """Keycloak Constructor

        Args:
            server_url (str): URL of server [http(s)://host:port]
            realm (str): Name of Keycloak Realm
            client_id (str): Client ID to use
            client_secret (str, optional): Client secret, if present. Defaults to None.
            well_known (str, optional): Alternate URL to well_known page. Defaults to "/realms/sso/.well-known/openid-configuration".
        """

        # Set basic parameters
        self.server_url = server_url.rstrip("/") + "{path}"
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self._wellknown_url = well_known

        # Get Well-Known data
        resp = requests.get(self.server_url.format(path=well_known.format(realm=self.realm)))
        if resp.status_code >= 400:
            raise KeycloakConnectionError(resp.status_code, resp.text)
        
        self._wk_all = resp.json()

        self.endpoint_token = self._wk_all["token_endpoint"]
        self.endpoint_userinfo = self._wk_all["userinfo_endpoint"]
        self.endpoint_logout = self._wk_all["end_session_endpoint"]

        self.current_token: AccessToken = None
    
    @property
    def authenticated(self) -> bool:
        return bool(self.current_token)

    def login(self, username: str, password: str) -> AccessToken:
        """Logs user into Keycloak

        Args:
            username (str): Username
            password (str): Password

        Raises:
            KeycloakConnectionError: Raised on an unspecified connection error

        Returns:
            AccessToken: Access Token
        """
        
        headers = {
            "Content-type": "application/x-www-form-urlencoded"
        }
        if self.client_secret:
            resp = requests.post(self.endpoint_token, data=formencode({
                "grant_type": "password",
                "username": username,
                "password": password,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }), headers=headers)
        else:
            resp = requests.post(self.endpoint_token, data=formencode({
                "grant_type": "password",
                "username": username,
                "password": password,
                "client_id": self.client_id,
            }), headers=headers)

        if resp.status_code >= 400:
            raise KeycloakConnectionError(resp.status_code, resp.text)
        self.current_token = AccessToken(resp.json())
        return self.current_token
    
    def userinfo(self) -> UserInfo:
        """Get User Info of user

        Raises:
            KeycloakError: Raised if not logged in
            KeycloakConnectionError: Raised if an unspecified server error occurs

        Returns:
            UserInfo: User Info object
        """
        if not self.authenticated:
            raise KeycloakError("Not authenticated. Run login() first.")
        resp = requests.get(self.endpoint_userinfo, headers={
            "Authorization": self.current_token.make_auth_header()
        })
        if resp.status_code >= 400:
            raise KeycloakConnectionError(resp.status_code, resp.text)
        
        return UserInfo(resp.json())
    
    def is_scoped(self, scope: str) -> bool:
        """Checks if current token has scope

        Args:
            scope (str): Scope to check

        Raises:
            KeycloakError: Raised if client is not authenticated

        Returns:
            bool: True if client has scope
        """
        if not self.authenticated:
            raise KeycloakError("Not authenticated. Run login() first.")
        return scope in self.current_token.scope
    
    
    def logout(self) -> None:
        """Logs out from keycloak

        Raises:
            KeycloakError: Raised if not logged in
            KeycloakConnectionError: Raised if an unexpected error occurs
        """
        if not self.authenticated:
            raise KeycloakError("Not authenticated. Run login() first.")
        
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Authorization": self.current_token.make_auth_header()
        }
        if self.client_secret:
            resp = requests.post(self.endpoint_logout, data=formencode({
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token":self.current_token.token_refresh
            }), headers=headers)
        else:
            resp = requests.post(self.endpoint_logout, data=formencode({
                "client_id": self.client_id,
                "refresh_token":self.current_token.token_refresh
            }), headers=headers)
        
        if resp.status_code >= 400:
            raise KeycloakConnectionError(resp.status_code, resp.text)
        
        self.current_token = None
    
    def refresh(self):
        """Refreshes token

        Raises:
            KeycloakError: Raised if not logged in
            KeycloakConnectionError: Raised if an unexpected connection error occurs

        Returns:
            AccessToken: New access token
        """
        if not self.authenticated:
            raise KeycloakError("Not authenticated. Run login() first.")
        
        headers = {
            "Content-type": "application/x-www-form-urlencoded"
        }
        if self.client_secret:
            resp = requests.post(self.endpoint_token, data=formencode({
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token":self.current_token.token_refresh,
                "grant_type": "refresh_token",
                "scope": "openid profile"
            }), headers=headers)
        else:
            resp = requests.post(self.endpoint_token, data=formencode({
                "client_id": self.client_id,
                "refresh_token":self.current_token.token_refresh,
                "grant_type": "refresh_token",
                "scope": "openid profile"
            }), headers=headers)
        
        if resp.status_code >= 400:
            raise KeycloakConnectionError(resp.status_code, resp.text)
        
        self.current_token = AccessToken(resp.json())
        return self.current_token



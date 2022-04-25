import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
    url: "https://auth.daxcode.org/auth",
    realm: "sso",
    clientId: "react-local",
});
keycloak.init({
    onLoad: "login-required",
});

export default keycloak;

import keycloak from "./utilities/auth";
import { ReactKeycloakProvider } from "@react-keycloak/web";
import { useEffect } from "react";

function App() {
    useEffect(() => {
        keycloak.login();
    }, []);
    return (
        <ReactKeycloakProvider authClient={keycloak}>
            <div>boop</div>
        </ReactKeycloakProvider>
    );
}

export default App;

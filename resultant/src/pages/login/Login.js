import { post } from "../../utilities/api";
import Form from "../../utilities/forms/form";
import { Input } from "../../utilities/forms/inputs";
import "./login.css";
import Cookies from "js-cookie";

export default function PageLogin() {
    return (
        <div className="login paper">
            <span className="login-title noselect">Log In</span>
            <Form
                extraClasses={["login-form"]}
                onSubmit={(data) => {
                    post("/login", {
                        body: {
                            username: data.username,
                            password: data.password,
                        },
                    }).then((data) => {
                        if (data.result === "failure") {
                            alert("Failed to login. Message: " + data.reason);
                            return;
                        }
                        window.localStorage.setItem(
                            "userInfo",
                            JSON.stringify(data.userInfo)
                        );
                        Cookies.set("Authorization", data.clientToken, {
                            domain: window.location.hostname
                                .split(".")
                                .slice(-2)
                                .join("."),
                            secure: true,
                        });
                        window.location.pathname = "/";
                    });
                }}
            >
                <Input
                    fieldName="username"
                    icon="account"
                    placeholder="Username"
                    type="text"
                />
                <Input
                    fieldName="password"
                    icon="textbox_password"
                    placeholder="Password"
                    type="password"
                />
            </Form>
        </div>
    );
}

import Form from "../../utilities/forms/form";
import { Input } from "../../utilities/forms/inputs";

export default function PageLogin() {
    return (
        <div className="login">
            <Form extraClasses={["login-form"]} onSubmit={console.log}>
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
                    type="text"
                />
            </Form>
        </div>
    );
}

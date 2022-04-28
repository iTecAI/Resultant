import { Outlet } from "react-router-dom";
import Icon from "../../utilities/icons";
import "../../util.css";
import "./layout.css";
import md5 from "js-md5";
import { post } from "../../utilities/api";
import Cookies from "js-cookie";

export default function Layout() {
    if (
        window.localStorage.getItem("userInfo") &&
        window.localStorage.getItem("userInfo") !== "undefined"
    ) {
        var uinfo = JSON.parse(window.localStorage.getItem("userInfo"));
    }
    return (
        <div className="page">
            <div className="nav paper noselect">
                <Icon name="adjust" />
                <div className="title">Resultant</div>
                {window.location.pathname.includes(
                    "login"
                ) ? null : window.localStorage.getItem("userInfo") ? (
                    <>
                        <div className="profile paper">
                            <span className="name">
                                {uinfo.name.length > 0
                                    ? uinfo.name
                                    : uinfo.username}
                            </span>
                            <img
                                alt="Profile"
                                src={
                                    "https://www.gravatar.com/avatar/" +
                                    md5(uinfo.email.trim().toLowerCase()) +
                                    "?d=identicon"
                                }
                                className="profile-image"
                            />
                        </div>
                        <button
                            className="logout paper"
                            onClick={() => {
                                post("/user/logout").then(() => {
                                    Cookies.remove("Authorization", {
                                        domain: window.location.hostname
                                            .split(".")
                                            .slice(-2)
                                            .join("."),
                                        secure: true,
                                    });
                                    window.localStorage.removeItem("userInfo");
                                    window.location.pathname = "/login";
                                });
                            }}
                        >
                            <Icon name="logout_variant" />
                        </button>
                    </>
                ) : null}
            </div>
            <div className="content">
                <Outlet />
            </div>
            <div className="footer paper noselect">
                <span>
                    <Icon name="copyright" />
                    <span>Dax Harris 2022</span>•
                    <a
                        href="https://raw.githubusercontent.com/iTecAI/Resultant/main/LICENSE"
                        target="_blank"
                        rel="noreferrer"
                    >
                        MIT Licensed
                    </a>
                    •
                    <a
                        href="https://github.com/iTecAI/Resultant"
                        target="_blank"
                        rel="noreferrer"
                    >
                        Resultant
                    </a>
                </span>
            </div>
        </div>
    );
}

import { Outlet } from "react-router-dom";
import Icon from "../../utilities/icons";
import "../../util.css";
import "./layout.css";

export default function Layout() {
    return (
        <div className="page">
            <div className="nav paper noselect">
                <Icon name="ray_start_arrow" />
                <div className="title">Resultant</div>
            </div>
            <div className="content">
                <Outlet />
            </div>
        </div>
    );
}

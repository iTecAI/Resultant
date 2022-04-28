import { useEffect, useState } from "react";
import { get } from "../../utilities/api";
import Icon from "../../utilities/icons";
import "./index.css";

export default function Index() {
    const [plugins, setPlugins] = useState({});
    const [search, setSearch] = useState("");

    function searchSend() {
        console.log(search);
    }

    useEffect(() => {
        get("/search/plugins").then((data) => {
            if (data.result !== "failure") {
                setPlugins(data);
                console.log(data);
            }
        });
    }, []);
    return (
        <div className="search paper">
            <input
                className="search-bar"
                value={search}
                onChange={(e) => {
                    setSearch(e.target.value);
                }}
                onKeyUp={(e) => {
                    if (e.key === "Enter") {
                        searchSend();
                    }
                }}
                placeholder="Search"
            />
            <Icon name="magnify" />
            <button className="search-btn paper" onClick={searchSend}>
                <Icon name="magnify" />
            </button>
        </div>
    );
}

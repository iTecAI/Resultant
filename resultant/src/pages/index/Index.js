import { useEffect, useState } from "react";
import { get, post } from "../../utilities/api";
import Icon from "../../utilities/icons";
import "./index.css";
import Form from "../../utilities/forms/form";
import { Input, Select, Switch, Range } from "../../utilities/forms/inputs";

function Tab({ tab = {}, setTab = () => {}, currentTab = "" } = {}) {
    var _tab = tab.info;
    return (
        <button
            className={
                "tab-button" + (currentTab === _tab.name ? " selected" : "")
            }
            name={_tab.name}
        >
            <Icon name={_tab.icon[1]} category={_tab.icon[0]} />
            <span className="title">{_tab.displayName}</span>
        </button>
    );
}

function PluginSettings({
    info = {},
    settings = {},
    active = false,
    setSettings = () => {},
} = {}) {
    return (
        <Form onChange={setSettings} submitButton={<></>}>
            <Switch
                fieldName="active"
                label="Active"
                icon="power"
                initialValue={active}
            ></Switch>
            {info.options.map((v, i, a) => {
                if (v.type === "select") {
                    return (
                        <Select
                            fieldName={v.name}
                            label={v.displayName}
                            icon={v.icon ? v.icon[1] : null}
                            iconClass={v.icon ? v.icon[0] : null}
                            key={v.name}
                            initialValue={settings[v.name]}
                        >
                            {Object.keys(v.options).map((vv, ii, aa) => (
                                <option value={vv} key={vv}>
                                    {v.options[vv]}
                                </option>
                            ))}
                        </Select>
                    );
                }
                return <></>;
            })}
        </Form>
    );
}

export default function Index() {
    const [plugins, setPlugins] = useState({});
    const [search, setSearch] = useState("");
    const [tab, setTab] = useState(null);

    function searchSend() {
        window.location = window.location.origin + "/results?q=" + search;
    }

    useEffect(() => {
        get("/search/plugins").then((data) => {
            if (data.result !== "failure") {
                setPlugins(data);
                setTab(Object.keys(data)[0]);
                console.log(data);
            }
        });
    }, []);
    return (
        <div className="search paper">
            <input
                className="search-bar paper"
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
            <div className="options-area paper">
                <div className="tabs">
                    {Object.values(plugins).map((v, i, a) => (
                        <Tab
                            tab={v}
                            setTab={setTab}
                            currentTab={tab}
                            key={tab}
                        />
                    ))}
                </div>
                <div className="settings">
                    {plugins[tab] ? (
                        <PluginSettings
                            info={plugins[tab].info}
                            settings={plugins[tab].settings}
                            active={plugins[tab].active}
                            setSettings={(data) => {
                                plugins[tab].settings = data;
                                console.log(plugins);
                                post("/search/plugins/" + tab + "/settings", {
                                    body: { settings: plugins[tab].settings },
                                }).then(console.log);
                            }}
                        />
                    ) : null}
                </div>
            </div>
        </div>
    );
}

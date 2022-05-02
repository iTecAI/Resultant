import { useEffect, useState } from "react";

export default function ThemeProvider(props = { theme: "main", children: [] }) {
    var current = JSON.parse(window.localStorage.getItem("themes") || "{}");
    const [theme, setTheme] = useState(
        Object.keys(current).includes(props.theme) ? current[props.theme] : {}
    );
    useEffect(
        function () {
            fetch("/api/theme/" + (props.theme || "main")).then((d) =>
                d.json().then((data) => {
                    setTheme(data);
                    var _current = JSON.parse(
                        window.localStorage.getItem("themes") || "{}"
                    );
                    _current[props.theme] = data;
                    window.localStorage.setItem(
                        "themes",
                        JSON.stringify(_current)
                    );
                })
            );
        },
        [props.theme]
    );
    return (
        <div style={theme} className="theme-provider">
            {props.children}
        </div>
    );
}

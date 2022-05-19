import { useEffect, useState } from "react";
import { get } from "../../utilities/api";

export default function Results() {
    const [schema, setSchema] = useState({});
    const [tab, setTab] = useState("root");
    useEffect(() => {
        var query = window.location.search.split("=")[1] || "";
        if (query.length === 0) {
            window.location = window.location.origin;
        }
        get("/search/", { parameters: { query: query } }).then((data) => {
            setSchema(data);
            console.log(data);
        });
    }, []);
    return <></>;
}

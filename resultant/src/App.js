import { useEffect } from "react";
import ThemeProvider from "./utilities/themeProvider";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "./pages/layout/Layout";
import PageLogin from "./pages/login/Login";
import Index from "./pages/index/Index";
import Cookies from "js-cookie";
import { get } from "./utilities/api";

function App() {
    useEffect(() => {
        if (!window.location.pathname.includes("/login")) {
            if (!Cookies.get("Authorization")) {
                window.location.pathname = "/login";
            }
            get("/user/info").then((v) => {
                if (v.result === "failure") {
                    window.location.pathname = "/login";
                }
                window.localStorage.setItem("userInfo", JSON.stringify(v.info));
            });
        }
    }, []);
    return (
        <ThemeProvider theme="dark">
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<Layout />}>
                        <Route path="/login" element={<PageLogin />} />
                        <Route index element={<Index />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </ThemeProvider>
    );
}

export default App;

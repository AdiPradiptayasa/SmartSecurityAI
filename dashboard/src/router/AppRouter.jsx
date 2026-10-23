import {
    BrowserRouter,
    Routes,
    Route
} from "react-router-dom";

import MainLayout from "../layouts/MainLayout";

import Dashboard from "../pages/Dashboard/Dashboard";
import Camera from "../pages/Camera/Camera";
import Persons from "../pages/Persons/Persons";
import Dataset from "../pages/Dataset/Dataset";
import Events from "../pages/Events/Events";
import Settings from "../pages/Settings/Settings";

export default function AppRouter() {

    return (

        <BrowserRouter>

            <Routes>

                <Route element={<MainLayout />}>

                    <Route
                        path="/"
                        element={<Dashboard />}
                    />

                    <Route
                        path="/camera"
                        element={<Camera />}
                    />

                    <Route
                        path="/persons"
                        element={<Persons />}
                    />

                    <Route
                        path="/dataset"
                        element={<Dataset />}
                    />

                    <Route
                        path="/events"
                        element={<Events />}
                    />

                    <Route
                        path="/settings"
                        element={<Settings />}
                    />

                </Route>

            </Routes>

        </BrowserRouter>

    );

}
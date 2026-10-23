import Sidebar from "../components/layout/Sidebar";
import Navbar from "../components/layout/Navbar";
import { Outlet } from "react-router-dom";

export default function MainLayout() {

    return (

        <div className="flex h-screen bg-slate-950 text-white">

            <Sidebar/>

            <div className="flex-1 flex flex-col overflow-hidden">

                <Navbar/>

                <main className="flex-1 overflow-y-auto p-8">

                    <Outlet/>

                </main>

            </div>

        </div>

    );

}
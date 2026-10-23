import { useState } from "react";

import {
    LayoutDashboard,
    Camera,
    Users,
    FolderOpen,
    ClipboardList,
    Settings,
    PanelLeftClose,
    PanelRightOpen
} from "lucide-react";

import SidebarLogo from "./SidebarLogo";
import SidebarFooter from "./SidebarFooter";
import NavItem from "./NavItem";

export default function Sidebar() {

    const [collapsed, setCollapsed] = useState(false);

    return (

        <aside
            className={`
                h-screen
                bg-slate-900
                border-r
                border-slate-800
                transition-all
                duration-300
                flex
                flex-col
                ${collapsed ? "w-20" : "w-72"}
            `}
        >

            <SidebarLogo
                 collapsed={collapsed}
                onToggle={() => setCollapsed(!collapsed)}
                />

            <div className="flex-1 mt-8">

                {

                    !collapsed &&

                    <p className="px-6 mb-4 text-xs uppercase tracking-[0.25em] text-slate-500">

                           

                    </p>

                }

                <nav className="px-1 space-y-3">

                    <NavItem collapsed={collapsed} to="/" title="Dashboard" icon={LayoutDashboard}/>

                    <NavItem collapsed={collapsed} to="/camera" title="Live Camera" icon={Camera}/>

                    <NavItem collapsed={collapsed} to="/persons" title="Persons" icon={Users}/>

                    <NavItem collapsed={collapsed} to="/dataset" title="Dataset" icon={FolderOpen}/>

                    <NavItem collapsed={collapsed} to="/events" title="Event Logs" icon={ClipboardList}/>

                    <NavItem collapsed={collapsed} to="/settings" title="Settings" icon={Settings}/>

                </nav>

            </div>

            <SidebarFooter collapsed={collapsed}/>

        </aside>

    );

}
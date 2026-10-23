import { NavLink } from "react-router-dom";

export default function NavItem({

    to,

    title,

    icon: Icon,

    collapsed

}) {

    return (

        <NavLink

            to={to}

            className={({isActive})=>

                `

                relative

                flex

                items-center

                ${collapsed ? "justify-center" : "gap-4"}

                h-12

                rounded-xl

                transition-all

                duration-200

                ${

                    isActive

                    ?

                    "bg-slate-800 text-white"

                    :

                    "text-slate-400 hover:bg-slate-800 hover:text-white"

                }

                `

            }

        >

            {({isActive})=>(

                <>

                    {

                        isActive &&

                        <span

                            className="

                                absolute

                                left-0

                                top-2

                                bottom-2

                                w-1

                                rounded-r-full

                                bg-blue-500

                            "

                        />

                    }

                    <Icon

                        size={20}

                        className={collapsed ? "" : "ml-4"}

                    />

                    {

                        !collapsed &&

                        <span>

                            {title}

                        </span>

                    }

                </>

            )}

        </NavLink>

    );

}
import { ShieldCheck } from "lucide-react";

export default function SidebarLogo({

    collapsed,

    onToggle

}) {

    return (

        <div className="border-none px-4 py-6">

            <button

                onClick={onToggle}

                className={`
                    w-full
                    transition-all
                    duration-300
                    rounded-2xl
                    hover:bg-slate-800
                    p-3
                    ${
                        collapsed
                            ? "flex justify-center"
                            : "flex items-center gap-4"
                    }
                `}

            >

                <div
                    className="
                        w-12
                        h-12
                        rounded-xl
                        bg-gradient-to-br
                        from-blue-500
                        to-blue-700
                        flex
                        items-center
                        justify-center
                        shadow-lg
                        shadow-blue-900/30
                        shrink-0
                    "
                >

                    <ShieldCheck
                        size={24}
                        className="text-white"
                    />

                </div>

                {

                    !collapsed &&

                    <div className="text-left">

                        <h1 className="font-bold text-white">

                            Intruder Detection

                        </h1>

                        <p className="text-sm text-slate-400">

                            v.1.0

                        </p>

                    </div>

                }

            </button>

        </div>

    );

}
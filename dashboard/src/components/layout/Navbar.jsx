import { Bell, Shield } from "lucide-react";

export default function Navbar() {
    return (
        <header className="h-20 border-b border-slate-700 bg-slate-900 px-8">

            <div className="h-full flex items-center justify-between">

                <div>

                 

                </div>

                <div className="flex items-center gap-6">

                    <Bell
                        size={22}
                        className="text-slate-400 cursor-pointer hover:text-white transition"
                    />

                    <div className="flex items-center gap-3">

                        <div
                            className="
                                w-10
                                h-10
                                rounded-full
                                bg-blue-600
                                flex
                                items-center
                                justify-center
                            "
                        >
                            <Shield size={22}/>
                        </div>

                        <div>

                            <h3 className="font-semibold">

                                Admin

                            </h3>

                           

                        </div>

                    </div>

                </div>

            </div>

        </header>
    );
}
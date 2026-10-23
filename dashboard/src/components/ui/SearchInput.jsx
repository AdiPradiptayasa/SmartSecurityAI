import { Search } from "lucide-react";

export default function SearchBox({

    placeholder = "Search..."

}) {

    return (

        <div className="relative">

            <Search

                size={18}

                className="absolute left-3 top-3 text-slate-400"

            />

            <input

                className="

                    w-full

                    bg-slate-800

                    border

                    border-slate-700

                    rounded-lg

                    py-2

                    pl-10

                    pr-4

                    focus:outline-none

                    focus:border-blue-500

                "

                placeholder={placeholder}

            />

        </div>

    );

}
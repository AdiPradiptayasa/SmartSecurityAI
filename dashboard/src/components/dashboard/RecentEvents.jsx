import SectionCard from "./SectionCard";

import SearchBox from "../ui/SearchInput";

export default function RecentEvents() {

    const events = [

        "System Started",

        "MongoDB Connected",

        "Waiting Camera",

        "Waiting AI",

        "Waiting Detection"

    ];

    return (

        <SectionCard title="Recent Events">

            <div className="space-y-5">

                <SearchBox />

                <div className="space-y-3">

                    {

                        events.map((item,index)=>(

                            <div

                                key={index}

                                className="bg-slate-900 rounded-lg p-3"

                            >

                                {item}

                            </div>

                        ))

                    }

                </div>

            </div>

        </SectionCard>

    );

}
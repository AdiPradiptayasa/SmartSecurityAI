import PageTitle from "../../components/ui/PageTitle";
import StatusGrid from "../../components/dashboard/StatusGrid";
import LiveCamera from "../../components/dashboard/LiveCamera";
import LatestDetection from "../../components/dashboard/LatestDetection";
import RecentEvents from "../../components/dashboard/RecentEvents";
import { Divide } from "lucide-react";

export default function Dashboard() {

    return (

        <div className="space-y-8">

            <PageTitle
                title="Monitoring System"
            />

            <StatusGrid />

            <div
                className="
                    grid
                    grid-cols-12
                    gap-5
                    items-start
                "
            >

                <div className="col-span-12 lg:col-span-8">

                    <LiveCamera />

                </div>

                <div className="col-span-12 lg:col-span-4">

                    <LatestDetection />

                </div>

            </div>

           

        </div>

    );

}
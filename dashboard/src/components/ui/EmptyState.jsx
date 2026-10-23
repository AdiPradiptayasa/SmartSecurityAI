import { Inbox } from "lucide-react";

export default function EmptyState({

    message

}) {

    return (

        <div className="text-center py-12 text-slate-500">

            <Inbox

                size={50}

                className="mx-auto mb-3"

            />

            <p>

                {message}

            </p>

        </div>

    );

}
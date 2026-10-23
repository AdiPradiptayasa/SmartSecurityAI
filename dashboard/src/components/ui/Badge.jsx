export default function Badge({

    text,

    type = "success"

}) {

    const colors = {

        success:
            "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",

        warning:
            "bg-yellow-500/15 text-yellow-400 border border-yellow-500/30",

        danger:
            "bg-red-500/15 text-red-400 border border-red-500/30",

        info:
            "bg-blue-500/15 text-blue-400 border border-blue-500/30"

    };

    return (

        <span
            className={`
                inline-flex
                items-center
                px-3
                py-1.5
                rounded-full
                text-xs
                font-semibold
                ${colors[type]}
            `}
        >

            <span className="w-2 h-2 rounded-full bg-current mr-2"></span>

            {text}

        </span>

    );

}
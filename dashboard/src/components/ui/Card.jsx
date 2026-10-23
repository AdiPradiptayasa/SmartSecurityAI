export default function Card({
    children,
    title,
    subtitle,
    className = ""
}) {

    return (

        <div
            className={`
                bg-slate-800
                border
                border-slate-700
                rounded-2xl
                shadow-lg
                p-6
                ${className}
            `}
        >

            {(title || subtitle) && (

                <div className="mb-5">

                    {title && (

                        <h2 className="text-xl font-semibold text-white">

                            {title}

                        </h2>

                    )}

                    {subtitle && (

                        <p className="text-sm text-slate-400 mt-1">

                            {subtitle}

                        </p>

                    )}

                </div>

            )}

            {children}

        </div>

    );

}
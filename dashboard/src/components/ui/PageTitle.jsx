export default function PageTitle({

    title,

    subtitle

}) {

    return (

        <div className="mb-2">

            <h1 className="text-4xl font-bold tracking-tight">

                {title}

            </h1>

            <p className="text-slate-400 mt-2">

                {subtitle}

            </p>

        </div>

    );

}
import useHealth from "../../hooks/useHealth";

export default function SystemHealth() {

    const {

        health,

        loading,

        error

    } = useHealth();

    if (loading)

        return <p>Loading...</p>;

    if (error)

        return <p>Backend Offline</p>;

   return (

<div className="bg-slate-800 rounded-xl p-5 shadow">

    <h2 className="text-xl font-bold mb-4">
        Backend Status
    </h2>

    <div className="space-y-2">

        <p>
            Status :
            <span className="text-green-400">
                {" "}{health.status}
            </span>
        </p>

        <p>
            Server :
            <span className="text-green-400">
                {" "}{health.server}
            </span>
        </p>

        <p>
            Database :
            <span className={health.database ? "text-green-400" : "text-red-400"}>
                {health.database ? " Connected" : " Offline"}
            </span>
        </p>

        <p>
            MQTT :
            <span className={health.mqtt ? "text-green-400" : "text-yellow-400"}>
                {health.mqtt ? " Connected" : " Waiting"}
            </span>
        </p>

        <p>
            Camera :
            <span className={health.camera ? "text-green-400" : "text-yellow-400"}>
                {health.camera ? " Online" : " Waiting"}
            </span>
        </p>

        <p>
            AI Server :
            <span className={health.ai ? "text-green-400" : "text-yellow-400"}>
                {health.ai ? " Running" : " Waiting"}
            </span>
        </p>

        <p>
            Telegram :
            <span className={health.telegram ? "text-green-400" : "text-yellow-400"}>
                {health.telegram ? " Connected" : " Waiting"}
            </span>
        </p>

        <p className="text-slate-400">
            Version : {health.version}
        </p>

    </div>

</div>

);

}
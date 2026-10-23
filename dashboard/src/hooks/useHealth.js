import { useEffect, useState } from "react";

import { HealthService } from "../services/healthService";

export default function useHealth() {

    const [health, setHealth] = useState(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState(null);

    useEffect(() => {

        loadHealth();

    }, []);

    async function loadHealth() {

        try {

            const data = await HealthService.check();

            setHealth(data);

        }

        catch (err) {

            setError(err);

        }

        finally {

            setLoading(false);

        }

    }

    return {

        health,

        loading,

        error,

        reload: loadHealth

    };

}
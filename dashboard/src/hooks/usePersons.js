import { useEffect, useState } from "react";
import { PersonService } from "../services/personService";

export default function usePersons() {

    const [persons, setPersons] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {

        loadPersons();

    }, []);

    async function loadPersons() {

        try {

            const data = await PersonService.getPersons();

            setPersons(data.persons);

        }

        catch (err) {

            setError(err);

        }

        finally {

            setLoading(false);

        }

    }

    return {

        persons,

        loading,

        error,

        reload: loadPersons

    };

}
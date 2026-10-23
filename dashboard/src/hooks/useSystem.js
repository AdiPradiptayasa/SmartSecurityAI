import { useEffect, useState } from "react";

import { SystemService } from "../services/systemService";

export default function useSystem(){

    const [system,setSystem]=useState(null);

    const [loading,setLoading]=useState(true);

    const [error,setError]=useState(null);

    useEffect(()=>{

        loadSystem();

    },[]);

    async function loadSystem(){

        try{

            const data=await SystemService.status();

            setSystem(data);

        }

        catch(err){

            setError(err);

        }

        finally{

            setLoading(false);

        }

    }

    return{

        system,

        loading,

        error,

        reload:loadSystem

    };

}
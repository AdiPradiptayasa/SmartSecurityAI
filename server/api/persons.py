from fastapi import APIRouter

from server.services.database_service import DatabaseService

router = APIRouter()

database = DatabaseService()


@router.get("/persons")
async def get_persons():

    persons = database.get_persons()

    return {
        "total": len(persons),
        "persons": persons
    }
from fastapi import APIRouter
from pydantic import BaseModel

from server.services.dataset_service import DatasetService
from server.services.database_service import DatabaseService

router = APIRouter()

service = DatasetService()
database = DatabaseService()


class RegisterUser(BaseModel):
    name: str


@router.post("/register")
async def register(user: RegisterUser):

    # Membuat folder dataset
    folder = service.create_folder(user.name)

    # Simpan ke MongoDB
    saved = database.save_person(user.name)

    return {
        "status": "success",
        "person": user.name,
        "folder": str(folder),
        "database_saved": saved
    }
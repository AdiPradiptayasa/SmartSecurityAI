from fastapi import APIRouter

from server.services.database_service import DatabaseService

router = APIRouter()

database = DatabaseService()


@router.get("/dataset")
async def get_dataset():
    dataset = database.get_dataset_summary()

    total_images = sum(d["images"] for d in dataset)

    return {
        "total_datasets": len(dataset),
        "total_images": total_images,
        "dataset": dataset
    }
from fastapi import APIRouter, UploadFile, File, Form
from typing import List

from server.services.ai_data_service import AIDataService

router = APIRouter()
ai_data = AIDataService()


@router.get("/ai/owners")
def get_owners():
    owners = ai_data.get_owners()
    return {"total": len(owners), "owners": owners}


@router.get("/ai/dataset")
def get_ai_dataset():
    dataset = ai_data.get_dataset_summary()
    total_images = sum(d["images"] for d in dataset)
    return {
        "total_datasets": len(dataset),
        "total_images": total_images,
        "dataset": dataset
    }


@router.post("/ai/dataset/upload")
def upload_dataset_photos(
    name: str = Form(...),
    files: List[UploadFile] = File(...)
):
    saved_count = ai_data.save_uploaded_photos(name, files)
    return {
        "status": "success",
        "message": f"{saved_count} foto berhasil diupload untuk '{name}'",
        "person": name,
        "uploaded_count": saved_count
    }


@router.post("/ai/enroll/run")
def trigger_enrollment():
    try:
        owners = ai_data.run_enrollment()
        return {
            "status": "success",
            "message": "Enrollment berhasil dijalankan ulang",
            "owners": owners
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from server.services.dataset_service import DatasetService

router = APIRouter()

service = DatasetService()


@router.post("/capture")
async def capture_image(
    person: str = Form(...),
    image: UploadFile = File(...)
):

    # Validasi file
    if image.content_type not in ["image/jpeg", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="File harus berupa JPG/JPEG"
        )

    # Membaca isi file
    image_bytes = await image.read()

    # Simpan gambar
    result = service.save_image(person, image_bytes)

    return result
from fastapi import APIRouter, HTTPException

from server.services.database_service import DatabaseService

router = APIRouter()

database = DatabaseService()


@router.get("/events")
def get_events(limit: int = 50):
    events = database.get_events(limit=limit)
    return {"total": len(events), "events": events}


@router.delete("/events/{event_id}")
def delete_event(event_id: str):
    deleted = database.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event tidak ditemukan")
    return {"status": "success", "message": "Event berhasil dihapus"}


@router.delete("/events")
def delete_all_events():
    count = database.delete_all_events()
    return {"status": "success", "message": f"{count} event berhasil dihapus"}
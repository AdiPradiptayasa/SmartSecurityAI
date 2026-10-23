from fastapi import APIRouter
from server.services.health_service import HealthService

router = APIRouter()
health_service = HealthService()


@router.get("/status")
def get_status():  # dari "async def" jadi "def"
    health = health_service.check()

    items = [
        {"key": "camera", "title": "ESP32-CAM", "value": "Online" if health["camera"] else "Offline", "status": "success" if health["camera"] else "danger"},
        {"key": "database", "title": "MongoDB", "value": "Connected" if health["database"] else "Disconnected", "status": "success" if health["database"] else "danger"},
        {"key": "ai", "title": "AI Server", "value": "Running" if health["ai"] else "Stopped", "status": "success" if health["ai"] else "danger"},
        {"key": "mqtt", "title": "MQTT Broker", "value": "Connected" if health["mqtt"] else "Offline", "status": "success" if health["mqtt"] else "danger"},
        {"key": "telegram", "title": "Telegram Bot", "value": "Active" if health["telegram"] else "Waiting", "status": "success" if health["telegram"] else "warning"},
    ]

    return {"status": health["status"], "items": items}
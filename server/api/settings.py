from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from server.services.settings_service import SettingsService

router = APIRouter()
settings_service = SettingsService()


class SettingsUpdate(BaseModel):
    system_armed: Optional[bool] = None
    telegram_enabled: Optional[bool] = None
    auto_alarm_enabled: Optional[bool] = None


@router.get("/settings")
def get_settings():
    return settings_service.get_settings()


@router.put("/settings")
def update_settings(update: SettingsUpdate):
    partial = {k: v for k, v in update.dict().items() if v is not None}
    updated = settings_service.update_settings(partial)
    return {"status": "success", "settings": updated}
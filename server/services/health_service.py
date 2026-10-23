from server.database.mongodb import client
from server.services.mqtt_service import is_mqtt_connected, is_ai_ready
from server.services.camera_service import is_camera_online
from server.services.telegram_service import is_telegram_configured


class HealthService:

    def check(self):

        database = False

        try:
            client.admin.command("ping")
            database = True
        except:
            database = False

        return {
            "status": "healthy",
            "server": "running",
            "database": database,
            "mqtt": is_mqtt_connected(),
            "telegram": is_telegram_configured(),
            "camera": is_camera_online(),
            "ai": is_ai_ready(),
            "version": "1.0.0"
        }
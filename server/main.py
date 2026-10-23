from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 1. Pastikan seluruh import modul konsisten menggunakan prefix 'server.'
from server.api.register import router as register_router
from server.api.persons import router as persons_router
from server.api.capture import router as capture_router
from server.api.events import router as events_router
from server.api.dataset import router as dataset_router
from server.api.status import router as status_router
from server.api.ai_data import router as ai_data_router
from server.api.settings import router as settings_router

from server.services.health_service import HealthService
from server.services.mqtt_service import start_mqtt_client
from server.services.telegram_service import start_telegram_bot

# Inisialisasi Service dan App
health_service = HealthService()
app = FastAPI(title="Smart Security AI", version="1.0.0")

# Konfigurasi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.137.50:81/stream",
        "https://cauterize-rearrange-monetary.ngrok-free.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router
app.include_router(register_router)
app.include_router(persons_router)
app.include_router(capture_router)
app.include_router(events_router)
app.include_router(dataset_router)
app.include_router(status_router)
app.include_router(ai_data_router)
app.include_router(settings_router)

# Mount Static Folder untuk preview tangkapan gambar
app.mount("/uploads", StaticFiles(directory="server/uploads"), name="uploads")


# 2. Gabungkan startup event menjadi satu dan taruh SETELAH 'app' dibuat
@app.on_event("startup")
def startup_event():
    # Jalankan client MQTT
    start_mqtt_client()

    # Jalankan listener bot Telegram (mengambil fungsi health_service.check yang sama dengan endpoint /health web)
    start_telegram_bot(get_status_func=health_service.check)


@app.get("/")
async def root():
    return {
        "project": "Smart Security AI",
        "status": "Running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return health_service.check()
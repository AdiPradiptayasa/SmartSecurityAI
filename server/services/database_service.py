import os
from datetime import datetime
from bson import ObjectId

from server.database.mongodb import (
    persons_collection,
    captures_collection,
    events_collection
)


class DatabaseService:

    def save_person(self, name):
        data = {
            "name": name,
            "created_at": datetime.now()
        }
        return persons_collection.insert_one(data)

    def get_persons(self):
        persons = list(persons_collection.find({}, {"_id": 0}))

        enriched = []
        for p in persons:
            name = p.get("name")
            image_count = captures_collection.count_documents({"person": name})
            last_capture = captures_collection.find_one(
                {"person": name},
                sort=[("created_at", -1)]
            )

            enriched.append({
                "name": name,
                "created_at": p.get("created_at"),
                "images": image_count,
                "status": "registered" if image_count > 0 else "pending",
                "last_seen": last_capture["created_at"] if last_capture else None,
            })

        return enriched

    def save_capture(self, person, filename, filepath):
        document = {
            "person": person,
            "filename": filename,
            "filepath": filepath,
            "camera_id": "ESP32CAM01",
            "location": "Living Room",
            "status": "dataset",
            "created_at": datetime.now()
        }
        return captures_collection.insert_one(document)

    def save_event(self, person, status, confidence=None, image_url=None, camera_id="ESP32CAM01", location="Living Room"):
        document = {
            "person": person,
            "status": status,
            "confidence": confidence,
            "image_url": image_url,
            "camera_id": camera_id,
            "location": location,
            "created_at": datetime.now()
        }
        return events_collection.insert_one(document)

    def get_events(self, limit=50):
        events = list(
            events_collection.find({})
            .sort("created_at", -1)
            .limit(limit)
        )
        for e in events:
            e["_id"] = str(e["_id"])
        return events

    def _delete_image_file(self, image_url):
        """Hapus file fisik di disk berdasarkan image_url yang tersimpan di database"""
        if not image_url:
            return

        # image_url formatnya "/uploads/events/nama_file.jpg"
        # server menyimpan fisik di "server/uploads/events/nama_file.jpg"
        relative_path = image_url.lstrip("/")  # buang "/" di depan
        filepath = os.path.join("server", relative_path)

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"[DELETE] File dihapus: {filepath}")
            else:
                print(f"[DELETE] File tidak ditemukan (sudah terhapus?): {filepath}")
        except OSError as e:
            print(f"[DELETE] Gagal hapus file {filepath}: {e}")

    def delete_event(self, event_id):
        event = events_collection.find_one({"_id": ObjectId(event_id)})

        if not event:
            return False

        # Hapus file foto dulu sebelum record-nya dihapus
        self._delete_image_file(event.get("image_url"))

        result = events_collection.delete_one({"_id": ObjectId(event_id)})
        return result.deleted_count > 0

    def delete_all_events(self):
        # Ambil semua event dulu untuk tahu file mana saja yang perlu dihapus
        all_events = list(events_collection.find({}, {"image_url": 1}))

        for event in all_events:
            self._delete_image_file(event.get("image_url"))

        result = events_collection.delete_many({})
        return result.deleted_count

    def get_dataset_summary(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$person",
                    "images": {"$sum": 1},
                    "updated_at": {"$max": "$created_at"},
                }
            },
            {"$sort": {"updated_at": -1}},
        ]

        results = list(captures_collection.aggregate(pipeline))

        dataset = []
        for r in results:
            images = r["images"]
            status = "ready" if images >= 30 else "incomplete"

            dataset.append({
                "name": r["_id"],
                "images": images,
                "status": status,
                "updated_at": r["updated_at"],
            })

        return dataset
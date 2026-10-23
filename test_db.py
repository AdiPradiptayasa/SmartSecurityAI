from server.database.mongodb import db

print("Database:", db.name)

result = db["persons"].insert_one({
    "name": "TEST_DATABASE"
})

print("Inserted ID:", result.inserted_id)

print("Collections:", db.list_collection_names())
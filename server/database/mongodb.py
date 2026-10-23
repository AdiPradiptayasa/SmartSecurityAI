from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)

db = client["smart_security_ai"]

persons_collection = db["persons"]
captures_collection = db["captures"]
events_collection = db["events"]
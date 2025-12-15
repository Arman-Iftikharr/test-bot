from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
    print(client.server_info())  # Test
    print("MongoDB Connected Successfully!")
except Exception as e:
    print("MongoDB Connection Failed:", e)

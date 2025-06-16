# app/api.py
from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
import os

router = APIRouter()

# MONGO_URI = os.environ.get("MONGO_URI", "mongodb://root:example@mongo:27017/?authSource=admin")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://pytest:EhXioTZ78ve72h@13.229.95.250:27017/seo_ai?authSource=pytest")
client = MongoClient(MONGO_URI)
# db = client["seo_ai"]
db = client["pytest"]
collection = db["text_result"]

def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("/result/list")
def get_test_result():
    result = list(collection.find())
    if result:
        return [serialize(i) for i in result]
    raise HTTPException(status_code=404, detail="anything is not found!")

@router.get("/result/{task_id}")
def get_test_result(task_id: str):
    result = collection.find_one({"task_id": task_id})
    if result:
        result["_id"] = str(result["_id"])
        return result
    raise HTTPException(status_code=404, detail="result not found!")

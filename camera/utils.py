from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

mongo = MongoClient(os.getenv("MONGODB_URL"), server_api=ServerApi("1"))
db = mongo["db"]


def init_database():
    config = db["config"].find_one(
        {
            "_id": "config",
        }
    )
    if len(config) == 0:
        db["config"].insert_one(
            {
                "_id": "config",
                "camera_status": False,
            }
        )

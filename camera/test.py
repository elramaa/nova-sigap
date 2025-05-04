from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from ubidots import *
from datetime import datetime, timedelta
import cv2

load_dotenv()

mongo = MongoClient(os.getenv("MONGODB_URL"), server_api=ServerApi("1"))
db = mongo["db"]

today = datetime.combine(datetime.today(), datetime.min.time())

# db["saved_detections"].delete_many(
#     {
#         "tags": "same person",
#         "timestamp": {"$gte": today, "$lte": today + timedelta(days=1)},
#     }
# )

db["config"].update_one({"_id": "config"}, {"$set": {"camera_status": False}})

# db["sus_images"].delete_many(
#     {"timestamp": {"$gte": today, "$lte": today + timedelta(days=1)}, "tag": "weapon"}
# )


# get_var_ubidots('camera_status')

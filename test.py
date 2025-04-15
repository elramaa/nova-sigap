from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from ubidots import *
from datetime import datetime, timedelta
import cv2

load_dotenv()

mongo = MongoClient(os.getenv("MONGODB_URL"), server_api=ServerApi('1'))
db = mongo['db']
sus_images_collection = db['sus_images']

today = datetime.combine(datetime.today(), datetime.min.time())

db['members'].find({
    'timestamp': {
        '$gte': today,
        '$lte': today + timedelta(days=1)
    }
})

# get_var_ubidots('camera_status')
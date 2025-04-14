from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import cv2

load_dotenv()

mongo = MongoClient(os.getenv("MONGODB_URL"), server_api=ServerApi('1'))
db = mongo['db']
sus_images_collection = db['sus_images']

img_data = sus_images_collection.find_one()
print(img_data)

with open("example.jpg", "wb") as f:
    img = f.write(img_data['image_bin'])
    cv2.imshow('Image', img)

if cv2.waitKey(1) == ord('q'):
    cv2.destroyAllWindows()
import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from io import BytesIO
from dotenv import load_dotenv
from datetime import timedelta, datetime
import cv2

load_dotenv()

mongo = MongoClient(os.getenv("MONGODB_URL"), server_api=ServerApi('1'))
db = mongo['db']
sus_images_collection = db['sus_images']

st.set_page_config(page_title="SIGAP Dashboard", layout="wide")

st.title("SIGAP: Sistem Intelijen Garda Aman Pintar")

input_col1, input_col2 = st.columns(2)

date = input_col1.date_input("Filter Day", max_value="today")
tag = input_col2.selectbox("Filter Image Tag", ("all", "fight", 'package', 'idle'))

col1, col2, col3, col4 = st.columns(4)

filter_date = datetime.fromisoformat(date.isoformat())
if tag != 'all':
    filtered_images = sus_images_collection.find(
        {
            'timestamp': {'$gte': filter_date, '$lte': filter_date + timedelta(days=1)},
            'tag': tag
        }
    ).limit(50).sort('timestamp', -1)
else:
    filtered_images = sus_images_collection.find(
        {
            'timestamp': {'$gte': filter_date, '$lte': filter_date + timedelta(days=1)}
        }
    ).limit(50).sort('timestamp', -1)

count = 0
for image in filtered_images:
    image_stream = BytesIO(image['image_bin'])
    if count % 4 == 0:
        col1.image(image_stream, caption=image['timestamp'].strftime("%H:%M"))
    elif count % 4 == 1:
        col2.image(image_stream, caption=image['timestamp'].strftime("%H:%M"))
    elif count % 4 == 2:
        col3.image(image_stream, caption=image['timestamp'].strftime("%H:%M"))
    elif count % 4 == 3:
        col4.image(image_stream, caption=image['timestamp'].strftime("%H:%M"))
    count += 1

if not filtered_images:
    st.text("No image found")
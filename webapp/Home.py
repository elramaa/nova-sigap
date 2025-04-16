import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from io import BytesIO
from dotenv import load_dotenv
from datetime import timedelta, datetime

load_dotenv()

mongo = MongoClient(os.getenv("MONGODB_URL"), server_api=ServerApi('1'))
db = mongo['db']
sus_images_collection = db['sus_images']

def get_members_today():
    today = datetime.combine(datetime.today(), datetime.min.time())
    members = db['members'].find({
        'timestamp': {
            '$gte': today,
            '$lte': today + timedelta(days=1)
        }
    }).sort('timestamp', -1)
    return members

st.set_page_config(page_title="SIGAP Dashboard", layout="wide")

st.title("SIGAP: Sistem Intelijen Garda Aman Pintar")

st.metric("Warga Terlihat Hari Ini", len(list(get_members_today())), border=True)

with st.expander("Pengenalan Warga"):
    col1, col2, col3, col4 = st.columns(4)
    count = 0
    for member in get_members_today():
        image_stream = BytesIO(member['image_bin'])
        if count % 4 == 0:
            col1.image(image_stream, caption=member['name'])
        elif count % 4 == 1:
            col2.image(image_stream, caption=member['name'])
        elif count % 4 == 2:
            col3.image(image_stream, caption=member['name'])
        elif count % 4 == 3:
            col4.image(image_stream, caption=member['name'])
        count += 1

input_col1, input_col2 = st.columns(2)

date = input_col1.date_input("Filter Hari", max_value="today")
tag_translated = {'Semua': 'all', 'Senjata': 'weapon', 'Paket': 'package', 'Diam': 'idle', 'Perkelahian': 'fight'}
tag = input_col2.selectbox("Filter Image Tag", list(tag_translated.keys()))

col1, col2, col3, col4 = st.columns(4)

filter_date = datetime.fromisoformat(date.isoformat())
if tag != 'Semua':
    filtered_images = sus_images_collection.find(
        {
            'timestamp': {'$gte': filter_date, '$lte': filter_date + timedelta(days=1)},
            'tag': tag_translated[tag]
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
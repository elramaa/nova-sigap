import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from io import BytesIO
from dotenv import load_dotenv
from datetime import timedelta, datetime
import altair as alt
import pandas as pd
import requests as req
import humanize

load_dotenv()

mongo = MongoClient(os.getenv("MONGODB_URL"), server_api=ServerApi("1"))
db = mongo["db"]
saved_detections = db["saved_detections"]


def get_visitor_today():
    today = datetime.combine(datetime.today(), datetime.min.time())
    visitors = (
        db["saved_detections"]
        .find(
            {
                "timestamp": {
                    "$gte": today,
                    "$lte": today + timedelta(days=1),
                },
                "tags": "visitor",
            }
        )
        .sort("timestamp", -1)
    )
    return visitors


st.set_page_config(page_title="SIGAP Dashboard", layout="wide")

# Custom CSS for fonts and colors
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Roboto:wght@400;700&display=swap');

    .title-text {
        font-size: 40px;
        font-weight: 800;
        line-height: 1;
    }
    .subtitle-text {
        font-size: 16px;
        letter-spacing: 0.1em;
        margin-top: -6px;
        font-weight: 300;
    }
    .section {
        background-color: #152022;
        border-radius: 12px;
        padding: 20px;
    }
    .card {
    background-color: #152022;
    border-radius: 16px;
    padding: 24px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header
col1, col2 = st.columns([7, 1])
with col1:
    st.title("SIGAP")
    st.markdown("**Sistem Intelijen Garda Aman Pintar**")
with col2:
    st.image("dashboard/logo.jpeg", width=200) # FOR DEPLOY
    # st.image("logo.jpeg", width=200)  # FOR LOCAL


# Main Sections
grid1, grid2, grid3 = st.columns([2, 1, 1])

with grid1:
    # Activity History
    st.html("<h2 class='section' style='margin:0'>ACTIVITY HISTORY</h2>")

    # Calculate start (Monday) and end (Sunday) of the current week
    today = datetime.combine(datetime.today(), datetime.min.time())
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=7)
    print(start_of_week)

    # Aggregation pipeline to group by day
    pipeline = [
        {
            "$match": {
                "timestamp": {"$gte": start_of_week, "$lt": end_of_week},
                "tags": "suspicious",
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%u", "date": "$timestamp"}},
                "count": {"$sum": 1},
            }
        },
    ]

    result = list(saved_detections.aggregate(pipeline))

    # Initialize with 0s for each day
    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_counts = {day: 0 for day in day_order}

    # Fill with result counts
    for r in result:
        day = day_order[int(r["_id"]) - 1]
        count = r["count"]
        day_counts[day] = count

    # Create DataFrame and plot
    df = pd.DataFrame(
        {"Day": list(day_counts.keys()), "Suspicious Count": list(day_counts.values())}
    )

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Day", sort=day_order),
            y="Suspicious Count",
            color=alt.Color("Day", scale=alt.Scale(range=["#3a7f8a", "#7a8a8f"])),
            tooltip=["Day", "Suspicious Count"],
        )
        .properties(width="container", height=200)
    )

    st.altair_chart(chart, use_container_width=True)

with grid2:
    suspicious_activities = {
        "weapon": "Senjata",
        "idle": "Orang berdiam diri",
        "fight": "Perkelahian",
        "loitering": "Orang mondar-mandir",
    }
    last_detection = saved_detections.find_one(
        {"tags": "suspicious"}, sort=[("timestamp", -1)]
    )
    suspicious_key = set(last_detection["tags"]) & set(suspicious_activities.keys())
    suspicious_activity = suspicious_activities[suspicious_key.pop()]
    now = datetime.now()
    time_diff = last_detection["timestamp"] - now
    diff = humanize.naturaldelta(time_diff)
    st.html(
        f"""
        <section style="
            background-color: #152022;
            border-radius: 0.5rem;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        ">
            <h4 style="
                margin-bottom: 0.75rem;
            ">ALERT</h4>
            <img src="https://storage.googleapis.com/a1aa/image/09e32bab-8769-42ec-df9c-9f420b1160c0.jpg" alt="Red triangular warning icon with exclamation mark" style="width: 64px; height: 64px; margin-bottom: 1rem;"/>
            <p style="
                max-width: 280px;
                font-size: 1rem;
                line-height: 1.4;
                margin: 0 auto;
            ">Suspicious behavior detected: {suspicious_activity}</p>
            <br>
            <p>{diff} ago</p>
        </section>
    """
    )

with grid3:
    is_active = db["config"].find_one({"_id": "config"})["camera_status"]
    st.html(
        f"""
        <div class="card" style="margin-bottom:16px; height:100%;">
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="background:{"#3B9B7A" if is_active else "red"};border-radius:16px;width:64px;height:64px;display:flex;align-items:center;justify-content:center;font-weight:800;">{"ON" if is_active else "OFF"}</div>
                <h4>Camera Status</h4>
            </div>
        </div>
        """,
    )

# Second row
grid3, grid4, grid5 = st.columns(3)

with grid3:
    st.html(
        """
    <section style="
        background-color: #152022;
        border-radius: 16px;
        padding: 1.25rem;
        padding-bottom: 1.9rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.25rem;
        height: 100%;
    ">
        <h4 style="
            margin: 0;
        ">Deteksi Terakhir</h4>
        <div style="
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background-color: #3a7f8a;
                border-radius: 0.5rem;
                padding: 1rem;
                width: 80px;
                height: 80px;
                display: flex;
                justify-content: center;
                align-items: center;
            ">
                <img src="https://storage.googleapis.com/a1aa/image/12b9b0ed-2fbc-469c-f7b2-aaf65a7d0875.jpg" alt="Icon of a delivery person standing next to a box in teal color" style="width: 48px; height: 48px;"/>
            </div>
            <p style="
                font-size: 1.125rem;
                line-height: 1.2;
                margin: 0;
            ">Paket</p>
        </div>
    </section>
    """,
    )

with grid4:
    today = datetime.combine(datetime.today(), datetime.min.time())
    visitor_counter = len(list(get_visitor_today()))
    suspicious_counter = len(
        list(
            saved_detections.find(
                {
                    "timestamp": {
                        "$gte": today,
                        "$lte": today + timedelta(days=1),
                    },
                    "tags": "suspicious",
                }
            )
        )
    )
    st.html(
        f"""
        <section style="
            background-color: #152022;
            border-radius: 16px;
            padding-x: 2.3rem;
            padding-bottom: 3.2rem;
            padding-top: 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 1rem;
        ">
            <h4 
            style="
                # align-self: flex-start;
            ">Deteksi Hari ini</h4>
            <div style="
                display: flex;
                justify-content: center;
                flex-direction: row;
                align-items: center;
                text-align: center;
                gap: 1rem;
                width: 100%;
            ">
                <div>
                    <p style="
                        color: #3a7f8a;
                        font-size: 2.5rem;
                        font-weight: 600;
                        line-height: 1;
                        margin: 0;
                    ">{suspicious_counter}</p>
                    <p style="
                        font-size: 0.75rem;
                        letter-spacing: 0.1em;
                        margin: 0;
                    ">SUSPICIOUS</p>
                </div>
                <div>
                    <p style="
                        color: #3a7f8a;
                        font-size: 2.5rem;
                        font-weight: 600;
                        line-height: 1;
                        margin: 0;
                    ">{visitor_counter}</p>
                    <p style="
                        font-size: 0.75rem;
                        letter-spacing: 0.1em;
                        margin: 0;
                    ">VISITORS</p>
                </div>
            </div>
        </section>
    """
    )


with grid5:
    now = datetime.now()
    last_suspicious_activity = humanize.naturaltime(
        now
        - saved_detections.find_one({"tags": "suspicious"}, sort=[("timestamp", -1)])[
            "timestamp"
        ]
    )
    last_package = humanize.naturaltime(
        now - saved_detections.find_one({"tags": "package"})["timestamp"]
    )
    last_visitor = humanize.naturaltime(
        now
        - saved_detections.find_one({"tags": "visitor"}, sort=[("timestamp", -1)])[
            "timestamp"
        ]
    )
    st.html(
        f"""
        <div class="card">
            <h4>Riwayat Deteksi</h4>
            <ul style="list-style: none;">
                <li>🟠 Aktivitas Mencurigakan ({last_suspicious_activity})</li>
                <li>🟢 Paket ({last_package})</li>
                <li>🟢 Tamu ({last_visitor})</li>
            </ul>
        </div>
        """
    )

# ====

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Live Camera Feed")
with col2:
    ip_cam = st.text_input("Camera IP Address", "192.168.0.104")
    ip_cam_url = f"http://{ip_cam}:8000/video_feed"
try:
    response = req.get(ip_cam_url, stream=True, timeout=5)
    if response.status_code == 200:
        st.html(
            f"""
            <div style="text-align:center;">
                <img src="{ip_cam_url}" width="640" height="480" />
            </div>
            """
        )
    else:
        st.error("Camera is offline")
except req.exceptions.RequestException:
    st.error("Camera is offline")

input_col1, input_col2 = st.columns(2)

date = input_col1.date_input("Filter Hari", max_value="today")
tag_translated = {
    "Semua": "all",
    "Senjata": "weapon",
    "Paket": "package",
    "Diam": "idle",
    "Perkelahian": "fight",
    "Hal Mencurigakan": "suspicious",
    "Tamu": "visitor",
    "Aman": "safe",
    "Mondar mandir": "loitering",
}
tag = input_col2.selectbox("Filter Image Tag", list(tag_translated.keys()))

filter_date = datetime.fromisoformat(date.isoformat())

with st.expander("Visitor Detected"):
    col1, col2, col3, col4 = st.columns(4)
    count = 0
    visitors = saved_detections.find(
        {
            "timestamp": {
                "$gte": filter_date,
                "$lte": filter_date + timedelta(days=1),
            },
            "tags": "visitor",
        }
    ).sort("timestamp", -1)
    for visitor in visitors:
        image_stream = BytesIO(visitor["image_bin"])
        if count % 4 == 0:
            col1.image(image_stream, caption=visitor["name"])
        elif count % 4 == 1:
            col2.image(image_stream, caption=visitor["name"])
        elif count % 4 == 2:
            col3.image(image_stream, caption=visitor["name"])
        elif count % 4 == 3:
            col4.image(image_stream, caption=visitor["name"])
        count += 1
    if count == 0:
        st.text("No visitor found")

if tag != "Semua":
    filtered_images = (
        saved_detections.find(
            {
                "timestamp": {
                    "$gte": filter_date,
                    "$lte": filter_date + timedelta(days=1),
                },
                "tags": tag_translated[tag],
            }
        )
        .limit(50)
        .sort("timestamp", -1)
    )
else:
    filtered_images = (
        saved_detections.find(
            {
                "timestamp": {
                    "$gte": filter_date,
                    "$lte": filter_date + timedelta(days=1),
                }
            }
        )
        .limit(50)
        .sort("timestamp", -1)
    )

col1, col2, col3, col4 = st.columns(4)

count = 0
for image in filtered_images:
    image_stream = BytesIO(image["image_bin"])

    if count % 4 == 0:
        col1.image(image_stream, caption=image["timestamp"].strftime("%H:%M"))
    elif count % 4 == 1:
        col2.image(image_stream, caption=image["timestamp"].strftime("%H:%M"))
    elif count % 4 == 2:
        col3.image(image_stream, caption=image["timestamp"].strftime("%H:%M"))
    elif count % 4 == 3:
        col4.image(image_stream, caption=image["timestamp"].strftime("%H:%M"))
    count += 1

if not filtered_images:
    st.text("No image found")

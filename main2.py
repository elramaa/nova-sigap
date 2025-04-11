import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict, deque

st.title("🚶‍♂️ Suspicious Behavior Detection: Pacing Detector")
stframe = st.empty()

model = YOLO("yolov8n-pose.pt")  # model pose + track

# Untuk menyimpan history posisi X setiap track ID
track_history = defaultdict(lambda: deque(maxlen=30))

def is_pacing(track_id):
    x_positions = track_history[track_id]
    if len(x_positions) < 10:
        return False
    movement = max(x_positions) - min(x_positions)
    return movement > 100  # threshold bisa kamu atur

# Gunakan webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True, conf=0.5)

    annotated_frame = results[0].plot()

    # Ambil tracking dan pose info
    if results[0].boxes.id is not None:
        track_ids = results[0].boxes.id.int().cpu().numpy()
        keypoints = results[0].keypoints.xy.cpu().numpy()

        for idx, track_id in enumerate(track_ids):
            if idx >= len(keypoints): continue
            x_coords = keypoints[idx][:, 0]
            center_x = np.mean(x_coords)
            track_history[track_id].append(center_x)

            if is_pacing(track_id):
                cv2.putText(annotated_frame, "🚨 Pacing Detected", (50, 50 + idx * 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Tampilkan ke Streamlit
    stframe.image(annotated_frame, channels="BGR")

cap.release()

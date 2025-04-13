# main.py
import streamlit as st
import cv2
from ultralytics import YOLO
import numpy as np
from detection import *

from mqtt import connect_mqtt, MQTT

client = connect_mqtt()

def send_notif_to_buzzer(msg):
    client.publish(MQTT['topic'], msg)

# Load model
# box_model = YOLO("model1.pt")
# crime_model = YOLO("crime_model.pt")
# weapon_model = YOLO("weapon_model.pt")
pose_model = YOLO("yolo11n-pose.pt")
obj_model = YOLO("models/obj_model.pt")

# ESP32-CAM stream URL
ESP32_STREAM_URL = "http://192.168.204.161:81/stream"

def detected_items(model, results):
    names = set()
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls)
            name = model.names[cls_id]
            names.add(name)
    return names

# Streamlit UI
st.title("🏠 Housing Security System")
frame_placeholder = st.empty()

# Stream processing
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        st.warning("No video from Webcam")
        break

    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)
    
    pose_results = pose_model(frame, conf=0.4)
    annotated = pose_results[0].plot()

    object_results = obj_model(annotated, conf=0.6)
    annotated = object_results[0].plot()

    detected = detected_items(obj_model, object_results)
    print(detected)

    if 'package' in detected:
        send_notif_to_buzzer("paket")

    frame_placeholder.image(annotated, channels="BGR")
    cv2.imshow("Live Detection", annotated)

    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
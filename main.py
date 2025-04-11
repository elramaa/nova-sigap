# main.py
import streamlit as st
import cv2
from ultralytics import YOLO
import numpy as np

# Load model
model = YOLO("yolov8n-pose.pt")

# ESP32-CAM stream URL
ESP32_STREAM_URL = "http://192.168.204.161:81/stream"

# Streamlit UI
st.title("🏠 Housing Security System")
frame_placeholder = st.empty()

# Detection logic
def is_crouching(keypoints):
    try:
        # Key joints
        left_hip = keypoints[11]
        right_hip = keypoints[12]
        left_knee = keypoints[13]
        right_knee = keypoints[14]
        left_ankle = keypoints[15]
        right_ankle = keypoints[16]

        # Average y-positions
        hip_y = (left_hip[1] + right_hip[1]) / 2
        knee_y = (left_knee[1] + right_knee[1]) / 2
        ankle_y = (left_ankle[1] + right_ankle[1]) / 2

        # Estimated leg length
        leg_length = ankle_y - hip_y

        # Crouching: hips are lower (closer) to knees than normal
        crouch_ratio = (knee_y - hip_y) / leg_length

        return crouch_ratio < 0.4  # Adjust threshold as needed
    except:
        return False


def is_fighting_pose(keypoints):
    try:
        # Extract important joints
        left_wrist = keypoints[9]
        right_wrist = keypoints[10]
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]
        left_hip = keypoints[11]
        right_hip = keypoints[12]
        mid_hip_y = (left_hip[1] + right_hip[1]) / 2

        # Rule: Wrists are high & close to head → possibly guarding
        raised_hands = (left_wrist[1] < mid_hip_y) and (right_wrist[1] < mid_hip_y)

        # Rule: Shoulder width wide → aggressive stance
        shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
        hand_distance = abs(left_wrist[0] - right_wrist[0])
        hands_apart = hand_distance > (0.8 * shoulder_width)

        return raised_hands and hands_apart
    except:
        return False



# Stream processing
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        st.warning("No video from ESP32-CAM")
        break

    frame = cv2.resize(frame, (640, 480))
    results = model(frame)
    annotated = results[0].plot()

    for person in results[0].keypoints.data:
        keypoints = person.cpu().numpy().reshape(-1, 3)
        if is_crouching(keypoints):
            cv2.putText(annotated, "SUSPICIOUS: Crouching!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if is_fighting_pose(keypoints):
            cv2.putText(annotated, "SUSPICIOUS: Fighting Stance!", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


    frame_placeholder.image(annotated, channels="BGR")


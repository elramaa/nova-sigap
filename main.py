import cv2
from ultralytics import YOLO
import supervision as sv
import numpy as np
from detection import *
import time
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from bson import Binary
from mqtt import connect_mqtt, MQTT
from utils import *
from datetime import datetime

load_dotenv()

mongo = MongoClient(os.getenv("MONGODB_URL"), server_api=ServerApi('1'))
db = mongo['db']
sus_images_collection = db['sus_images']

client = connect_mqtt()

def send_notif_to_buzzer(msg):
    client.publish(MQTT['topic'], msg)

# Load model
yolo_model = YOLO("yolo11n.pt")
obj_model = YOLO("models/obj_model.pt")

def detected_items(model, results):
    names = set()
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls)
            name = model.names[cls_id]
            names.add(name)
    return names

def save_detections(tag, frame):
    filename = "results/result.jpg"
    frame_save = cv2.resize(frame, (640, 480))
    cv2.imwrite(filename, frame_save)
    with open(filename, 'rb') as image:
        bin_image = Binary(image.read())
    data = {
        'tag': tag,
        'timestamp': datetime.now(),
        'image_bin': bin_image,
    }
    sus_images_collection.insert_one(data)

# Stream processing
cap = cv2.VideoCapture(1)

# Parameter loitering
LOITER_THRESHOLD = 5  # dalam detik
POSITION_TOLERANCE = 100  # piksel

# Data tracking
loiter_data = {}   # track_id -> (last_position, start_time)
loiter_flags = {}  # track_id -> True/False (pernah loitering)

track_history = {}

box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

last_save_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        st.warning("No video from Webcam")
        break

    frame = cv2.resize(frame, (320, 240))
    frame = cv2.flip(frame, 1)
    
    yolo_results = yolo_model.track(frame, conf=0.4, classes=[0])[0]
    yolo_detections = sv.Detections.from_ultralytics(yolo_results)
    object_results = obj_model(frame, conf=0.6)[0]
    object_detections = sv.Detections.from_ultralytics(object_results)

    annotated = box_annotator.annotate(scene=frame, detections=yolo_detections)
    annotated = label_annotator.annotate(scene=annotated, detections=yolo_detections)
    annotated = box_annotator.annotate(scene=annotated, detections=object_detections)
    annotated = label_annotator.annotate(scene=annotated, detections=object_detections)

    annotated = cv2.resize(annotated, (640, 480))

    detected = detected_items(obj_model, object_results) | detected_items(yolo_model, yolo_results)
    print(detected)

    for result in yolo_results.boxes:
        # Ambil koordinat kotak
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        center = ((x1 + x2) // 2, (y1 + y2) // 2)

        # ID tracking manual (hash dari bounding box)
        track_id = hash((x1, y1, x2, y2)) % 10000

        # Jika sudah pernah loitering, tampilkan peringatan permanen
        if loiter_flags.get(track_id, False):
            cv2.putText(annotated, "LOITERING DETECTED!", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            send_notif_to_buzzer("bahaya")
            save_detections('loitering', annotated)
        else:
            # Cek posisi dan waktu
            if track_id in loiter_data:
                old_center, start_time = loiter_data[track_id]
                dx = abs(center[0] - old_center[0])
                dy = abs(center[1] - old_center[1])

                if dx < POSITION_TOLERANCE and dy < POSITION_TOLERANCE:
                    elapsed = time.time() - start_time
                    if elapsed > LOITER_THRESHOLD:
                        loiter_flags[track_id] = True  # Deteksi permanen
                else:
                    loiter_data[track_id] = (center, time.time())
            else:
                loiter_data[track_id] = (center, time.time())


    current_time = time.time()
    if current_time - last_save_time >= 5: # save every 5 seconds to not spam
        last_save_time = current_time
        if 'package' in detected:
            send_notif_to_buzzer("paket")
            save_detections('package', annotated)
        if 'fight' in detected:
            send_notif_to_buzzer("bahaya")
            save_detections('fight', annotated)
    cv2.imshow("Live Detection", annotated)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
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
from ubidots import *
from datetime import datetime
import face_recognition

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
cap = cv2.VideoCapture(0)

faces = {}

# Load images
for image in os.listdir('known_faces'):
    name = image.split('.')[0].title()
    loaded_image = face_recognition.load_image_file(f"known_faces/{image}")
    face_encoding = face_recognition.face_encodings(loaded_image)[0]
    faces[name] = face_encoding

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
    
# Parameter idle
IDLE_THRESHOLD = 5  # dalam detik
POSITION_TOLERANCE = 100  # piksel

# Data tracking
idle_data = {}   # track_id -> (last_position, start_time)
idle_flags = {}  # track_id -> True/False 

track_history = {}

box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

last_save_time = time.time()

notified_package_ids = set()

send_to_ubidots('camera_status', {
    'value': 1,
    'context': {
        'status': 'Aktif'
    }
})
print('KAMERA AKTIF')

while True:
    ret, frame = cap.read()
    if not ret:
        print("No video from Webcam")
        break

    frame = cv2.resize(frame, (320, 240))
    frame = cv2.flip(frame, 1)
    
    yolo_results = yolo_model.track(frame, conf=0.4, classes=[0])[0]
    yolo_detections = sv.Detections.from_ultralytics(yolo_results)
    object_results = obj_model.track(frame, conf=0.6)[0]
    object_detections = sv.Detections.from_ultralytics(object_results)

    annotated = box_annotator.annotate(scene=frame, detections=yolo_detections)
    annotated = label_annotator.annotate(scene=annotated, detections=yolo_detections)
    annotated = box_annotator.annotate(scene=annotated, detections=object_detections)
    annotated = label_annotator.annotate(scene=annotated, detections=object_detections)

    annotated = cv2.resize(annotated, (640, 480))

    detected = detected_items(obj_model, object_results) | detected_items(yolo_model, yolo_results)
    print(detected)

    

    # current_time = time.time()
    # if current_time - last_save_time >= 5: # save every 5 seconds to not spam
    #     last_save_time = current_time
    #     if 'package' in detected:
    #         send_notif_to_buzzer("paket")
    #         save_detections('package', annotated)
    #     if 'fight' in detected:
    #         send_notif_to_buzzer("bahaya")
    #         save_detections('fight', annotated)

    frame = annotated

    rgb_frame = frame[:, :, ::-1]  # BGR → RGB

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(list(faces.values()), face_encoding, tolerance=0.5)
        name = "unknown"

        if True in matches:
            matched_idx = matches.index(True)
            name = list(faces.keys())[matched_idx]

        if name == "unknown":
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        else:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)            
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    for result in yolo_results.boxes:
        # Ambil koordinat kotak
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        center = ((x1 + x2) // 2, (y1 + y2) // 2)

        # ID tracking manual (hash dari bounding box)
        track_id = hash((x1, y1, x2, y2)) % 10000

        # Jika sudah pernah idle, tampilkan peringatan permanen
        if idle_flags.get(track_id, False):
            cv2.putText(annotated, "IDLE DETECTED!", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            current_time = time.time()
            if current_time - last_save_time >= 10:
                last_save_time = current_time
                send_notif_to_buzzer("bahaya")
                save_detections('idle', annotated)
        else:
            # Cek posisi dan waktu
            if track_id in idle_data:
                old_center, start_time = idle_data[track_id]
                dx = abs(center[0] - old_center[0])
                dy = abs(center[1] - old_center[1])

                if dx < POSITION_TOLERANCE and dy < POSITION_TOLERANCE:
                    elapsed = time.time() - start_time
                    if elapsed > IDLE_THRESHOLD:
                        idle_flags[track_id] = True  # Deteksi permanen
                else:
                    idle_data[track_id] = (center, time.time())
            else:
                idle_data[track_id] = (center, time.time())

    for box in object_results.boxes:
        cls_id = int(box.cls[0])
        class_name = obj_model.names[cls_id]

        if class_name == 'package':
            track_id = int(box.id.item()) if box.id is not None else hash(tuple(map(int, box.xyxy[0]))) % 10000

            if track_id not in notified_package_ids:
                notified_package_ids.add(track_id)
                send_notif_to_buzzer("paket")
                save_detections('package', annotated)

        elif class_name == 'fight':
            current_time = time.time()
            if current_time - last_save_time >= 10:
                last_save_time = current_time
                send_notif_to_buzzer("bahaya")
                save_detections('fight', annotated)

    cv2.imshow("Live Detection", annotated)

    if cv2.waitKey(1) == ord('q'):
        break

print('KAMERA MATI')
send_to_ubidots('camera_status', {
    'value': 1,
    'context': {
        'status': 'Nonaktif'
    }
})

cap.release()
cv2.destroyAllWindows()
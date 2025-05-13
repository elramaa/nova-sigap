from flask import Flask, Response
import cv2
import threading
import time
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
from datetime import datetime, timedelta
from collections import defaultdict
import face_recognition

load_dotenv()

app = Flask(__name__)
cap = cv2.VideoCapture(2)  # or your IP camera URL

frame_lock = threading.Lock()
latest_frame = None
original_frame = None
latest_detection = None

mongo = MongoClient(os.getenv("MONGODB_URL"), server_api=ServerApi("1"))
db = mongo["db"]
saved_detections = db["saved_detections"]

client = connect_mqtt()


def send_notif_to_buzzer(msg):
    client.publish(MQTT["topic"], msg)


# Load model
yolo_model = YOLO("yolo11n.pt")  # deteksi person
obj_model = YOLO("models/obj_model.pt")  # deteksi paket, pisau, dan perkelahian


def detected_items(model, results):
    names = set()
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls)
            name = model.names[cls_id]
            names.add(name)
    return names


def save_image(frame):
    filename = "results/result.jpg"
    frame_save = cv2.resize(frame, (640, 480))
    cv2.imwrite(filename, frame_save)
    with open(filename, "rb") as image:
        bin_image = Binary(image.read())
    return bin_image


def save_detections(tags, frame):
    data = {
        "tags": tags,
        "timestamp": datetime.now(),
        "image_bin": save_image(frame),
    }
    saved_detections.insert_one(data)


def check_visitors():
    today = datetime.combine(datetime.today(), datetime.min.time())
    visitors = db["saved_detections"].find(
        {
            "tags": "visitor",
            "timestamp": {"$gte": today, "$lte": today + timedelta(days=1)},
        }
    )
    return [visitor["name"] for visitor in visitors]


def adjust_gamma(frame, gamma=1.5):
    invGamma = 1.0 / gamma
    table = [((i / 255.0) ** invGamma) * 255 for i in range(256)]
    table = np.array(table, dtype="uint8")
    return cv2.LUT(frame, table)


def detection_thread():
    global latest_frame, original_frame, latest_detection

    faces = {}
    # Load images
    for image in os.listdir("known_faces"):
        name = image.split(".")[0].title()
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
    idle_data = {}  # track_id -> (last_position, start_time)
    idle_flags = {}  # track_id -> True/False

    id_entry_time = dict()
    presence_duration = defaultdict(float)  # track_id => detik

    FPS = cap.get(cv2.CAP_PROP_FPS)
    max_allowed_duration = 30  # dalam detik = 3 menit

    track_history = {}

    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    # last_save_time = time.time()
    last_save_times = {
        key: time.time() for key in ["package", "weapon", "fight", "idle", "loitering"]
    }

    item_ids = {name: set() for name in ["package", "knife", "fight"]}

    db["config"].update_one({"_id": "config"}, {"$set": {"camera_status": True}})
    print("KAMERA AKTIF")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 480))
        frame = cv2.flip(frame, 1)

        # Membenarkan backlight supaya tidak terlalu terang
        lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab_frame)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        lframe = cv2.merge((cl, a, b))
        frame = cv2.cvtColor(lframe, cv2.COLOR_LAB2BGR)

        # frame = adjust_gamma(frame, 1.5)

        original_frame = frame.copy()
        original_frame = cv2.resize(original_frame, (640, 480))

        yolo_results = yolo_model.track(frame, conf=0.4, classes=[0])[0]
        yolo_detections = sv.Detections.from_ultralytics(yolo_results)
        object_results = obj_model.track(frame, conf=0.6)[0]
        object_detections = sv.Detections.from_ultralytics(object_results)

        annotated = box_annotator.annotate(scene=frame, detections=yolo_detections)
        annotated = label_annotator.annotate(
            scene=annotated, detections=yolo_detections
        )
        annotated = box_annotator.annotate(
            scene=annotated, detections=object_detections
        )
        annotated = label_annotator.annotate(
            scene=annotated, detections=object_detections
        )

        annotated = cv2.resize(annotated, (640, 480))

        detected = detected_items(obj_model, object_results) | detected_items(
            yolo_model, yolo_results
        )
        print(detected)

        # PENGENALAN WAJAH
        # rgb_frame = frame[:, :, ::-1]  # BGR → RGB
        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(bgr_frame)
        face_encodings = face_recognition.face_encodings(bgr_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(
            face_locations, face_encodings
        ):
            matches = face_recognition.compare_faces(
                list(faces.values()), face_encoding, tolerance=0.5
            )
            name = "unknown"

            if True in matches:
                matched_idx = matches.index(True)
                name = list(faces.keys())[matched_idx]
                print("face detected")

            if name == "unknown":
                cv2.rectangle(annotated, (left, top), (right, bottom), (0, 0, 255), 2)
            else:
                cv2.rectangle(annotated, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
            )

            if name != "unknown" and name not in check_visitors():
                db["saved_detections"].insert_one(
                    {
                        "name": name,
                        "timestamp": datetime.now(),
                        "image_bin": save_image(annotated),
                        "tags": ["safe", "visitor"],
                    }
                )

        # Pendeteksian orang yang sama dalam jangkauan kamera
        current_ids = set()

        if len(yolo_results) != 0:
            if yolo_results[0].boxes.id is not None:
                boxes = yolo_results[0].boxes
                for box, track_id in zip(
                    boxes.xyxy.cpu().numpy(), boxes.id.int().cpu().numpy()
                ):
                    current_ids.add(track_id)

                    x1, y1, x2, y2 = map(int, box[:4])

                    # Catat waktu pertama kali orang ini muncul
                    if track_id not in id_entry_time:
                        id_entry_time[track_id] = time.time()

                    # Hitung durasi kehadiran
                    elapsed_time = time.time() - id_entry_time[track_id]
                    presence_duration[track_id] = elapsed_time

                    label = f"ID {track_id}"

                    # Tandai jika terlalu lama
                    if elapsed_time > max_allowed_duration:
                        label += " | Lama disini"
                        color = (0, 0, 255)
                    else:
                        color = (0, 255, 0)

                    # Gambar kotak & label
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(
                        annotated,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2,
                    )

                    current_time = time.time()
                    if current_time - last_save_times["loitering"] >= 10:
                        last_save_times["loitering"] = current_time
                        send_notif_to_buzzer("bahaya")
                        save_detections(["suspicious", "loitering"], annotated)

        # Bersihkan ID yang sudah hilang dari frame
        all_tracked_ids = set(id_entry_time.keys())
        for old_id in all_tracked_ids - current_ids:
            if time.time() - id_entry_time[old_id] > 2:  # toleransi delay
                del id_entry_time[old_id]
                del presence_duration[old_id]

        # Track apabila ada orang yang diam
        for result in yolo_results.boxes:
            # Ambil koordinat kotak
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            center = ((x1 + x2) // 2, (y1 + y2) // 2)

            # ID tracking manual (hash dari bounding box)
            track_id = hash((x1, y1, x2, y2)) % 10000

            # Jika sudah pernah idle, tampilkan peringatan permanen
            if idle_flags.get(track_id, False):
                cv2.putText(
                    annotated,
                    "IDLE DETECTED!",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )
                current_time = time.time()
                if current_time - last_save_times["idle"] >= 10:
                    last_save_times["idle"] = current_time
                    send_notif_to_buzzer("bahaya")
                    save_detections(["suspicious", "idle"], annotated)
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
            track_id = (
                int(box.id.item())
                if box.id is not None
                else hash(tuple(map(int, box.xyxy[0]))) % 10000
            )

            if class_name == "package":
                if track_id not in item_ids["package"]:
                    item_ids["package"].add(track_id)
                    # send_to_ubidots("jumlah_paket", {"value": 1})
                    send_notif_to_buzzer("paket")
                    save_detections(["safe", "package"], annotated)

            if class_name == "fight":
                if track_id not in item_ids["fight"]:
                    item_ids["fight"].add(track_id)
                current_time = time.time()
                if current_time - last_save_times["fight"] >= 10:
                    last_save_times["fight"] = current_time
                    send_notif_to_buzzer("bahaya")
                    save_detections(["suspicious", "fight"], annotated)

            if class_name == "knife":
                if track_id not in item_ids["knife"]:
                    item_ids["knife"].add(track_id)
                current_time = time.time()
                if current_time - last_save_times["weapon"] >= 10:
                    last_save_times["weapon"] = current_time
                    send_notif_to_buzzer("bahaya")
                    save_detections(["suspicious", "weapon"], annotated)

        with frame_lock:
            latest_frame = annotated.copy()

        # Show in local window
        cv2.imshow("Live Detection", annotated)
        if cv2.waitKey(1) == ord("q"):
            break

        time.sleep(0.01)  # tweak to balance CPU usage

    print("KAMERA MATI")
    db["config"].update_one({"_id": "config"}, {"$set": {"camera_status": False}})

    cap.release()
    cv2.destroyAllWindows()
    raise SystemExit("Camera Off: Program Terminated. Please restart the program.")


# Start detection thread
threading.Thread(target=detection_thread, daemon=True).start()


def generate_stream():
    global original_frame
    while True:
        with frame_lock:
            if original_frame is None:
                continue
            _, buffer = cv2.imencode(".jpg", original_frame)
            frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/")
def index():
    return "Streaming. Go to /video_feed to view stream."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

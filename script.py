import cv2
import time
from ultralytics import YOLO

# Load YOLOv8 (pakai model kecil agar ringan)
model = YOLO("yolov8n.pt")

# Inisialisasi kamera
cap = cv2.VideoCapture(0)

# Parameter loitering
LOITER_THRESHOLD = 5  # dalam detik
POSITION_TOLERANCE = 100  # piksel

# Data tracking
loiter_data = {}   # track_id -> (last_position, start_time)
loiter_flags = {}  # track_id -> True/False (pernah loitering)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Deteksi orang dengan YOLO
    results = model(frame)[0]

    for result in results.boxes:
        cls_id = int(result.cls[0])
        if model.names[cls_id] != 'person':
            continue  # hanya deteksi manusia

        # Ambil koordinat kotak
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        center = ((x1 + x2) // 2, (y1 + y2) // 2)

        # ID tracking manual (hash dari bounding box)
        track_id = hash((x1, y1, x2, y2)) % 10000

        filename = f"captures/loitering_{track_id}_{int(time.time())}.jpg"

        # Jika sudah pernah loitering, tampilkan peringatan permanen
        if loiter_flags.get(track_id, False):
            cv2.putText(frame, "LOITERING DETECTED!", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.imwrite(filename, frame)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
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

            # Gambar kotak normal (belum loitering)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Tampilkan hasil
    cv2.imshow("Loitering Detection with YOLOv8", frame)

    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan
cap.release()
cv2.destroyAllWindows()

import face_recognition
import cv2
import numpy as np

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
ato_image = face_recognition.load_image_file("ato.jpg")
ato_face_encoding = face_recognition.face_encodings(ato_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    ato_face_encoding,
]
known_face_names = [
    "Ato",
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    ret, frame = video_capture.read()
    rgb_frame = frame[:, :, ::-1]  # BGR → RGB

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        name = "Tidak dikenal"

        if True in matches:
            matched_idx = matches.index(True)
            name = known_face_names[matched_idx]

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()